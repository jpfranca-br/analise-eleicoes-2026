"""Servidor MCP para explorar os dados da análise das eleições presidenciais 2026 (e linha de base 2022).

Quem se conecta não precisa baixar nada: consultas SQL (DuckDB, somente leitura) rodam no servidor sobre os
parquets consolidados; o log bruto de qualquer urna é lido sob demanda dos arquivos originais do TSE.

Execução:
    python -I servidor_mcp/servidor.py                       # stdio (uso local, ex.: Claude Desktop / Claude Code)
    python -I servidor_mcp/servidor.py --http --porta 8000   # HTTP (streamable-http) em /mcp, para acesso remoto

Variáveis de ambiente:
    ELEICOES_RAIZ   pasta do projeto (padrão: pasta-mãe deste arquivo) — precisa ter dados/processados e saida
    MCP_TOKEN       se definido, exige "Authorization: Bearer <token>" no modo HTTP
    MCP_TIMEOUT_S   tempo máximo por consulta SQL (padrão 60 s)
"""
import argparse
import functools
import hmac
import html as htmllib
import io
import json
import os
import re
import threading
import zipfile
from pathlib import Path

import duckdb
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

RAIZ = Path(os.environ.get("ELEICOES_RAIZ", Path(__file__).resolve().parent.parent)).resolve()
PROC = RAIZ / "dados" / "processados"
LOGS = PROC / "logs"
SAIDA = RAIZ / "saida"
BRUTOS = RAIZ / "dados" / "brutos" / "arqurna"
TIMEOUT = float(os.environ.get("MCP_TIMEOUT_S", "60"))
MAX_LINHAS = 5000
SO_LEITURA = ToolAnnotations(readOnlyHint=True, openWorldHint=False)

# ----------------------------------------------------------------------------- catálogo de tabelas
def _p(path):
    return path.as_posix()


TABELAS = {}  # nome -> (sql da view, descrição)


def _registra(nome, sql, desc):
    TABELAS[nome] = (sql, desc)


for ano in (2026, 2022):
    _registra(f"resultados_{ano}", f"SELECT * FROM read_parquet('{_p(PROC)}/resultados_{ano}.parquet')",
              f"Resultado oficial por seção e turno (Presidente), {ano}. Chave: turno, uf, cd_municipio, nr_zona, nr_secao. "
              "Colunas v<NN> = votos do candidato NN (13 = Lula; 22 = Flávio Bolsonaro em 2026 / Jair Bolsonaro em 2022); "
              "aptos, comparecimento, abstencoes, brancos, nulos, nominais; local de votação; horário de recebimento do BU.")
    _registra(f"candidatos_{ano}", f"SELECT * FROM read_parquet('{_p(PROC)}/candidatos_{ano}.parquet')",
              f"Número, nome e total de votos dos candidatos a Presidente, {ano}.")
    _registra(f"indicadores_{ano}", f"SELECT * FROM read_parquet('{_p(PROC)}/indicadores_{ano}.parquet')",
              f"Uma linha por seção com 1º e 2º turno lado a lado (sufixos _1 e _2), {ano}: resultados, percentuais (p13, p22, "
              "p_abst, p_branco, p_nulo), e indicadores do log da urna em horário de Brasília (n_votos, n_pos17 = votos após 17h, "
              "taxa_dia, taxa_pos17, pct_manual = sem biometria após falha da digital, pct_semcad = sem biometria cadastrada, "
              "t_abre_b/t_encerra_b/t_ult_voto em segundos desde 0h, fuso_h, contingencia = urna substituída), e diferenças d_*.")
    _registra(f"escores_{ano}", f"SELECT * FROM read_parquet('{_p(SAIDA)}/escores_{ano}.parquet')",
              f"Resultado dos testes estatísticos por seção, {ano}: z_A_voto (desvio da votação no 2º turno; >0 pró-13, <0 pró-22), "
              "z_B_abst/z_B_branco/z_B_nulo, p_C_pos17 e flags de fluxo após 17h, z_D_manual_entre_turnos e flags de biometria, "
              "n_sinais e motivos. |z| >= 4 é considerado sinal forte.")
    _registra(f"secoes_sinalizadas_{ano}", f"SELECT * FROM read_csv('{_p(SAIDA)}/secoes_sinalizadas_{ano}.csv', delim=';', header=true)",
              f"Seções com pelo menos um sinal forte em {ano}, com motivos e indicadores principais.")
    _registra(f"curva_horaria_{ano}",
              f"SELECT *, regexp_extract(filename, 'curva_horaria_(\\d+)_(\\d)t', 2)::INT AS turno FROM "
              f"read_parquet('{_p(PROC)}/curva_horaria_{ano}_*t.parquet', filename=true)",
              f"Votos por bloco de 15 min (t15, segundos desde 0h, horário de Brasília), por UF e tipo de habilitação (bio), {ano}.")

