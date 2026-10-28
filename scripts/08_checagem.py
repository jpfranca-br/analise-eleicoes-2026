"""Checagem de afirmações de uma mensagem viral com dados oficiais do TSE já baixados.

Uso:  python -I scripts/08_checagem.py
Saída: saida/checagem_dados.json (todos os números) e figuras em saida/fig_checagem/
Os vereditos em texto ficam em saida/checagem.html (gerado por 09_checagem_html.py).
"""
import json
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy.optimize import nnls

RAIZ = Path(__file__).resolve().parent.parent
ODS = RAIZ / "dados" / "brutos" / "odsele"
PROC = RAIZ / "dados" / "processados"
SAIDA = RAIZ / "saida"
FIG = SAIDA / "fig_checagem"
COR = {2026: "#2a78d6", 2022: "#eb6834"}
TXT2, GRADE, FUNDO = "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "axes.edgecolor": GRADE,
                     "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "axes.grid": True, "grid.color": GRADE, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "font.size": 10})

# Classificação ideológica dos partidos: baseada em Bolognesi, Ribeiro & Codato (2023), "Uma nova
# classificação ideológica dos partidos políticos brasileiros" (Dados, 66(2)). Partidos criados ou
# renomeados depois foram alocados pela origem (PRD = PTB+Patriota; MOBILIZA = ex-PMN; MISSÃO = MBL;
# UNIÃO = DEM+PSL). DEMOCRATA, sem classificação acadêmica, fica provisoriamente no centro.
IDEOLOGIA = {
    "extrema-esquerda/esquerda": ["PSOL", "PCO", "PSTU", "PCB", "UP", "PT", "PCDOB", "PC do B"],
    "centro-esquerda": ["PSB", "PDT", "PV", "REDE"],
    "centro": ["MDB", "PSDB", "CIDADANIA", "SOLIDARIEDADE", "AVANTE", "PMB", "PMN", "MOBILIZA", "AGIR", "DEMOCRATA"],
    "centro-direita": ["PSD", "PODE", "PROS"],
    "direita/extrema-direita": ["PL", "PP", "REPUBLICANOS", "UNIÃO", "NOVO", "PRTB", "PSC", "PTB",
                                "PATRIOTA", "PRD", "DC", "MISSÃO"],
}
PART2IDEO = {p: k for k, ps in IDEOLOGIA.items() for p in ps}


def campo(p):
    """Agrupa em 3 campos; 'direita ampla' = centro-direita + direita."""
    i = PART2IDEO.get(p, "?")
    if i in ("extrema-esquerda/esquerda", "centro-esquerda"):
        return "esquerda"
    if i in ("centro-direita", "direita/extrema-direita"):
        return "direita"
    return "centro" if i == "centro" else "?"


def cand(ano):
    with zipfile.ZipFile(ODS / f"consulta_cand_{ano}.zip") as z:
        return pl.read_csv(z.read(f"consulta_cand_{ano}_BRASIL.csv"), separator=";",
                           encoding="latin1", infer_schema_length=0)


def res(ano):
    return pl.read_parquet(PROC / f"resultados_{ano}.parquet")


def presidenciais(ano):
    r = res(ano)
    c = cand(ano).filter(pl.col("DS_CARGO") == "PRESIDENTE").select(
        pl.col("NR_CANDIDATO").cast(pl.Int64).alias("nr"), pl.col("NM_URNA_CANDIDATO").alias("nome"),
        pl.col("SG_PARTIDO").alias("partido")).unique("nr")
    out = {}
    for t in (1, 2):
        rt = r.filter(pl.col("turno") == t)
        vcols = [x for x in rt.columns if x.startswith("v") and x[1:].isdigit() and rt[x].sum() > 0]
        val = int(rt["nominais"].sum())
        linhas = []
        for v in vcols:
            nr = int(v[1:])
            q = int(rt[v].sum())
            info = c.filter(pl.col("nr") == nr)
            nome = info["nome"][0] if info.height else str(nr)
            part = info["partido"][0] if info.height else "?"
            linhas.append({"nr": nr, "nome": nome, "partido": part, "ideologia": PART2IDEO.get(part, "?"),
                           "votos": q, "pct_validos": round(100 * q / val, 3)})
        linhas.sort(key=lambda x: -x["votos"])
        out[t] = {"validos": val, "aptos": int(rt["aptos"].sum()), "comparecimento": int(rt["comparecimento"].sum()),
                  "abstencoes": int(rt["abstencoes"].sum()), "brancos": int(rt["brancos"].sum()),
                  "nulos": int(rt["nulos"].sum()), "candidatos": linhas}
    return out


