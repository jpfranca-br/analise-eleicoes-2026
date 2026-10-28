"""Urnas que receberam votos entre 17h e 19h no 2º turno de 2026 (prorrogação da votação até 19h).

Uso:  python -I scripts/10_pos17.py
Saídas: saida/pos17_resumo.json, saida/pos17_secoes.csv, saida/fig_pos17/*.png

Grupos (horário de Brasília, 2º turno):
  ESTENDIDA : urna com voto computado depois de 17h15 (continuou aberta além da fila normal das 17h)
  FILA      : votos só até 17h15 (fila de quem chegou até 17h)
  NORMAL    : nenhum voto depois de 17h
Perguntas:
  1. Quantas urnas, onde, até que horas; alguma votou depois de fechar ou depois de 19h?
  2. Dentro das urnas ESTENDIDAS: os votos de 17h15-19h têm perfil diferente dos votos do dia
     (biometria, tempo de votação, intervalo entre eleitores, rajadas)?
  3. Resultado: essas seções desviam do esperado (teste A/B) mais que seções vizinhas do mesmo município?
  4. Comparação com o 1º turno das mesmas seções e com 2022.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "dados" / "processados"
LOGS = PROC / "logs"
SAIDA = RAIZ / "saida"
FIG = SAIDA / "fig_pos17"
CHAVE = ["uf", "cd_municipio", "nr_zona", "nr_secao"]
H17, H1715, H19 = 17 * 3600, 17 * 3600 + 15 * 60, 19 * 3600
COR, COR2, TXT2, GRADE, FUNDO = "#2a78d6", "#eb6834", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "axes.edgecolor": GRADE,
                     "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "axes.grid": True, "grid.color": GRADE, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "font.size": 10})


def eleitores(ano, turno, ind):
    """Todos os votos computados com horário de Brasília e chave da seção."""
    fuso = ind.select(CHAVE + [pl.col(f"fuso_h_{turno}").alias("fuso_h")]).drop_nulls("fuso_h")
    partes = []
    for arq in sorted(LOGS.glob(f"secoes_{ano}_{turno}t_*.parquet")):
        uf = arq.stem.split("_")[-1]
        s = pl.read_parquet(arq).select(["sec"] + CHAVE + ["t_encerrar", "t_pronta", "t_pronta_ult", "contingencia", "n_urnas"])
        e = pl.read_parquet(LOGS / f"eleitores_{ano}_{turno}t_{uf}.parquet")
        s = s.join(fuso, on=CHAVE, how="inner")
        e = e.join(s.select("sec", "fuso_h", *CHAVE, "t_encerrar"), on="sec")
        partes.append(e.with_columns((pl.col("ts") - pl.col("fuso_h") * 3600).alias("tb"),
                                     (pl.col("t_encerrar") - pl.col("fuso_h") * 3600).alias("enc_b")).drop("sec"))
    e = pl.concat(partes).sort(CHAVE + ["tb"])
    return e.with_columns((pl.col("tb") - pl.col("tb").shift(1).over(CHAVE)).alias("gap"))


def categoria(motivo):
    for chave, nome in [("log com", "log ≠ BU"), ("depois do horário de encerramento", "voto após encerramento"),
                        ("depois de 19h", "voto após 19h"), ("antes das 17h", "encerramento antes de 17h"),
                        ("redesenhada", "seção redesenhada entre turnos")]:
        if chave in motivo:
            return nome
    return "outro"


def divisao_encerramento(ano):
    """Margem Lula-adversário (2º e 1º turno) separando urnas pelo horário de encerramento no 2º turno.
    Testa vários cortes, porque 'fechou às 17h' vs 'depois' depende de como se define (o encerramento leva ~1 min)."""
    d = pl.read_parquet(PROC / f"indicadores_{ano}.parquet")
    if "t_encerra_b_2" not in d.columns:
        return None
    d = d.filter(pl.col("t_encerra_b_2").is_not_null())
    if d.height == 0:
        return None
    enc = pl.col("t_encerra_b_2")
    cortes = {"encerrou depois de 17h00:00": enc > H17, "encerrou depois de 17h01": enc > H17 + 60,
              "encerrou depois de 17h05": enc > H17 + 300, "encerrou depois de 17h15": enc > H1715,
              "teve voto depois de 17h": pl.col("n_pos17_2") > 0,
              "último voto depois de 17h15 (comparável 2022×2026)": pl.col("t_ult_voto_2") >= H1715}
    out = {"nota": "Em 2022 o log não registra 'Encerrar votação'; o encerramento usa 'Inicio do Encerramento' (~2 min depois). "
                   "Para comparar anos, use os cortes marcados como comparáveis (baseados no horário do último voto).",
           "secoes_com_log": d.height, "ufs": sorted(d["uf"].unique().to_list()),
           "margem_total_2t_mi": round(float((d["v13_2"] - d["v22_2"]).sum()) / 1e6, 3),
           "votos_apos_17h": int(d["n_pos17_2"].fill_null(0).sum())}
    for nome, cond in cortes.items():
        g = {}
        for flag, x in d.with_columns(cond.fill_null(False).alias("_g")).group_by("_g"):
            flag = flag[0] if isinstance(flag, tuple) else flag
            g["depois" if flag else "até"] = {
                "urnas": x.height, "votos_apos_17h": int(x["n_pos17_2"].fill_null(0).sum()),
                "margem_13_2t_mi": round(float((x["v13_2"] - x["v22_2"]).sum()) / 1e6, 3),
                "margem_13_1t_mi": round(float((x["v13_1"] - x["v22_1"]).sum()) / 1e6, 3),
                "pct13_2t": round(100 * float(x["v13_2"].sum() / (x["v13_2"] + x["v22_2"]).sum()), 2),
                "pct13_1t_entre_13_e_22": round(100 * float(x["v13_1"].sum() / (x["v13_1"] + x["v22_1"]).sum()), 2)}
        out[nome] = g
    # agrupando áreas inteiras (local / zona / município) que tiveram ALGUMA urna tardia: é assim que se chega
    # a números do tipo "Lula +6 mi nas áreas com urnas após 17h x Flávio +1,8 mi nas demais"
    areas = {}
    crit = {"alguma urna encerrou depois de 17h15": enc > H1715, "alguma urna teve voto depois de 17h": pl.col("n_pos17_2") > 0,
            "alguma urna teve voto depois de 17h15 (comparável 2022×2026)": pl.col("t_ult_voto_2") >= H1715}
    for cn, c in crit.items():
        x = d.with_columns(c.fill_null(False).alias("_f"))
        for nivel, ch in [("zona", ["uf", "nr_zona"]), ("município", ["uf", "cd_municipio"]),
                          ("local de votação", ["uf", "cd_municipio", "nr_zona", "nr_local"])]:
            g = x.with_columns(pl.col("_f").any().over(ch).alias("_g")).group_by("_g").agg(
                pl.len().alias("urnas"), ((pl.col("v13_2") - pl.col("v22_2")).sum() / 1e6).round(3).alias("m2"),
                ((pl.col("v13_1") - pl.col("v22_1")).sum() / 1e6).round(3).alias("m1"))
            areas[f"{cn} — por {nivel}"] = {("sim" if r["_g"] else "não"): {"urnas": r["urnas"], "margem_13_2t_mi": r["m2"],
                                                                            "margem_13_1t_mi": r["m1"]}
                                           for r in g.iter_rows(named=True)}
    out["agrupado_por_area"] = areas
    # por UF: onde estão as urnas "às 17h" (útil para entender de onde vem cada número)
    out["por_uf_encerrou_ate_17h01"] = {u: {"urnas": n, "margem_13_2t_mi": round(m / 1e6, 3)} for u, n, m in
        d.filter(enc <= H17 + 60).group_by("uf").agg(pl.len(), (pl.col("v13_2") - pl.col("v22_2")).sum())
         .sort("len", descending=True).iter_rows()}
    return out


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    ind = pl.read_parquet(PROC / "indicadores_2026.parquet")
    esc = pl.read_parquet(SAIDA / "escores_2026.parquet")
    e = eleitores(2026, 2, ind)
    R = {"ufs_com_log": sorted(e["uf"].unique().to_list())}

    # ---------- 1. classificação das urnas ----------
    sec = e.group_by(CHAVE).agg(
        pl.len().alias("n"), (pl.col("tb") >= H17).sum().alias("n_17"),
        (pl.col("tb") >= H1715).sum().alias("n_1715"), pl.col("tb").max().alias("ultimo"),
        pl.col("enc_b").first().alias("enc_b"),
        ((pl.col("tb") > pl.col("enc_b")) & pl.col("enc_b").is_not_null()).sum().alias("votos_apos_encerrar"))
    sec = sec.with_columns(pl.when(pl.col("n_1715") > 0).then(pl.lit("ESTENDIDA"))
                           .when(pl.col("n_17") > 0).then(pl.lit("FILA")).otherwise(pl.lit("NORMAL")).alias("grupo"))
    R["urnas_por_grupo"] = dict(sec.group_by("grupo").len().iter_rows())
    R["votos_por_grupo_apos_17h"] = dict(sec.group_by("grupo").agg(pl.col("n_17").sum()).iter_rows())
    R["votos_17h15_19h_total"] = int(sec["n_1715"].sum())
    R["votos_apos_19h"] = int(e.filter(pl.col("tb") >= H19).height)
    R["votos_apos_19h05"] = int(e.filter(pl.col("tb") >= H19 + 300).height)
    R["urnas_com_voto_apos_encerramento"] = int((sec["votos_apos_encerrar"] > 0).sum())
    est = sec.filter(pl.col("grupo") == "ESTENDIDA")
    R["estendidas_por_uf"] = dict(est.group_by("uf").len().sort("len", descending=True).iter_rows())
    R["estendidas_distribuicao_votos_1715"] = {
        "mediana": float(est["n_1715"].median()) if est.height else None,
        "p90": float(est["n_1715"].quantile(0.9)) if est.height else None,
        "max": int(est["n_1715"].max()) if est.height else None,
        "urnas_com_10+": int((est["n_1715"] >= 10).sum()), "urnas_com_30+": int((est["n_1715"] >= 30).sum())}
    R["horario_encerramento"] = {g: {"p50": float(x["enc_b"].median() / 3600) if x.height else None,
                                     "p99": float(x["enc_b"].quantile(0.99) / 3600) if x.height else None}
                                 for g, x in sec.group_by("grupo")}
    R["horario_encerramento"] = {str(k[0] if isinstance(k, tuple) else k): v for k, v in R["horario_encerramento"].items()}

    # ---------- 2. perfil dos votos 17h15-19h vs dia, dentro das urnas estendidas ----------
    ee = e.join(est.select(CHAVE), on=CHAVE)
    dia = ee.filter(pl.col("tb") < H17)
    tarde = ee.filter(pl.col("tb") >= H1715)
    def perfil(x):
        n = x.height
        return {"votos": n, "pct_sem_biometria_apos_falha": round(100 * float((x["bio"] == 0).mean()), 2) if n else None,
                "pct_sem_biometria_cadastrada": round(100 * float((x["bio"] == 2).mean()), 2) if n else None,
                "pct_mesario_habilitou": round(100 * float((x["mesa"] == 1).mean()), 2) if n else None,
                "duracao_mediana_voto_s": float(x["dur"].median()) if n else None,
                "intervalo_mediano_entre_eleitores_s": float(x["gap"].median()) if n else None,
                "pct_intervalo_menor_30s": round(100 * float((x["gap"] < 30).mean()), 2) if n else None}
    R["perfil_urnas_estendidas"] = {"8h-17h": perfil(dia), "17h15-19h": perfil(tarde)}
    if tarde.height and dia.height:
        k1, n1 = int((tarde["bio"] == 0).sum()), tarde.height
        k0, n0 = int((dia["bio"] == 0).sum()), dia.height
        R["perfil_urnas_estendidas"]["teste_sem_biometria_p"] = float(stats.fisher_exact([[k1, n1 - k1], [k0, n0 - k0]])[1])
        R["perfil_urnas_estendidas"]["teste_duracao_mannwhitney_p"] = float(
            stats.mannwhitneyu(tarde["dur"].to_numpy(), dia["dur"].to_numpy()).pvalue)
    # por urna: sem biometria na prorrogação vs dia (binomial), rajadas
    pu = ee.group_by(CHAVE).agg(
        (pl.col("tb") >= H1715).sum().alias("n_t"), ((pl.col("tb") >= H1715) & (pl.col("bio") == 0)).sum().alias("m_t"),
        (pl.col("tb") < H17).sum().alias("n_d"), ((pl.col("tb") < H17) & (pl.col("bio") == 0)).sum().alias("m_d"),
        ((pl.col("tb") >= H1715) & (pl.col("gap") < 30)).sum().alias("rajadas_t"),
        pl.col("dur").filter(pl.col("tb") >= H1715).median().alias("dur_t"),
        pl.col("dur").filter(pl.col("tb") < H17).median().alias("dur_d"))
    # contagens vêm como u32: converter antes de subtrair (m_t - 1 com m_t = 0 estourava para 4 bilhões)
    m_t, n_t = pu["m_t"].cast(pl.Int64).to_numpy(), pu["n_t"].cast(pl.Int64).to_numpy()
    p_d = np.clip(pu["m_d"].cast(pl.Int64).to_numpy() / np.maximum(pu["n_d"].cast(pl.Int64).to_numpy(), 1), 0.005, 0.995)
    pval = np.where(n_t >= 5, stats.binom.sf(m_t - 1, n_t, p_d), np.nan)  # com menos de 5 votos não há teste
    pu = pu.with_columns(pl.Series("p_sem_bio_prorrogacao", pval))
    R["urnas_estendidas_testaveis_5+_votos_prorrogacao"] = int(np.sum(n_t >= 5))
    R["urnas_estendidas_sem_biometria_anomala_p<0.001"] = int(np.nansum(pval < 0.001))
    R["urnas_estendidas_com_rajadas_5+"] = int((pu["rajadas_t"] >= 5).sum())

    # ---------- 3. resultado: desvio de votação das seções estendidas vs vizinhas ----------
    j = sec.join(esc.select(CHAVE + [c for c in ["z_A_voto", "z_B_abst", "z_B_branco", "z_B_nulo"] if c in esc.columns]), on=CHAVE, how="left") \
           .join(ind.select(CHAVE + ["p13_1", "p13_2", "p_abst_1", "p_abst_2", "aptos_2", "nm_municipio", "nm_local"]), on=CHAVE, how="left")
    # vizinhas = mesmas cidades onde houve urna estendida
    cidades = est.select("uf", "cd_municipio").unique()
    viz = j.join(cidades, on=["uf", "cd_municipio"])
    comp = {}
    for g, x in viz.group_by("grupo"):
        g = g[0] if isinstance(g, tuple) else g
        z = x["z_A_voto"].drop_nulls()
        comp[g] = {"secoes": x.height, "z_A_medio": round(float(z.mean()), 3) if len(z) else None,
                   "pct_z_A_forte": round(100 * float((z.abs() >= 4).mean()), 3) if len(z) else None,
                   "z_abst_medio": round(float(x["z_B_abst"].drop_nulls().mean()), 3) if "z_B_abst" in x.columns and x["z_B_abst"].drop_nulls().len() else None,
                   "delta_lula_medio_pp": round(100 * float((x["p13_2"] - x["p13_1"]).mean()), 2),
                   "delta_abstencao_media_pp": round(100 * float((x["p_abst_2"] - x["p_abst_1"]).mean()), 2)}
    R["resultado_mesmos_municipios"] = comp
    # dose-resposta: quanto maior a fração de votos na prorrogação, maior o desvio pró-13?
    jj = viz.filter(pl.col("z_A_voto").is_not_null()).with_columns((pl.col("n_1715") / pl.col("n")).alias("frac_1715"))
    if jj.height > 30:
        r = stats.spearmanr(jj["frac_1715"].to_numpy(), jj["z_A_voto"].to_numpy())
        R["correlacao_frac_votos_prorrogacao_x_desvio_voto"] = {"spearman": round(float(r.statistic), 4), "p": float(r.pvalue)}
        est_z = jj.filter(pl.col("grupo") == "ESTENDIDA")["z_A_voto"].to_numpy()
        out_z = jj.filter(pl.col("grupo") == "NORMAL")["z_A_voto"].to_numpy()
        if len(est_z) > 5:
            R["teste_z_A_estendida_vs_normal_mesmos_municipios"] = {
                "mannwhitney_p": float(stats.mannwhitneyu(est_z, out_z).pvalue),
                "mediana_estendida": round(float(np.median(est_z)), 3), "mediana_normal": round(float(np.median(out_z)), 3)}

    # ---------- 4. 1º turno das mesmas seções ----------
    if "n_pos17_1" in ind.columns:
        x = est.join(ind.select(CHAVE + ["n_pos17_1", "n_votos_1", "t_ult_voto_1"]), on=CHAVE, how="left")
        R["estendidas_no_1t"] = {"pct_votos_apos_17h_1t": round(100 * float(x["n_pos17_1"].sum() / max(x["n_votos_1"].sum(), 1)), 2),
                                 "ultimo_voto_mediano_1t_h": float(x["t_ult_voto_1"].median() / 3600) if x["t_ult_voto_1"].drop_nulls().len() else None}

    # ---------- 5. afirmação viral: margem por horário de encerramento da urna ----------
    R["divisao_por_encerramento"] = {str(a): divisao_encerramento(a) for a in (2026, 2022)}

    # ---------- 6. casos para conferência individual ----------
    verif = []
    x = ind.filter(pl.col("n_votos_2").is_not_null() & (pl.col("n_votos_2") != pl.col("comparecimento_2")))
    verif += [dict(zip(CHAVE, r[:4]), motivo=f"log com {r[4]} votos, BU com {r[5]} (contingência={r[6]}, origem={r[7]})")
              for r in x.select(CHAVE + ["n_votos_2", "comparecimento_2", "contingencia_2", "origem_voto_2"]).iter_rows()]
    x = sec.filter(pl.col("votos_apos_encerrar") > 0)
    verif += [dict(zip(CHAVE, r[:4]), motivo=f"{r[4]} voto(s) registrados depois do horário de encerramento do log")
              for r in x.select(CHAVE + ["votos_apos_encerrar"]).iter_rows()]
    x = e.filter(pl.col("tb") >= H19).group_by(CHAVE).agg(pl.len(), pl.col("tb").max())
    verif += [dict(zip(CHAVE, r[:4]), motivo=f"{r[4]} voto(s) depois de 19h (último às {r[5] // 3600}h{r[5] % 3600 // 60:02d}m{r[5] % 60:02d}s)")
              for r in x.iter_rows()]
    x = ind.filter(pl.col("t_encerra_b_2") < H17 - 60)
    verif += [dict(zip(CHAVE, r[:4]), motivo=f"encerramento registrado {(H17 - r[4]) / 60:.0f} min antes das 17h")
              for r in x.select(CHAVE + ["t_encerra_b_2"]).iter_rows()]
    x = ind.filter(pl.col("comparecimento_1") > pl.col("aptos_2") * 1.02)
    verif += [dict(zip(CHAVE, r[:4]), motivo=f"seção redesenhada? comparecimento 1T {r[4]} > aptos 2T {r[5]}")
              for r in x.select(CHAVE + ["comparecimento_1", "aptos_2"]).iter_rows()]
    R["encerramento_ate_17h00"] = {"exatamente_17h00m00s": int(ind.filter(pl.col("t_encerra_b_2") == H17).height),
                                   "1_a_60s_antes": int(ind.filter((pl.col("t_encerra_b_2") < H17) & (pl.col("t_encerra_b_2") >= H17 - 60)).height),
                                   "mais_de_1min_antes": int(ind.filter(pl.col("t_encerra_b_2") < H17 - 60).height)}
    vdf = pl.DataFrame(verif).join(ind.select(CHAVE + ["nm_municipio", "nm_local"]), on=CHAVE, how="left") if verif else pl.DataFrame()
    vdf.write_csv(SAIDA / "verificacao_individual_2026.csv", separator=";")
    R["verificacao_individual"] = {"total": vdf.height, "por_motivo": dict(pl.Series([categoria(v["motivo"]) for v in verif]).value_counts().iter_rows()) if verif else {},
                                   "lista": [{**v} for v in verif][:60]}

    # ---------- figuras ----------
    b = e.filter((pl.col("tb") >= 16 * 3600) & (pl.col("tb") < 19.5 * 3600)).with_columns((pl.col("tb") // 300 * 300).alias("b5"))
    cnt = b.group_by("b5").agg(pl.len(), (pl.col("bio") == 0).mean().alias("sem_bio")).sort("b5")
    fig, axs = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    x = cnt["b5"].to_numpy() / 3600
    axs[0].bar(x + 1 / 24, cnt["len"].to_numpy(), width=1 / 12 - 0.005, color=COR)
    axs[0].set_yscale("log"); axs[0].set_ylabel("votos / 5 min (log)")
    axs[0].set_title("Votos computados por 5 minutos — 2º turno 2026 (UFs processadas)", loc="left", fontsize=11)
    m = cnt["len"].to_numpy() >= 30
    axs[1].plot(x[m] + 1 / 24, 100 * cnt["sem_bio"].to_numpy()[m], color=COR, lw=2, marker="o", ms=4)
    axs[1].set_ylabel("% sem biometria"); axs[1].set_xlabel("horário de Brasília")
    axs[1].set_title("Votos habilitados sem biometria (blocos com 30+ votos)", loc="left", fontsize=11)
    for ax in axs:
        ax.axvline(17, color=TXT2, ls=":", lw=1); ax.axvline(19, color=TXT2, ls=":", lw=1)
    fig.tight_layout(); fig.savefig(FIG / "votos_16h_19h30.png", dpi=130); plt.close(fig)

    out = est.join(pu, on=CHAVE, how="left").join(j.select(CHAVE + [c for c in ["z_A_voto", "z_B_abst", "p13_1", "p13_2", "p_abst_1", "p_abst_2", "nm_municipio", "nm_local"] if c in j.columns]), on=CHAVE, how="left")
    out.sort("n_1715", descending=True).with_columns(
        (pl.col("ultimo") / 3600).round(3).alias("ultimo_voto_h"), (pl.col("enc_b") / 3600).round(3).alias("encerramento_h")
    ).write_csv(SAIDA / "pos17_secoes.csv", separator=";")
    (SAIDA / "pos17_resumo.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(R, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
