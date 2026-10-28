"""Extrai eventos dos logs das urnas (arquivos *-log.jez) para parquet.

Uso:
    python -I scripts/03_logs.py dados/brutos/arqurna/2026_2t_SP.zip [...]   # arquivos específicos
    python -I scripts/03_logs.py --todos                                      # tudo que já foi baixado

Para cada arquivo UF/turno gera, em dados/processados/logs/:
  eleitores_{ano}_{turno}_{UF}.parquet  -> 1 linha por voto computado
      sec   : índice da seção (junta com a tabela de seções)
      ts    : segundos desde 00:00 (hora LOCAL da urna) do dia da eleição
      bio   : 1 = biometria; 0 = manual após falha da digital (dado pessoal/mesário);
              2 = sem biometria cadastrada (só ano de nascimento); -1 = indeterminado
      mesa  : 1 se o log registrou "Mesário N habilitou o eleitor" (subconjunto de bio=0)
      dur   : segundos entre "Eleitor foi habilitado" e "O voto do eleitor foi computado"
  secoes_{ano}_{turno}_{UF}.parquet     -> 1 linha por seção (aberturas, encerramento, contadores)

O relógio da urna está em hora local; a conversão para o horário de Brasília é feita na análise.
Logs de urnas substituídas (contingência) vêm aninhados dentro do .jez e são somados.
"""
import argparse
import io
import re
import sys
import zipfile
from datetime import date, timedelta
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados" / "brutos" / "arqurna"
SAIDA = RAIZ / "dados" / "processados" / "logs"

DATAS = {("2026", "1t"): date(2026, 10, 4), ("2026", "2t"): date(2026, 10, 25),
         ("2022", "1t"): date(2022, 10, 2), ("2022", "2t"): date(2022, 10, 30)}

# 2026: o03220ac0101500020088-log.jez   2022: o00406-0111200060046.logjez
RE_NOME = re.compile(r"(\d{5})(\d{4})(\d{4})(?:-log\.jez|\.logjez)$")


def b(s):
    return s.encode("latin-1")


# Mensagens exatas (campo 5 do log) -> código
M_AGUARDA = 1
M_BIO = 2
M_MANUAL = 3
M_HABILITADO = 4
M_COMPUTADO = 5
M_PRONTA = 6
M_ENCERRAR = 7
M_SUSPENSA = 8
M_SUSP_ELEITOR = 9
M_PARCIAL = 10
M_SEM_VOTO = 11
M_JA_VOTOU = 12
M_JUSTIF = 13
M_PRESENTES_NAO = 14
M_CONTING = 15
M_REINICIO = 16
M_NAO_ENCONTRADO = 17
M_CANCEL_BIO = 18
M_ANO = 19
M_INICIO_ENC = 20
EXATAS = {
    b("Aguardando digitação do identificador do eleitor"): M_AGUARDA,
    b("Tipo de habilitação do eleitor [biométrica]"): M_BIO,
    b("Solicitação de dado pessoal do eleitor para habilitação manual"): M_MANUAL,
    b("Eleitor foi habilitado"): M_HABILITADO,
    b("O voto do eleitor foi computado"): M_COMPUTADO,
    b("Urna pronta para receber votos"): M_PRONTA,
    b("Operador selecionou: Encerrar votação"): M_ENCERRAR,
    b("Inicio do Encerramento"): M_INICIO_ENC,  # existe em 2022 e 2026
    b("Votação suspensa"): M_SUSPENSA,
    b("Eleitor foi suspenso pelo mesário"): M_SUSP_ELEITOR,
    b("Eleitor votou parcialmente e em seguida foi suspenso"): M_PARCIAL,
    b("Eleitor foi suspenso e não confirmou nenhum voto"): M_SEM_VOTO,
    b("O eleitor identificado já votou"): M_JA_VOTOU,
    b("Justificativa recebida"): M_JUSTIF,
    b("Todas as pessoas presentes já votaram? NÃO"): M_PRESENTES_NAO,
    b("Modo de carga da UE - Urna de contingência"): M_CONTING,
    b("Mesário confirmou o reinício da votação"): M_REINICIO,
    b("Eleitor não encontrado para o identificador informado"): M_NAO_ENCONTRADO,
    b("Habilitação cancelada durante reconhecimento biométrico"): M_CANCEL_BIO,
    b("Ano de nascimento digitado é igual ao do cadastro"): M_ANO,
    b("O eleitor não possui biometria"): M_ANO,  # mensagem equivalente em 2022
}
P_MESARIO_HAB = re.compile(rb"^Mes\xe1rio \d+ habilitou o eleitor$")
P_DEMO = b("Início do modo de demonstração")
P_INICIO_APP = b("Iniciando aplicação")