def lideres(ano, nivel):
    r = res(ano)
    chave = ["uf"] if nivel == "uf" else ["uf", "cd_municipio", "nm_municipio"]
    rows = {}
    for t in (1, 2):
        rt = r.filter(pl.col("turno") == t)
        vcols = [x for x in rt.columns if x.startswith("v") and x[1:].isdigit() and rt[x].sum() > 0]
        g = rt.group_by(chave).agg([pl.col(v).sum() for v in vcols] + [pl.col("aptos").sum(), pl.col("nominais").sum()])
        arr = g.select(vcols).to_numpy()
        g = g.with_columns(pl.Series("lider", [int(vcols[i][1:]) for i in arr.argmax(1)]),
                           (pl.col("v13") / pl.col("nominais")).alias("p13"),
                           (pl.col("v22") / pl.col("nominais")).alias("p22"))
        rows[t] = g.select(chave + ["lider", "v13", "v22", "p13", "p22", "aptos", "nominais"])
    return rows[1].join(rows[2], on=chave, suffix="_2", how="full", coalesce=True)


def congresso():
    out = {}
    for ano in (2026, 2022):
        c = cand(ano)
        el = c.filter(pl.col("DS_SIT_TOT_TURNO").str.contains("^ELEITO"))
        for cargo in ("DEPUTADO FEDERAL", "GOVERNADOR", "SENADOR"):
            e = el.filter(pl.col("DS_CARGO") == cargo)
            if cargo == "GOVERNADOR":  # se houve 2º turno, vale o resultado do 2º
                e = e.sort("NR_TURNO").unique(["SG_UF"], keep="last")
            part = e.group_by("SG_PARTIDO").len().sort("len", descending=True)
            por_campo = {}
            for p, n in part.iter_rows():
                por_campo[campo(p)] = por_campo.get(campo(p), 0) + n
            out[f"{cargo}_{ano}"] = {"total": e.height, "por_partido": dict(part.iter_rows()),
                                     "por_campo": por_campo,
                                     "lista": e.select("SG_UF", "NM_URNA_CANDIDATO", "SG_PARTIDO").sort("SG_UF").rows()
                                     if cargo == "GOVERNADOR" else None}
    # Senado em 2027 = eleitos em 2026 (2/3) + eleitos em 2022 (1/3); filiação da época da eleição
    s = {}
    for k in ("SENADOR_2026", "SENADOR_2022"):
        for p, n in out[k]["por_partido"].items():
            s[p] = s.get(p, 0) + n
    out["SENADO_2027_composicao"] = {"total": sum(s.values()), "por_partido": dict(sorted(s.items(), key=lambda x: -x[1])),
                                     "por_campo": {cp: sum(n for p, n in s.items() if campo(p) == cp)
                                                   for cp in ("esquerda", "centro", "direita", "?")}}
    return out