_registra("secoes_log",
          f"SELECT * EXCLUDE (filename), regexp_extract(filename, 'secoes_(\\d+)_', 1)::INT AS ano, "
          f"regexp_extract(filename, '_(\\d)t_', 1)::INT AS turno FROM read_parquet('{_p(LOGS)}/secoes_*.parquet', filename=true, union_by_name=true)",
          "Resumo do log de cada urna (todas as UFs, 2022 e 2026, 1º e 2º turno). Chave: ano, turno, uf, cd_municipio, nr_zona, nr_secao; "
          "'sec' liga com a tabela eleitores. Horários em hora LOCAL da urna (segundos desde 0h): t_pronta, t_encerrar. "
          "Contagens: n_votos, n_bio, n_manual, n_mesario, n_sem_cadastro, n_suspensa, n_ja_votou, n_erro, contingencia, n_urnas.")
_registra("eleitores",
          f"SELECT * EXCLUDE (filename), regexp_extract(filename, 'eleitores_(\\d+)_', 1)::INT AS ano, "
          f"regexp_extract(filename, '_(\\d)t_', 1)::INT AS turno, regexp_extract(filename, '_([A-Z]{{2}})\\.parquet', 1) AS uf "
          f"FROM read_parquet('{_p(LOGS)}/eleitores_*.parquet', filename=true)",
          "Um registro por voto computado (~490 milhões de linhas). Junte com secoes_log por (ano, turno, uf, sec). "
          "ts = segundos desde 0h na hora LOCAL da urna; bio: 1 biometria, 0 manual após falha da digital, 2 sem biometria cadastrada, "
          "-1 indeterminado; mesa = 1 se o mesário habilitou; dur = segundos entre habilitação e voto computado. "
          "Para horário de Brasília use indicadores_<ano>.fuso_h_<turno> (tb = ts - fuso_h*3600). Filtre sempre por ano/turno/uf.")
for nome, arq, desc in [
    ("pos17_secoes", "pos17_secoes.csv", "Urnas que receberam votos entre 17h15 e 19h no 2º turno de 2026 (prorrogação), com perfil dos votos."),
    ("verificacao_individual_2026", "verificacao_individual_2026.csv", "Seções de 2026 que merecem conferência individual e o motivo."),
]:
    if (SAIDA / arq).exists():
        _registra(nome, f"SELECT * FROM read_csv('{_p(SAIDA)}/{arq}', delim=';', header=true)", desc)


@functools.lru_cache(maxsize=1)
def _base():
    con = duckdb.connect(":memory:")
    disponiveis = {}
    for nome, (sql, desc) in TABELAS.items():
        try:
            con.execute(f"CREATE VIEW {nome} AS {sql}")
            con.execute(f"SELECT * FROM {nome} LIMIT 0")
            disponiveis[nome] = desc
        except duckdb.Error:
            con.execute(f"DROP VIEW IF EXISTS {nome}")
    # trava o banco: só lê arquivos das pastas de dados, não escreve nem muda configuração
    dirs = ", ".join(f"'{_p(d)}/'" for d in (PROC, SAIDA))
    con.execute(f"SET allowed_directories=[{dirs}]")
    con.execute("SET enable_external_access=false")
    con.execute(f"SET threads={max(2, (os.cpu_count() or 4) // 2)}")
    con.execute("SET memory_limit='8GB'")
    con.execute("SET lock_configuration=true")
    return con, disponiveis


RE_LEITURA = re.compile(r"^\s*(SELECT|WITH|DESCRIBE|SUMMARIZE|SHOW|EXPLAIN|FROM|VALUES|PIVOT|UNPIVOT)\b", re.I | re.S)
RE_PROIBIDO = re.compile(r"\b(COPY|ATTACH|DETACH|INSTALL|LOAD|EXPORT|IMPORT|CREATE|INSERT|UPDATE|DELETE|DROP|ALTER|PRAGMA|SET|CALL|CHECKPOINT|VACUUM)\b", re.I)


