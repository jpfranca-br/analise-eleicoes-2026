"""Junta resultados + logs e calcula indicadores por seção (1 linha por seção, 1º e 2º turno lado a lado).

Uso:  python -I scripts/04_indicadores.py [--anos 2026 2022]
Saída: dados/processados/indicadores_{ano}.parquet

Horários: o relógio da urna está em hora local. A diferença para Brasília é estimada por município
e turno como a hora (moda) de "Urna pronta para receber votos" menos 8h. Todos os horários abaixo
(abertura, 17h, etc.) estão em horário de Brasília.
Sufixos _1 e _2 = 1º e 2º turno.
"""
import argparse
from pathlib import Path

import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "dados" / "processados"
LOGS = PROC / "logs"
CHAVE = ["uf", "cd_municipio", "nr_zona", "nr_secao"]
H17 = 17 * 3600


def metricas_log(ano, turno):
    """Indicadores derivados do log para todas as UFs disponíveis de um ano/turno."""
    arquivos = sorted(LOGS.glob(f"secoes_{ano}_{turno}t_*.parquet"))
    if not arquivos:
        return None
    saidas, curvas = [], []
    for arq_s in arquivos:
        uf = arq_s.stem.split("_")[-1]
        s = pl.read_parquet(arq_s)
        if "falha" in s.columns:
            s = s.filter(pl.col("falha").is_null())
        e = pl.read_parquet(LOGS / f"eleitores_{ano}_{turno}t_{uf}.parquet")
        # fuso: moda da hora de abertura por município (abertura às 7h50+ conta como 8h)
        s = s.with_columns(((pl.col("t_pronta") + 600) // 3600).alias("_h_abre"))
        fuso = (s.drop_nulls("_h_abre").group_by("cd_municipio")
                 .agg(pl.col("_h_abre").mode().first().alias("_h_mun"))
                 .with_columns((pl.col("_h_mun") - 8).alias("fuso_h")))
        s = s.join(fuso.select("cd_municipio", "fuso_h"), on="cd_municipio", how="left") \
             .with_columns(pl.col("fuso_h").fill_null(0))
        e = e.join(s.select("sec", "fuso_h"), on="sec").with_columns(
            (pl.col("ts") - pl.col("fuso_h") * 3600).alias("tb")).sort("sec", "tb")
        e = e.with_columns([
            (pl.col("tb") >= H17).alias("pos17"),
            (pl.col("tb") - pl.col("tb").shift(1).over("sec")).alias("gap"),
            (pl.col("tb") // 3600).alias("hora"),
        ])
        dia = pl.col("pos17").not_()
        pos = pl.col("pos17")
        ag = e.group_by("sec").agg([
            dia.sum().alias("n_dia"),
            pos.sum().alias("n_pos17"),
            pl.col("tb").min().alias("t_prim_voto"),
            pl.col("tb").max().alias("t_ult_voto"),
            ((pl.col("bio") == 0) & dia).sum().alias("manual_dia"),
            ((pl.col("bio") == 0) & pos).sum().alias("manual_pos17"),
            ((pl.col("bio") == 2) & dia).sum().alias("semcad_dia"),
            ((pl.col("bio") == 2) & pos).sum().alias("semcad_pos17"),
            ((pl.col("mesa") == 1)).sum().alias("mesario_hab"),
            pl.col("dur").filter(dia).median().alias("dur_med_dia"),
            pl.col("dur").filter(pos).median().alias("dur_med_pos17"),
            pl.col("gap").filter(dia).median().alias("gap_med_dia"),
            pl.col("gap").filter(pos).median().alias("gap_med_pos17"),
            (pl.col("gap") < 30).sum().alias("n_gap_lt30"),
            ((pl.col("gap") < 30) & pos).sum().alias("n_gap_lt30_pos17"),
        ])
        # pico de votos/hora durante o dia (8h-17h) e na última hora antes das 17h
        hor = e.filter(dia & (pl.col("hora") >= 8)).group_by("sec", "hora").len()
        pico = hor.group_by("sec").agg(pl.col("len").max().alias("pico_hora_dia"))
        ult = hor.filter(pl.col("hora") == 16).select("sec", pl.col("len").alias("n_16h"))
        manual_ult = e.filter((pl.col("hora") == 16) & (pl.col("bio") == 0)).group_by("sec") \
                      .len().rename({"len": "manual_16h"})
        s = (s.join(ag, on="sec", how="left").join(pico, on="sec", how="left")
              .join(ult, on="sec", how="left").join(manual_ult, on="sec", how="left"))
        saidas.append(s.with_columns(pl.lit(uf).alias("uf")))
        curvas.append(e.with_columns((pl.col("tb") // 900 * 900).alias("t15"))
                       .group_by("t15", "bio").len().with_columns(pl.lit(uf).alias("uf")))
    s = pl.concat(saidas, how="diagonal_relaxed")
    pl.concat(curvas).write_parquet(PROC / f"curva_horaria_{ano}_{turno}t.parquet")
    # horário de Brasília para marcos da seção
    s = s.with_columns([
        (pl.col("t_pronta") - pl.col("fuso_h") * 3600).alias("t_abre_b"),
        (pl.col("t_encerrar") - pl.col("fuso_h") * 3600).alias("t_encerra_b"),
    ])
    horas_dia = ((H17 - pl.max_horizontal(pl.col("t_abre_b"), pl.lit(8 * 3600))) / 3600).clip(0.5, 9)
    janela_pos = ((pl.col("t_ult_voto") - H17) / 3600).clip(lower_bound=1 / 12)
    s = s.with_columns([
        (pl.col("n_dia") / horas_dia).alias("taxa_dia"),
        pl.when(pl.col("n_pos17") > 0).then(pl.col("n_pos17") / janela_pos).alias("taxa_pos17"),
        (pl.col("n_pos17") / pl.col("n_votos")).alias("pct_pos17"),
        ((pl.col("manual_dia") + pl.col("manual_pos17")) / pl.col("n_votos")).alias("pct_manual"),
        ((pl.col("semcad_dia") + pl.col("semcad_pos17")) / pl.col("n_votos")).alias("pct_semcad"),
        (pl.col("manual_dia") / pl.col("n_dia")).alias("pct_manual_dia"),
        (pl.col("manual_pos17") / pl.col("n_pos17")).alias("pct_manual_pos17"),
    ]).with_columns(
        (pl.col("taxa_pos17") / pl.col("taxa_dia")).alias("razao_taxa_pos17_dia"),
        (pl.col("taxa_pos17") / pl.col("pico_hora_dia")).alias("razao_taxa_pos17_pico"),
    )
    manter = CHAVE + [
        "fuso_h", "contingencia", "n_arquivos", "n_urnas", "n_votos", "n_bio", "n_manual",
        "n_mesario", "n_sem_cadastro", "n_indet", "n_suspensa", "n_reinicio", "n_presentes_nao",
        "n_parcial", "n_sem_voto", "n_ja_votou", "n_erro", "t_abre_b", "t_encerra_b",
        "t_prim_voto", "t_ult_voto", "n_dia", "n_pos17", "taxa_dia", "taxa_pos17", "pico_hora_dia",
        "n_16h", "manual_16h", "razao_taxa_pos17_dia", "razao_taxa_pos17_pico", "pct_pos17",
        "pct_manual", "pct_semcad", "manual_dia", "manual_pos17", "semcad_dia", "semcad_pos17",
        "pct_manual_dia", "pct_manual_pos17", "mesario_hab", "dur_med_dia", "dur_med_pos17",
        "gap_med_dia", "gap_med_pos17", "n_gap_lt30", "n_gap_lt30_pos17"]
    return s.select([c for c in manter if c in s.columns])


def resultados(ano):
    r = pl.read_parquet(PROC / f"resultados_{ano}.parquet")
    vcols = [c for c in r.columns if c.startswith("v") and c[1:].isdigit()]
    r = r.with_columns((pl.col("nominais")).alias("validos"))
    r = r.with_columns([
        (pl.col("v13") / pl.col("validos")).alias("p13"),
        (pl.col("v22") / pl.col("validos")).alias("p22"),
        (pl.col("abstencoes") / pl.col("aptos")).alias("p_abst"),
        (pl.col("brancos") / pl.col("comparecimento")).alias("p_branco"),
        (pl.col("nulos") / pl.col("comparecimento")).alias("p_nulo"),
    ] + [(pl.col(c) / pl.col("validos")).alias("p" + c[1:]) for c in vcols if c not in ("v13", "v22")])
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs="+", default=["2026", "2022"])
    a = ap.parse_args()
    for ano in a.anos:
        r = resultados(ano)
        fixas = ["nm_municipio", "nr_local", "nm_local"]
        partes = []
        for t in (1, 2):
            rt = r.filter(pl.col("turno") == t).drop("turno", "ano")
            if t == 2:  # candidatos eliminados não existem no 2º turno
                rt = rt.select([c for c in rt.columns
                                if not ((c.startswith("v") or c.startswith("p")) and c[1:].isdigit()
                                        and c not in ("v13", "v22", "p13", "p22"))])
            lg = metricas_log(ano, t)
            if lg is not None:
                rt = rt.join(lg, on=CHAVE, how="left")
            ren = {c: f"{c}_{t}" for c in rt.columns if c not in CHAVE + fixas}
            rt = rt.rename(ren)
            if t == 2:
                rt = rt.drop([c for c in fixas if c in rt.columns])
            partes.append(rt)
        df = partes[0].join(partes[1], on=CHAVE, how="full", coalesce=True)
        # diferenças entre turnos
        d = []
        for c in ["p13", "p22", "p_abst", "p_branco", "p_nulo", "pct_manual", "pct_semcad",
                  "pct_pos17", "razao_taxa_pos17_dia"]:
            if f"{c}_1" in df.columns and f"{c}_2" in df.columns:
                d.append((pl.col(f"{c}_2") - pl.col(f"{c}_1")).alias(f"d_{c}"))
        df = df.with_columns(d).with_columns(pl.lit(int(ano)).alias("ano"))
        df.write_parquet(PROC / f"indicadores_{ano}.parquet")
        com_log = df.filter(pl.col("n_votos_2").is_not_null()).height if "n_votos_2" in df.columns else 0
        print(f"{ano}: {df.height} seções, {com_log} com log do 2º turno, {len(df.columns)} colunas")


if __name__ == "__main__":
    main()