def crescimento_municipal():
    """Testa várias definições de 'cresceu' entre o 1º e o 2º turno, por município (e cidade no exterior)."""
    m = lideres(2026, "mun")
    m = m.with_columns((pl.col("uf") == "ZZ").alias("exterior"))
    defs = {
        "votos absolutos": (pl.col("v13_2") > pl.col("v13"), pl.col("v22_2") > pl.col("v22")),
        "% dos válidos": (pl.col("p13_2") > pl.col("p13"), pl.col("p22_2") > pl.col("p22")),
        "ganho absoluto maior que o do adversário": (
            (pl.col("v13_2") - pl.col("v13")) > (pl.col("v22_2") - pl.col("v22")),
            (pl.col("v22_2") - pl.col("v22")) > (pl.col("v13_2") - pl.col("v13"))),
        "ganho em pontos % maior que o do adversário": (
            (pl.col("p13_2") - pl.col("p13")) > (pl.col("p22_2") - pl.col("p22")),
            (pl.col("p22_2") - pl.col("p22")) > (pl.col("p13_2") - pl.col("p13"))),
    }
    out = {"municipios_brasil": int((~m["exterior"]).sum()), "cidades_exterior": int(m["exterior"].sum())}
    for nome, (c13, c22) in defs.items():
        x = m.with_columns(c13.alias("a"), c22.alias("b"))
        out[nome] = {"lula_cresceu": int(x["a"].sum()), "flavio_cresceu": int(x["b"].sum()),
                     "lula_cresceu_so_brasil": int(x.filter(~pl.col("exterior"))["a"].sum()),
                     "flavio_cresceu_so_brasil": int(x.filter(~pl.col("exterior"))["b"].sum())}
    lid = m.filter(~pl.col("exterior"))
    out["lider_1t_municipios"] = {str(k): v for k, v in lid.group_by("lider").len().sort("len", descending=True).iter_rows()}
    out["lider_1t_aptos"] = {str(k): v for k, v in lid.group_by("lider").agg(pl.col("aptos").sum()).sort("aptos", descending=True).iter_rows()}
    out["lider_2t_municipios"] = {str(k): v for k, v in lid.group_by("lider_2").len().sort("len", descending=True).iter_rows()}
    out["viradas_municipais"] = {f"{a}->{b}": n for a, b, n in lid.group_by("lider", "lider_2").len().sort("len", descending=True).iter_rows()}
    # mesma conta para 2022, como referência
    m22 = lideres(2022, "mun")
    out["ref_2022_votos_absolutos"] = {"lula_cresceu": int((m22["v13_2"] > m22["v13"]).sum()),
                                       "bolsonaro_cresceu": int((m22["v22_2"] > m22["v22"]).sum()),
                                       "total": m22.height}
    return out


def transferencias(ano):
    """Inferência ecológica (mínimos quadrados não negativos), por UF, ponderada nacionalmente.
    Para cada UF: votos_2T_destino(seção) ~ soma_k taxa_k,destino * votos_1T_origem_k(seção).
    Destinos: 13, 22, não-válido (abstenção+branco+nulo). Origens: candidatos com >=1% + 'outros' + não-válido no 1T."""
    r = res(ano)
    w = r.filter(pl.col("turno") == 1)
    vcols = [x for x in w.columns if x.startswith("v") and x[1:].isdigit() and w[x].sum() > 0]
    tot = {v: w[v].sum() for v in vcols}
    val = w["nominais"].sum()
    princ = [v for v in vcols if tot[v] / val >= 0.01]
    outros = [v for v in vcols if v not in princ]
    k = ["uf", "cd_municipio", "nr_zona", "nr_secao"]
    a = w.select(k + princ + [pl.sum_horizontal(outros).alias("outros"),
                              (pl.col("abstencoes") + pl.col("brancos") + pl.col("nulos")).alias("nao_valido")])
    b = r.filter(pl.col("turno") == 2).select(k + [pl.col("v13").alias("d13"), pl.col("v22").alias("d22"),
                                                   (pl.col("abstencoes") + pl.col("brancos") + pl.col("nulos")).alias("dnv")])
    j = a.join(b, on=k)
    origens = princ + ["outros", "nao_valido"]
    acum = {o: np.zeros(3) for o in origens}
    for uf in j["uf"].unique().to_list():
        x = j.filter(pl.col("uf") == uf)
        X = x.select(origens).to_numpy().astype(float)
        T = np.zeros((len(origens), 3))
        for di, dcol in enumerate(["d13", "d22", "dnv"]):
            T[:, di], _ = nnls(X, x[dcol].to_numpy().astype(float))
        T = T / np.clip(T.sum(1, keepdims=True), 1e-9, None)   # normaliza: cada origem soma 100%
        peso = X.sum(0)
        for i, o in enumerate(origens):
            acum[o] += T[i] * peso[i]
    out = {}
    for o in origens:
        s = acum[o].sum()
        out[o] = {"votos_1t": int(s), "para_13": round(100 * acum[o][0] / s, 1),
                  "para_22": round(100 * acum[o][1] / s, 1), "nao_valido": round(100 * acum[o][2] / s, 1)}
    return out