def _executa(sql, limite):
    sql = sql.strip().rstrip(";").strip()
    sem_strings = re.sub(r"'(?:[^']|'')*'", "''", sql)
    if ";" in sem_strings:
        raise ValueError("Envie um único comando por vez.")
    if not RE_LEITURA.match(sql) or RE_PROIBIDO.search(sem_strings):
        raise ValueError("Apenas consultas de leitura (SELECT/WITH/DESCRIBE/SUMMARIZE/SHOW/EXPLAIN).")
    con, _ = _base()
    cur = con.cursor()
    timer = threading.Timer(TIMEOUT, cur.interrupt)
    timer.start()
    try:
        rel = cur.sql(sql)
        cols = rel.columns
        linhas = rel.limit(limite + 1).fetchall()
    except duckdb.InterruptException:
        raise ValueError(f"Consulta excedeu {TIMEOUT:.0f} s. Filtre por ano/turno/uf ou agregue antes.")
    finally:
        timer.cancel()
        cur.close()
    truncado = len(linhas) > limite
    return cols, linhas[:limite], truncado


def _tabela_texto(cols, linhas, truncado):
    def fmt(v):
        if v is None:
            return ""
        if isinstance(v, float):
            return f"{v:.6g}"
        return str(v).replace("\t", " ").replace("\n", " ")
    out = ["\t".join(cols)] + ["\t".join(fmt(v) for v in r) for r in linhas]
    if truncado:
        out.append(f"... (resultado truncado em {len(linhas)} linhas; use LIMIT/agregação ou aumente 'limite')")
    return "\n".join(out)


# ----------------------------------------------------------------------------- servidor
mcp = MCPServer(
    name="eleicoes-2026",
    title="Análise das eleições presidenciais 2026 — dados por seção e logs de urna",
    instructions=(
        "Dados oficiais do TSE da eleição presidencial de 2026 (1º e 2º turno; 2º turno Lula 13 × Flávio Bolsonaro 22) e de 2022 "
        "(linha de base), seção por seção, incluindo logs de todas as urnas. Comece por `visao_geral`, depois `listar_tabelas` e "
        "`descrever_tabela`. Use `consultar_sql` (DuckDB, somente leitura) para análises livres; `secao` e `linha_do_tempo_secao` "
        "para uma seção específica; `log_urna` para o log bruto; `ler_relatorio` para os relatórios. "
        "Lembre: um sinal estatístico é indício para verificação, não prova de fraude; compare sempre com 2022."),
    version="1.0",
)


@mcp.tool(annotations=SO_LEITURA)
def visao_geral() -> str:
    """Explica o projeto, a origem dos dados, as tabelas disponíveis e resume os principais resultados (2026 × 2022)."""
    _, disp = _base()
    partes = [
        "# Análise seção por seção — eleição presidencial 2026 (linha de base: 2022)",
        "Fontes: TSE — resultados por seção, detalhe da apuração, candidatos eleitos e arquivos de urna (BU, log, RDV) de todas as ~500 mil seções.",
        "Pipeline: scripts/01..10 (ver README.md). Logs conferidos: nº de votos no log = comparecimento do BU em >99,99% das seções.",
        f"Tabelas disponíveis ({len(disp)}): " + ", ".join(disp),
        f"Log bruto das urnas: {'disponível' if BRUTOS.exists() and any(BRUTOS.glob('*.zip')) else 'indisponível neste servidor'}.",
    ]
    for ano in (2026, 2022):
        p = SAIDA / f"resumo_{ano}.json"
        if p.exists():
            r = json.loads(p.read_text(encoding="utf-8"))
            a = r.get("A_votacao", {})
            partes.append(f"\n## {ano}: {r.get('secoes')} seções; sinais fortes por motivo: "
                          + json.dumps(r.get("sinais_por_motivo", {}), ensure_ascii=False)
                          + f"; teste A: {a.get('n_forte')} fortes ({a.get('forte_pro_13')} pró-13 / {a.get('forte_pro_22')} pró-22)"
                          + f"; seções com 2+ sinais: {r.get('secoes_com_2+_sinais')}")
    partes.append("\nRelatórios: use `listar_relatorios` / `ler_relatorio` (relatorio, checagem, analise_ia, resumos JSON).")
    return "\n".join(partes)