CONTADORES = ["n_suspensa", "n_susp_eleitor", "n_parcial", "n_sem_voto", "n_ja_votou",
              "n_justif", "n_presentes_nao", "n_reinicio", "n_nao_encontrado", "n_cancel_bio",
              "n_erro"]
COD_CONT = {M_SUSPENSA: "n_suspensa", M_SUSP_ELEITOR: "n_susp_eleitor", M_PARCIAL: "n_parcial",
            M_SEM_VOTO: "n_sem_voto", M_JA_VOTOU: "n_ja_votou", M_JUSTIF: "n_justif",
            M_PRESENTES_NAO: "n_presentes_nao", M_REINICIO: "n_reinicio",
            M_NAO_ENCONTRADO: "n_nao_encontrado", M_CANCEL_BIO: "n_cancel_bio"}


def abre_jez(dados):
    """Devolve lista de (nome, bytes) de todos os logs de texto, recursivamente."""
    saida = []
    if dados[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            for nm in z.namelist():
                conteudo = z.read(nm)
                if nm.lower().endswith(".jez"):
                    saida.extend(abre_jez(conteudo))
                else:
                    saida.append((nm, conteudo))
    elif dados[:6] == b"7z\xbc\xaf\x27\x1c":
        import py7zr
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with py7zr.SevenZipFile(io.BytesIO(dados)) as z:
                z.extractall(tmp)
            for p in sorted(Path(tmp).rglob("*")):
                if p.is_file():
                    conteudo = p.read_bytes()
                    if p.suffix.lower() == ".jez":
                        saida.extend(abre_jez(conteudo))
                    else:
                        saida.append((p.name, conteudo))
    else:
        saida.append(("?", dados))
    return saida


def processa_secao(textos, dia):
    """textos: lista de bytes (um por arquivo de log). Retorna (resumo, eleitores)."""
    janela = {}
    for k in (-1, 0, 1):
        d = dia + timedelta(days=k)
        janela[b(d.strftime("%d/%m/%Y"))] = k * 86400

    # remove linhas duplicadas entre logs aninhados (cada linha tem hash próprio no fim)
    vistos = set()
    linhas = []
    for t in textos:
        for ln in t.split(b"\n"):
            ln = ln.rstrip(b"\r")
            if len(ln) < 25 or ln in vistos:
                continue
            vistos.add(ln)
            linhas.append(ln)
    # ordena por data/hora (logs de urnas diferentes intercalados); estável dentro de cada log
    def chave(ln):
        return (ln[6:10], ln[3:5], ln[0:2], ln[11:19])
    linhas.sort(key=chave)

    r = dict.fromkeys(CONTADORES, 0)
    r.update(n_arquivos=len(textos), contingencia=len(textos) > 1, t_pronta=None,
             t_pronta_ult=None, t_encerrar=None, n_habilitados=0, n_votos=0, n_bio=0,
             n_manual=0, n_mesario=0, n_sem_cadastro=0, n_indet=0)
    urnas = set()
    ts_l, bio_l, mesa_l, dur_l = [], [], [], []
    demo = False
    flag_bio = flag_man = flag_mesa = flag_ano = False
    t_hab = None
    for ln in linhas:
        off = janela.get(ln[0:10])
        p = ln.split(b"\t")
        if len(p) < 5:
            continue
        msg = p[4]
        if msg.startswith(P_INICIO_APP):
            demo = False
        elif msg.startswith(P_DEMO):
            demo = True
        if off is None or demo:
            continue
        try:
            ts = off + int(ln[11:13]) * 3600 + int(ln[14:16]) * 60 + int(ln[17:19])
        except ValueError:
            continue
        if p[1] == b"ERRO":
            r["n_erro"] += 1
        cod = EXATAS.get(msg)
        if cod is None:
            if P_MESARIO_HAB.match(msg):
                flag_mesa = True
            continue
        if cod == M_AGUARDA:
            flag_bio = flag_man = flag_mesa = flag_ano = False
        elif cod == M_BIO:
            flag_bio = True
        elif cod == M_MANUAL:
            flag_man = True
        elif cod == M_ANO:
            flag_ano = True
        elif cod == M_HABILITADO:
            r["n_habilitados"] += 1
            t_hab = ts
            hab_bio = 1 if flag_bio else 0 if (flag_man or flag_mesa) else 2 if flag_ano else -1
            hab_mesa = flag_mesa
        elif cod == M_COMPUTADO:
            r["n_votos"] += 1
            urnas.add(p[2])
            if t_hab is None:
                bio, mesa, dur = -1, False, -1
            else:
                bio, mesa, dur = hab_bio, hab_mesa, ts - t_hab
            ts_l.append(ts)
            bio_l.append(bio)
            mesa_l.append(mesa)
            dur_l.append(min(dur, 32000))
            if bio == 1:
                r["n_bio"] += 1
            elif bio == 0:
                r["n_manual"] += 1
                r["n_mesario"] += mesa
            elif bio == 2:
                r["n_sem_cadastro"] += 1
            else:
                r["n_indet"] += 1
            t_hab = None
            flag_bio = flag_man = flag_mesa = flag_ano = False
        elif cod == M_PRONTA:
            if r["t_pronta"] is None:
                r["t_pronta"] = ts
            r["t_pronta_ult"] = ts
        elif cod == M_ENCERRAR:
            r["t_encerrar"] = ts
        elif cod == M_INICIO_ENC:
            if r["t_encerrar"] is None or ts > r["t_encerrar"] + 600:
                r["t_encerrar"] = ts  # 2022 não registra "Encerrar votação"
        elif cod == M_CONTING:
            r["contingencia"] = True
        else:
            r[COD_CONT[cod]] += 1
    r["n_urnas"] = len(urnas)
    el = (np.array(ts_l, dtype=np.int32), np.array(bio_l, dtype=np.int8),
          np.array(mesa_l, dtype=np.int8), np.array(dur_l, dtype=np.int16))
    return r, el


_Z = None


def _trabalho(args):
    caminho, nomes, dia, uf = args
    global _Z
    if _Z is None or _Z.filename != str(caminho):
        _Z = zipfile.ZipFile(caminho)
    res = []
    for nome in nomes:
        m = RE_NOME.search(nome)
        mun, zona, secao = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            textos = [c for _, c in abre_jez(_Z.read(nome))]
            r, el = processa_secao(textos, dia)
            r["falha"] = None
        except Exception as e:
            r = dict(falha=f"{type(e).__name__}: {e}")
            el = None
        r.update(uf=uf, cd_municipio=mun, nr_zona=zona, nr_secao=secao, arquivo=nome)
        res.append((r, el))
    return res


def processa_arquivo(caminho, pool, forcar=False):
    m = re.match(r"(\d{4})_(\dt)_([A-Z]{2})\.zip$", caminho.name)
    ano, turno, uf = m.groups()
    out_s = SAIDA / f"secoes_{ano}_{turno}_{uf}.parquet"
    out_e = SAIDA / f"eleitores_{ano}_{turno}_{uf}.parquet"
    if out_s.exists() and out_e.exists() and not forcar:
        print(f"{caminho.name}: já processado", flush=True)
        return
    dia = DATAS[(ano, turno)]
    with zipfile.ZipFile(caminho) as z:
        nomes = [n for n in z.namelist() if RE_NOME.search(n)]
    lotes = [(caminho, nomes[i:i + 200], dia, uf) for i in range(0, len(nomes), 200)]
    secoes, partes = [], []
    for res in pool.imap_unordered(_trabalho, lotes):
        for r, el in res:
            idx = len(secoes)
            r["sec"] = idx
            secoes.append(r)
            if el is not None and len(el[0]):
                partes.append(pl.DataFrame({
                    "sec": np.full(len(el[0]), idx, dtype=np.int32),
                    "ts": el[0], "bio": el[1], "mesa": el[2], "dur": el[3]}))
    df_s = pl.DataFrame(secoes, infer_schema_length=None).with_columns(
        pl.lit(int(ano)).alias("ano"), pl.lit(int(turno[0])).alias("turno"))
    df_e = pl.concat(partes) if partes else pl.DataFrame(
        schema={"sec": pl.Int32, "ts": pl.Int32, "bio": pl.Int8, "mesa": pl.Int8, "dur": pl.Int16})
    SAIDA.mkdir(parents=True, exist_ok=True)
    df_e.write_parquet(out_e)
    df_s.write_parquet(out_s)
    falhas = df_s["falha"].drop_nulls().len() if "falha" in df_s.columns else 0
    print(f"{caminho.name}: {len(df_s)} seções, {len(df_e):,} votos, falhas={falhas}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="*")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--forcar", action="store_true")
    ap.add_argument("--procs", type=int, default=16)
    a = ap.parse_args()
    arqs = [Path(x) for x in a.arquivos]
    if a.todos:
        arqs = sorted(BRUTOS.glob("*.zip"), key=lambda p: p.stat().st_size)
    if not arqs:
        sys.exit("nenhum arquivo")
    with Pool(a.procs) as pool:
        for c in arqs:
            processa_arquivo(c, pool, a.forcar)


if __name__ == "__main__":
    main()