def estados_foco():
    out = {}
    for ano in (2026, 2022):
        u = lideres(ano, "uf")
        sel = u.filter(pl.col("uf").is_in(["GO", "MT", "SC", "PR", "RS"])).sort("uf")
        out[ano] = {row["uf"]: {"p13_1t": round(100 * row["p13"], 2), "p13_2t": round(100 * row["p13_2"], 2),
                                "p22_1t": round(100 * row["p22"], 2), "p22_2t": round(100 * row["p22_2"], 2),
                                "lider_1t": row["lider"], "lider_2t": row["lider_2"]}
                    for row in sel.iter_rows(named=True)}
        out[f"{ano}_todas_ufs"] = {row["uf"]: {"lider_1t": row["lider"], "lider_2t": row["lider_2"],
                                               "p13_1t": round(100 * row["p13"], 2), "p13_2t": round(100 * row["p13_2"], 2),
                                               "p22_1t": round(100 * row["p22"], 2), "p22_2t": round(100 * row["p22_2"], 2)}
                                   for row in u.sort("uf").iter_rows(named=True)}
    return out


def apuracao():
    """Horário de recebimento dos BUs e de primeira totalização (horário do TSE = Brasília)."""
    out = {}
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
    for ano, t, estilo in [(2026, 2, "-"), (2026, 1, ":"), (2022, 2, "--")]:
        with zipfile.ZipFile(ODS / f"detalhe_votacao_secao_{ano}.zip") as z:
            d = pl.read_csv(z.read(f"detalhe_votacao_secao_{ano}_BR.csv"), separator=";", encoding="latin1",
                            columns=["NR_TURNO", "CD_CARGO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO",
                                     "DT_RECEBIMENTO_BU_HOR_TSE", "DT_PRIM_TOT_PARCIAL_HOR_TSE"],
                            infer_schema_length=0)
        d = d.filter((pl.col("NR_TURNO") == str(t)) & (pl.col("CD_CARGO") == "1")).with_columns([
            pl.col("DT_RECEBIMENTO_BU_HOR_TSE").str.strptime(pl.Datetime, "%d/%m/%Y %H:%M:%S", strict=False).alias("rec"),
            pl.col("DT_PRIM_TOT_PARCIAL_HOR_TSE").str.strptime(pl.Datetime, "%d/%m/%Y %H:%M:%S", strict=False).alias("tot"),
            pl.col("CD_MUNICIPIO").cast(pl.Int64).alias("cd_municipio"), pl.col("NR_ZONA").cast(pl.Int64).alias("nr_zona"),
            pl.col("NR_SECAO").cast(pl.Int64).alias("nr_secao"), pl.col("SG_UF").alias("uf")])
        r = res(ano).filter(pl.col("turno") == t).select("uf", "cd_municipio", "nr_zona", "nr_secao", "v13", "v22")
        d = d.join(r, on=["uf", "cd_municipio", "nr_zona", "nr_secao"], how="left")
        info = {"secoes": d.height, "sem_horario_recebimento": int(d["rec"].null_count()),
                "sem_horario_totalizacao": int(d["tot"].null_count())}
        for col in ("rec", "tot"):
            s = d.drop_nulls(col).sort(col)
            ts = s[col]
            n = len(ts)
            q = lambda f: str(ts[int(f * (n - 1))])
            # maior intervalo sem nenhuma seção entre 1% e 99% do total
            seg = ts.dt.epoch("s").to_numpy()
            i0, i1 = 0, int(0.99 * n)  # desde o 1º BU (a pausa de 2026 ocorreu antes de 1% recebido)
            gaps = np.diff(seg[i0:i1])
            gi = int(np.argmax(gaps))
            info[col] = {"primeira": str(ts[0]), "p50": q(0.5), "p90": q(0.9), "p99": q(0.99), "ultima": str(ts[-1]),
                         "maior_pausa_min_ate_99pct": round(float(gaps[gi]) / 60, 1),
                         "maior_pausa_inicio": str(ts[i0 + gi]), "maior_pausa_fim": str(ts[i0 + gi + 1]),
                         "pausas_maiores_que_5min": int((gaps > 300).sum())}
        # evolução do % de Lula conforme a totalização avança (ordem de totalização)
        s = d.drop_nulls("tot").sort("tot").with_columns(pl.col("v13").cum_sum().alias("c13"), pl.col("v22").cum_sum().alias("c22"))
        s = s.with_columns((pl.col("c13") / (pl.col("c13") + pl.col("c22"))).alias("p13_acum"),
                           (pl.int_range(pl.len()) / pl.len()).alias("frac"))
        marcos = {}
        for f in (0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0):
            row = s.row(min(int(f * s.height), s.height - 1), named=True)
            marcos[f"{int(f * 100)}%"] = {"hora": str(row["tot"]), "pct_lula": round(100 * row["p13_acum"], 2)}
        lider_troca = s.with_columns((pl.col("p13_acum") > 0.5).alias("l")).filter(pl.col("frac") > 0.01)
        trocas = int((lider_troca["l"] != lider_troca["l"].shift(1)).sum() - 1)
        info["evolucao_pct_lula_por_secoes_totalizadas"] = marcos
        info["trocas_de_lider_apos_1pct"] = max(trocas, 0)
        out[f"{ano}_{t}t"] = info
        cor = COR[ano]
        rec = d.drop_nulls("rec").sort("rec")
        h0 = rec["rec"][0].replace(hour=17, minute=0, second=0)
        x = (rec["rec"] - h0).dt.total_seconds().to_numpy() / 3600 + 17
        axs[0].plot(x, 100 * np.arange(1, len(x) + 1) / d.height, color=cor, ls=estilo, lw=2, label=f"{ano} {t}º turno")
        x2 = (s["tot"] - h0).dt.total_seconds().to_numpy() / 3600 + 17
        axs[1].plot(x2, 100 * s["p13_acum"].to_numpy(), color=cor, ls=estilo, lw=2, label=f"{ano} {t}º turno")
    axs[0].set_xlim(17, 23); axs[0].set_xlabel("horário (Brasília)"); axs[0].set_ylabel("% de BUs recebidos")
    axs[0].set_title("Recebimento dos boletins de urna no TSE", loc="left", fontsize=11)
    axs[1].set_xlim(17, 23); axs[1].set_xlabel("horário (Brasília)"); axs[1].set_ylabel("% de Lula entre 13 e 22 (acumulado)")
    axs[1].axhline(50, color=TXT2, lw=1, ls=":")
    axs[1].set_title("Placar acumulado durante a totalização", loc="left", fontsize=11)
    axs[1].legend(); axs[0].legend()
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "apuracao.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    SAIDA.mkdir(exist_ok=True)
    dados = {
        "presidente_2026": presidenciais(2026), "presidente_2022": presidenciais(2022),
        "congresso_governadores": congresso(),
        "crescimento_municipal": crescimento_municipal(),
        "transferencias_2026": transferencias(2026), "transferencias_2022": transferencias(2022),
        "estados": estados_foco(),
        "apuracao": apuracao(),
        "classificacao_ideologica": IDEOLOGIA,
    }
    (SAIDA / "checagem_dados.json").write_text(json.dumps(dados, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(dados, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