@mcp.tool(annotations=SO_LEITURA)
def listar_tabelas() -> str:
    """Lista as tabelas consultáveis via SQL com uma descrição de cada uma."""
    _, disp = _base()
    return "\n\n".join(f"### {n}\n{d}" for n, d in disp.items())


@mcp.tool(annotations=SO_LEITURA)
def descrever_tabela(tabela: str, amostra: int = 5) -> str:
    """Mostra colunas, tipos, nº de linhas (quando barato) e algumas linhas de exemplo de uma tabela.

    Args:
        tabela: nome retornado por listar_tabelas (ex.: indicadores_2026)
        amostra: nº de linhas de exemplo (máx. 20)
    """
    _, disp = _base()
    if tabela not in disp:
        return f"Tabela desconhecida. Opções: {', '.join(disp)}"
    cols, linhas, _ = _executa(f"DESCRIBE {tabela}", 1000)
    texto = [f"# {tabela}\n{disp[tabela]}\n", _tabela_texto(cols, linhas, False)]
    if tabela != "eleitores":
        n = _executa(f"SELECT count(*) FROM {tabela}", 1)[1][0][0]
        texto.append(f"\nLinhas: {n:,}".replace(",", "."))
    c, l, _ = _executa(f"SELECT * FROM {tabela} LIMIT {min(max(amostra, 1), 20)}", 20)
    texto.append("\nExemplo:\n" + _tabela_texto(c, l, False))
    return "\n".join(texto)


@mcp.tool(annotations=SO_LEITURA)
def consultar_sql(sql: str, limite: int = 500) -> str:
    """Executa uma consulta SQL de leitura (dialeto DuckDB) sobre as tabelas do projeto e devolve o resultado em TSV.

    Exemplos:
      SELECT uf, sum(v13_2) - sum(v22_2) AS margem FROM indicadores_2026 GROUP BY uf ORDER BY margem
      SELECT * FROM escores_2026 WHERE abs(z_A_voto) >= 4 ORDER BY z_A_voto
      SELECT bio, count(*) FROM eleitores WHERE ano = 2026 AND turno = 2 AND uf = 'AC' GROUP BY bio

    Args:
        sql: um único comando SELECT/WITH/DESCRIBE/SUMMARIZE
        limite: máximo de linhas devolvidas (padrão 500, máx. 5000)
    """
    try:
        cols, linhas, trunc = _executa(sql, min(max(int(limite), 1), MAX_LINHAS))
    except (ValueError, duckdb.Error) as e:
        return f"Erro: {e}"
    return _tabela_texto(cols, linhas, trunc)


@mcp.tool(annotations=SO_LEITURA)
def buscar_municipio(nome: str, uf: str | None = None) -> str:
    """Procura municípios pelo nome (sem acento ou parcial) e devolve uf, cd_municipio (código TSE) e nº de seções.

    Args:
        nome: parte do nome do município (ex.: 'sao paulo', 'ipixuna')
        uf: opcional, sigla da UF (ex.: 'AM'; 'ZZ' = exterior)
    """
    filtro = "strip_accents(lower(nm_municipio)) LIKE '%' || strip_accents(lower(?)) || '%'"
    sql = f"SELECT uf, cd_municipio, nm_municipio, count(*) AS secoes FROM indicadores_2026 WHERE {filtro}"
    params = [nome]
    if uf:
        sql += " AND uf = ?"
        params.append(uf.upper())
    sql += " GROUP BY ALL ORDER BY secoes DESC LIMIT 50"
    con, _ = _base()
    cur = con.cursor()
    try:
        rel = cur.execute(sql, params)
        return _tabela_texto([d[0] for d in rel.description], rel.fetchall(), False)
    finally:
        cur.close()


def _uf(uf):
    uf = (uf or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", uf):
        raise ValueError("UF inválida (use a sigla, ex.: SP, AM, ZZ).")
    return uf


def _uma_secao(tabela, uf, cd_municipio, nr_zona, nr_secao):
    con, _ = _base()
    cur = con.cursor()
    try:
        rel = cur.execute(f"SELECT * FROM {tabela} WHERE uf = ? AND cd_municipio = ? AND nr_zona = ? AND nr_secao = ?",
                          [uf.upper(), int(cd_municipio), int(nr_zona), int(nr_secao)])
        cols = [d[0] for d in rel.description]
        row = rel.fetchone()
        return dict(zip(cols, row)) if row else None
    finally:
        cur.close()


@mcp.tool(annotations=SO_LEITURA)
def secao(uf: str, cd_municipio: int, nr_zona: int, nr_secao: int, ano: int = 2026) -> str:
    """Ficha completa de uma seção: resultados e indicadores do log nos dois turnos, escores dos testes e motivos de sinal.

    Args:
        uf: sigla da UF (ZZ = exterior)
        cd_municipio: código TSE do município (use buscar_municipio)
        nr_zona: número da zona eleitoral
        nr_secao: número da seção
        ano: 2026 (padrão) ou 2022
    """
    if int(ano) not in (2022, 2026):
        return "ano deve ser 2026 ou 2022"
    ind = _uma_secao(f"indicadores_{int(ano)}", _uf(uf), cd_municipio, nr_zona, nr_secao)
    if not ind:
        return "Seção não encontrada."
    esc = _uma_secao(f"escores_{int(ano)}", _uf(uf), cd_municipio, nr_zona, nr_secao) or {}
    def limpa(d):
        out = {}
        for k, v in d.items():
            if v is None:
                continue
            if isinstance(v, float):
                v = round(v, 5)
            if k.startswith(("t_", "t_abre", "t_encerra", "t_ult", "t_prim")) and isinstance(v, (int, float)):
                v = f"{int(v) // 3600:02d}:{int(v) % 3600 // 60:02d}:{int(v) % 60:02d} (Brasília)" if k.endswith(("_b_1", "_b_2")) or "voto" in k else v
            out[k] = v
        return out
    return json.dumps({"indicadores": limpa(ind), "escores": limpa(esc)}, ensure_ascii=False, indent=1, default=str)


@mcp.tool(annotations=SO_LEITURA)
def linha_do_tempo_secao(uf: str, cd_municipio: int, nr_zona: int, nr_secao: int, turno: int = 2, ano: int = 2026,
                         a_partir_de: str | None = None, ate: str | None = None) -> str:
    """Lista cada voto computado na urna da seção (horário de Brasília, tipo de habilitação, duração), a partir do log.

    Args:
        uf, cd_municipio, nr_zona, nr_secao: identificação da seção
        turno: 1 ou 2
        ano: 2026 ou 2022
        a_partir_de / ate: filtro opcional de horário de Brasília no formato HH:MM (ex.: '16:30', '19:00')
    """
    def hm(s):
        h, m = s.split(":")[:2]
        return int(h) * 3600 + int(m) * 60
    uf = _uf(uf)
    ind = _uma_secao(f"indicadores_{int(ano)}", uf, cd_municipio, nr_zona, nr_secao)
    fuso = int((ind or {}).get(f"fuso_h_{int(turno)}") or 0)
    sql = (f"SELECT e.ts - {fuso} * 3600 AS tb, e.bio, e.mesa, e.dur FROM eleitores e JOIN secoes_log s "
           "ON e.ano = s.ano AND e.turno = s.turno AND e.uf = s.uf AND e.sec = s.sec "
           f"WHERE e.ano = {int(ano)} AND e.turno = {int(turno)} AND e.uf = '{uf}' AND s.ano = {int(ano)} "
           f"AND s.turno = {int(turno)} AND s.uf = '{uf}' AND s.cd_municipio = {int(cd_municipio)} "
           f"AND s.nr_zona = {int(nr_zona)} AND s.nr_secao = {int(nr_secao)}")
    if a_partir_de:
        sql += f" AND e.ts - {fuso} * 3600 >= {hm(a_partir_de)}"
    if ate:
        sql += f" AND e.ts - {fuso} * 3600 < {hm(ate)}"
    try:
        cols, linhas, trunc = _executa(sql + " ORDER BY tb", MAX_LINHAS)
    except (ValueError, duckdb.Error) as e:
        return f"Erro: {e}"
    tipo = {1: "biometria", 0: "manual (falha da digital)", 2: "sem biometria cadastrada", -1: "indeterminado"}
    out = [f"fuso aplicado: {fuso:+d} h | {len(linhas)} votos", "horario_brasilia\thabilitacao\tmesario_habilitou\tsegundos_ate_votar"]
    for tb, bio, mesa, dur in linhas:
        out.append(f"{tb // 3600:02d}:{tb % 3600 // 60:02d}:{tb % 60:02d}\t{tipo.get(bio, bio)}\t{'sim' if mesa else ''}\t{dur}")
    if trunc:
        out.append("... truncado")
    return "\n".join(out)


@functools.lru_cache(maxsize=8)
def _indice_zip(caminho):
    z = zipfile.ZipFile(caminho)
    idx = {}
    for n in z.namelist():
        m = re.search(r"(\d{5})(\d{4})(\d{4})(?:-log\.jez|\.logjez)$", n)
        if m:
            idx[(int(m.group(1)), int(m.group(2)), int(m.group(3)))] = n
    return z, idx


_trava_zip = threading.Lock()


@mcp.tool(annotations=SO_LEITURA)
def log_urna(uf: str, cd_municipio: int, nr_zona: int, nr_secao: int, turno: int = 2, ano: int = 2026,
             contem: str | None = None, dia: str | None = None, max_linhas: int = 400) -> str:
    """Lê o log bruto (texto) da urna de uma seção direto do arquivo oficial do TSE, com filtros opcionais.

    Cada linha: data hora (LOCAL da urna) | nível | id da urna | aplicação | mensagem | hash.
    Inclui logs de urnas substituídas (contingência) que vêm aninhados.

    Args:
        uf, cd_municipio, nr_zona, nr_secao: identificação da seção
        turno: 1 ou 2; ano: 2026 ou 2022
        contem: só linhas que contenham este texto (ex.: 'habilit', 'Encerr', 'computado')
        dia: só linhas desta data, formato DD/MM/AAAA (ex.: '25/10/2026')
        max_linhas: limite de linhas devolvidas (padrão 400, máx. 5000)
    """
    caminho = BRUTOS / f"{int(ano)}_{int(turno)}t_{_uf(uf)}.zip"
    if not caminho.exists():
        return "Arquivo bruto não disponível neste servidor para essa UF/ano/turno."
    with _trava_zip:
        z, idx = _indice_zip(str(caminho))
        nome = idx.get((int(cd_municipio), int(nr_zona), int(nr_secao)))
        if not nome:
            return "Seção não encontrada no arquivo de urnas (pode ser seção agregada a outra)."
        dados = z.read(nome)
    linhas = []
    for nm, conteudo in _abre_jez(dados):
        for ln in conteudo.decode("latin-1").splitlines():
            if dia and not ln.startswith(dia):
                continue
            if contem and contem.lower() not in ln.lower():
                continue
            linhas.append(ln)
    lim = min(max(int(max_linhas), 1), MAX_LINHAS)
    cab = f"arquivo: {caminho.name} :: {nome} | {len(linhas)} linhas após filtro"
    return cab + "\n" + "\n".join(linhas[:lim]) + (f"\n... truncado em {lim}" if len(linhas) > lim else "")


def _abre_jez(dados):
    """Abre .jez (zip em 2026, 7z em 2022), inclusive logs aninhados de urnas substituídas."""
    saida = []
    if dados[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(dados)) as z:
            for nm in z.namelist():
                c = z.read(nm)
                saida.extend(_abre_jez(c) if nm.lower().endswith(".jez") else [(nm, c)])
    elif dados[:6] == b"7z\xbc\xaf\x27\x1c":
        import tempfile
        import py7zr
        with tempfile.TemporaryDirectory() as tmp:
            with py7zr.SevenZipFile(io.BytesIO(dados)) as z:
                z.extractall(tmp)
            for p in sorted(Path(tmp).rglob("*")):
                if p.is_file():
                    c = p.read_bytes()
                    saida.extend(_abre_jez(c) if p.suffix.lower() == ".jez" else [(p.name, c)])
    else:
        saida.append(("?", dados))
    return saida


RELATORIOS = {
    "relatorio": ("relatorio.html", "Relatório final: testes A–E 2026 × 2022, gráficos, seções sinalizadas e análises adicionais"),
    "checagem": ("checagem.html", "Checagem de afirmações virais (19 fichas), parada da apuração, urnas 17h–19h"),
    "analise_ia": ("analise_ia.md", "Parecer técnico gerado pelo Claude a partir dos resultados agregados"),
    "resumo_2026": ("resumo_2026.json", "Números agregados de todos os testes, 2026"),
    "resumo_2022": ("resumo_2022.json", "Números agregados de todos os testes, 2022"),
    "pos17": ("pos17_resumo.json", "Urnas que votaram entre 17h e 19h e divisões por horário de encerramento"),
    "checagem_dados": ("checagem_dados.json", "Números usados na checagem (presidente, Congresso, transferências, apuração)"),
}


@mcp.tool(annotations=SO_LEITURA)
def listar_relatorios() -> str:
    """Lista os relatórios e resumos disponíveis para leitura."""
    return "\n".join(f"- {k}: {d}" for k, (f, d) in RELATORIOS.items() if (SAIDA / f).exists())


@mcp.tool(annotations=SO_LEITURA)
def ler_relatorio(nome: str, inicio: int = 0, tamanho: int = 60000) -> str:
    """Lê um relatório como texto (HTML é convertido em texto, sem imagens). Use inicio/tamanho para paginar.

    Args:
        nome: chave de listar_relatorios (relatorio, checagem, analise_ia, resumo_2026, resumo_2022, pos17, checagem_dados)
        inicio: posição (caracteres) de onde começar
        tamanho: quantidade de caracteres (padrão 60000)
    """
    if nome not in RELATORIOS:
        return f"Opções: {', '.join(RELATORIOS)}"
    p = SAIDA / RELATORIOS[nome][0]
    if not p.exists():
        return "Relatório ainda não gerado."
    t = p.read_text(encoding="utf-8")
    if p.suffix == ".html":
        t = re.sub(r"<img[^>]*>", "[gráfico]", t)
        t = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", t, flags=re.S)
        t = re.sub(r"</(p|div|li|tr|h\d|table)>|<br\s*/?>", "\n", t)
        t = re.sub(r"</t[dh]>", "\t", t)
        t = htmllib.unescape(re.sub(r"<[^>]+>", "", t))
        t = re.sub(r"[ \t]{2,}", " ", re.sub(r"\n\s*\n+", "\n\n", t))
    trecho = t[inicio:inicio + tamanho]
    resto = len(t) - (inicio + len(trecho))
    return trecho + (f"\n\n[... mais {resto} caracteres; chame de novo com inicio={inicio + len(trecho)}]" if resto > 0 else "")


# ----------------------------------------------------------------------------- execução
class _ExigeToken:
    """Middleware ASGI simples: exige o MCP_TOKEN quando definido. Aceita de duas formas:
    - cabeçalho 'Authorization: Bearer <token>' (Claude Code, Claude Desktop, clientes que permitem cabeçalhos);
    - token no caminho da URL: /<token>/mcp (Claude na web, cujos conectores não permitem cabeçalhos)."""

    def __init__(self, app, token):
        self.app, self.token = app, token
        self.prefixo = f"/{token}"

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path") != "/saude":
            path = scope.get("path", "")
            if path == self.prefixo or path.startswith(self.prefixo + "/"):
                novo = path[len(self.prefixo):] or "/"
                scope = dict(scope, path=novo, raw_path=novo.encode())
                await self.app(scope, receive, send)
                return
            if path.startswith("/.well-known/"):  # sem OAuth: responder 404 para clientes não tentarem login
                await send({"type": "http.response.start", "status": 404, "headers": [(b"content-type", b"text/plain")]})
                await send({"type": "http.response.body", "body": b"not found"})
                return
            cab = dict(scope.get("headers") or [])
            if not hmac.compare_digest(cab.get(b"authorization", b"").decode(), f"Bearer {self.token}"):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"text/plain; charset=utf-8"), (b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": "token inválido ou ausente".encode()})
                return
        await self.app(scope, receive, send)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="serve via streamable-http em /mcp (padrão: stdio)")
    ap.add_argument("--host", default=os.environ.get("MCP_HOST", "127.0.0.1"))
    ap.add_argument("--porta", type=int, default=int(os.environ.get("MCP_PORTA", "8000")))
    a = ap.parse_args()
    _base()  # valida o catálogo ao subir
    if not a.http:
        mcp.run("stdio")
        return
    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings
    from starlette.responses import PlainTextResponse
    from starlette.routing import Route
    token = os.environ.get("MCP_TOKEN")
    # atrás de túnel/proxy o cabeçalho Host é o domínio público; com token exigido a proteção contra
    # DNS rebinding (que só aceita Host local) é redundante e bloquearia o acesso
    seguranca = TransportSecuritySettings(enable_dns_rebinding_protection=False) if (token or a.host != "127.0.0.1") else None
    app = mcp.streamable_http_app(stateless_http=True, json_response=True, transport_security=seguranca, host=a.host)
    app.router.routes.append(Route("/saude", lambda req: PlainTextResponse("ok")))
    uvicorn.run(_ExigeToken(app, token) if token else app, host=a.host, port=a.porta)


if __name__ == "__main__":
    main()
