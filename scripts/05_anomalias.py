"""Testes estatísticos de anomalia por seção. Roda igual para 2026 e 2022 (linha de base).

Uso:  python -I scripts/05_anomalias.py [--anos 2026 2022]
Saídas (pasta saida/):
  secoes_sinalizadas_{ano}.csv  - seções com pelo menos um sinal forte, com os indicadores
  escores_{ano}.parquet         - z-scores de todas as seções
  resumo_{ano}.json             - contagens, assimetria de direção e testes agregados

Ideia geral: para cada indicador calcula-se um valor ESPERADO para a seção (a partir do 1º turno e
do comportamento das outras seções do mesmo município) e mede-se o desvio em unidades de erro
amostral (binomial), corrigido pela sobredispersão observada no país (z robusto). Assim seções
pequenas não aparecem como anômalas só por terem poucos eleitores.

Testes:
  A  votação Lula x Flávio no 2º turno vs. esperado pelo 1º turno (todos os candidatos)
  B  abstenção, brancos e nulos no 2º turno vs. esperado pelo 1º turno
  C  fluxo de eleitores depois das 17h (2º turno) vs. ritmo do dia e vs. 1º turno
  D  votos sem biometria: 2º vs 1º turno, e dentro do 2º turno por horário
  E  "impressão digital": as anomalias de A se correlacionam com votos tardios/sem biometria?
"""
import argparse
import json
from pathlib import Path

import numpy as np
import polars as pl
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "dados" / "processados"
SAIDA = RAIZ / "saida"
CHAVE = ["uf", "cd_municipio", "nr_zona", "nr_secao"]
Z_FORTE = 4.0       # |z| >= 4: ~1 em 16 mil seções por acaso, se a distribuição fosse normal
FDR_Q = 0.01
RE_INDIGENA = (r"IND[ÍI]GENA|ALDEIA|\bALD\.|\bTEKOA|TIKUNA|TICUNA|TUKUNA|TUCUNA|TENTENHAR|BACAJ[ÁA]|IÇANA|ICANA|"
               r"KRAH[ÔO]|KAIOW[ÁA]|PARESI|BORORO|APINAJ[ÉE]|XERENTE|KANAMARI|MARUBO|KULINA|KAXINAW[ÁA]|HUNI KUI|"
               r"ASHANINKA|YAWANAW[ÁA]|TAPIITAWA|TAPIRAP[ÉE]|KARIPUNA|GALIBI|PALIKUR|WAI ?WAI|TERRA IND|"
               r"YANOMAMI|XAVANTE|KAYAP[ÓO]|XIKRIN|GUARANI|"
               r"TENHARIM|TENHARINS|TERENA|MUNDURUKU|MAKUXI|MACUXI|WAPICHANA|SATER[ÉE]|BANIWA|"
               r"PATAX[ÓO]|POTIGUARA|KAINGANG|TUKANO|KOKAMA|KAMBEBA|TENTEHAR|GUAJAJARA|KARAJ[ÁA]")


def bh(p):
    """Benjamini-Hochberg: devolve máscara de rejeição a q=FDR_Q (NaN = não testado)."""
    p = np.asarray(p, dtype=float)
    ok = ~np.isnan(p)
    rej = np.zeros(len(p), dtype=bool)
    if ok.sum() == 0:
        return rej
    pv = p[ok]
    ordem = np.argsort(pv)
    m = len(pv)
    lim = FDR_Q * np.arange(1, m + 1) / m
    passa = pv[ordem] <= lim
    k = np.max(np.nonzero(passa)[0]) + 1 if passa.any() else 0
    r = np.zeros(m, dtype=bool)
    r[ordem[:k]] = True
    rej[ok] = r
    return rej


def demean(X, grupos):
    """Remove a média por grupo (efeito fixo de município)."""
    df = pl.DataFrame({"g": grupos}).with_row_index("i")
    out = np.empty_like(X)
    gid = df["g"].to_numpy()
    _, inv = np.unique(gid, return_inverse=True)
    cont = np.bincount(inv)
    for j in range(X.shape[1]):
        soma = np.bincount(inv, weights=X[:, j])
        out[:, j] = X[:, j] - (soma / cont)[inv]
    return out


def z_robusto(resid, sd):
    """Resíduo padronizado pelo erro binomial e reescalonado pela sobredispersão (MAD)."""
    raw = resid / sd
    med = np.nanmedian(raw)
    k = 1.4826 * np.nanmedian(np.abs(raw - med))
    return (raw - med) / k, float(k)


def logit(p):
    return np.log(p / (1 - p))


def spline(x, nos=5):
    """Base de spline cúbica (potências truncadas) com nós nos quantis de x."""
    q = np.quantile(x, np.linspace(0, 1, nos + 2)[1:-1])
    xs = (x - x.mean()) / x.std()
    qs = (q - x.mean()) / x.std()
    return np.column_stack([xs, xs ** 2, xs ** 3] + [np.clip(xs - c, 0, None) ** 3 for c in qs])


def regressao_fe(y, X, grupos, w=None):
    """OLS com efeito fixo de município (within). Devolve resíduos e R²."""
    Xd = demean(np.column_stack([X]), grupos)
    yd = demean(y.reshape(-1, 1), grupos).ravel()
    if w is not None:
        sw = np.sqrt(w)
        beta, *_ = np.linalg.lstsq(Xd * sw[:, None], yd * sw, rcond=None)
    else:
        beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
    res = yd - Xd @ beta
    r2 = 1 - np.sum(res ** 2) / np.sum((yd - yd.mean()) ** 2)
    return res, float(r2), beta


def teste_A(d, resumo):
    """Votação Lula (13) x Flávio/Bolsonaro (22) no 2º turno."""
    base = d.filter((pl.col("validos_1") >= 30) & (pl.col("validos_2") >= 30) & pl.col("secao_estavel"))
    pcols = sorted(c for c in base.columns if c.startswith("p") and c.endswith("_1")
                   and c[1:-2].isdigit())
    # candidatos com pouquíssimos votos juntam-se em "outros"
    tot = {c: base[c].mean() for c in pcols}
    principais = [c for c in pcols if tot[c] >= 0.003]
    outros = [c for c in pcols if c not in principais]
    feats = principais + ["p_abst_1", "p_branco_1", "p_nulo_1"]
    if outros:
        base = base.with_columns(pl.sum_horizontal(outros).alias("p_outros_1"))
        feats = feats + ["p_outros_1"]
    # Escala logit (lida com o "teto" em seções com 90%+ para um candidato) e splines na votação
    # de Lula e de Flávio no 1º turno; modelo estimado separadamente por UF (transferência de votos
    # dos candidatos eliminados varia por região), com efeito fixo de município.
    n = base["validos_2"].to_numpy().astype(float)
    y = logit((base["v13_2"].to_numpy() + 0.5) / (n + 1))
    l13 = logit((base["v13_1"].to_numpy() + 0.5) / (base["validos_1"].to_numpy() + 1))
    l22 = logit((base["v22_1"].to_numpy() + 0.5) / (base["validos_1"].to_numpy() + 1))
    X = np.column_stack([spline(l13), spline(l22), base.select(feats).fill_nan(0).fill_null(0).to_numpy()])
    ufs = base["uf"].to_numpy()
    grupos = {
        "município": base["cd_municipio"].to_numpy(),
        "zona": (base["uf"] + "_" + base["nr_zona"].cast(pl.Utf8)).to_numpy(),
        "local de votação": (base["cd_municipio"].cast(pl.Utf8) + "_" + base["nr_zona"].cast(pl.Utf8) + "_"
                             + base["nr_local"].cast(pl.Utf8)).to_numpy(),
    }

    def ajusta(Xm, ym, g, escala_logit=True):
        res = np.full(len(ym), np.nan)
        r2s = []
        for uf in np.unique(ufs):
            m = ufs == uf
            p0 = 1 / (1 + np.exp(-ym[m])) if escala_logit else np.clip(ym[m], 0.01, 0.99)
            res[m], r2_, _ = regressao_fe(ym[m], Xm[m], g[m], w=n[m] * p0 * (1 - p0) if escala_logit else n[m])
            r2s.append(r2_)
        if escala_logit:
            p_ = np.clip(1 / (1 + np.exp(-(ym - res))), 0.005, 0.995)
            raw_ = res * np.sqrt(n * p_ * (1 - p_))
        else:
            p_ = np.clip(ym - res, 0.005, 0.995)
            raw_ = res / np.sqrt(p_ * (1 - p_) / n)
        # calibra a escala por faixa (decil) da votação esperada: a dispersão real muda com o patamar
        faixa = np.digitize(p_, np.quantile(p_, np.linspace(0, 1, 11)[1:-1]))
        z_ = np.full(len(raw_), np.nan)
        ks_ = []
        for f in np.unique(faixa):
            mm = faixa == f
            z_[mm], kf = z_robusto(raw_[mm], 1.0)
            ks_.append(kf)
        return z_, float(np.median(r2s)), float(np.median(ks_))

    z, r2, k = ajusta(X, y, grupos["município"])
    # sensibilidade: o quanto contagem e direção dos casos fortes dependem da especificação
    sens = {}
    for nome, (zz, _, _) in {
            "logit+splines, por UF, efeito fixo de município (principal)": (z, r2, k),
            "logit+splines, por UF, efeito fixo de zona": ajusta(X, y, grupos["zona"]),
            "logit+splines, por UF, efeito fixo de local de votação": ajusta(X, y, grupos["local de votação"]),
            "linear simples nas proporções, efeito fixo de município": ajusta(
                base.select(feats).fill_nan(0).fill_null(0).to_numpy(), base["p13_2"].to_numpy(), grupos["município"], False),
    }.items():
        sens[nome] = {"n_forte": int(np.nansum(np.abs(zz) >= Z_FORTE)), "pro_13": int(np.nansum(zz >= Z_FORTE)),
                      "pro_22": int(np.nansum(zz <= -Z_FORTE))}
    resumo["A_sensibilidade"] = sens
    out = base.select(CHAVE).with_columns(pl.Series("z_A_voto", z, nan_to_null=True))
    forte = np.abs(z) >= Z_FORTE
    resumo["A_votacao"] = {
        "secoes_testadas": int(len(z)), "r2_modelo": round(r2, 4), "sobredispersao": round(k, 3),
        "variaveis_1t": feats + (["outros"] if outros else []),
        "n_forte": int(forte.sum()), "pct_forte": round(100 * forte.mean(), 4),
        "forte_pro_13": int((z >= Z_FORTE).sum()), "forte_pro_22": int((z <= -Z_FORTE).sum()),
        "n_abs_z_maior_6": int((np.abs(z) >= 6).sum()),
        "media_z": round(float(np.mean(z)), 4),
        "teste_simetria_binomial_p": float(stats.binomtest(
            int((z >= Z_FORTE).sum()), int(forte.sum()), 0.5).pvalue) if forte.sum() else None,
        "curtose": round(float(stats.kurtosis(z)), 3),
    }
    return out


def teste_B(d, resumo):
    """Abstenção, brancos e nulos: 2º turno vs. esperado pelo 1º."""
    outs = []
    for taxa, denom in [("p_abst", "aptos_2"), ("p_branco", "comparecimento_2"),
                        ("p_nulo", "comparecimento_2")]:
        base = d.filter((pl.col("aptos_2") >= 30) & (pl.col("comparecimento_2") >= 20) & pl.col("secao_estavel")
                        & (pl.col("aptos_1") >= 30) & (pl.col("comparecimento_1") >= 20)
                        & pl.col(f"{taxa}_1").is_not_null() & pl.col(f"{taxa}_2").is_not_null())
        xcols = list(dict.fromkeys([f"{taxa}_1", "p13_1", "p22_1", "p_abst_1"]))
        X = base.select(pl.col(xcols).fill_nan(0).fill_null(0)).to_numpy()
        y = base[f"{taxa}_2"].to_numpy()
        n = base[denom].to_numpy().astype(float)
        res, r2, _ = regressao_fe(y, X, base["cd_municipio"].to_numpy(), w=n)
        p = np.clip(y - res, 0.005, 0.995)
        z, k = z_robusto(res, np.sqrt(p * (1 - p) / n))
        outs.append(base.select(CHAVE).with_columns(pl.Series(f"z_B_{taxa[2:]}", z, nan_to_null=True)))
        resumo[f"B_{taxa[2:]}"] = {
            "secoes_testadas": int(len(z)), "r2_modelo": round(r2, 4),
            "sobredispersao": round(k, 3), "n_forte_alta": int((z >= Z_FORTE).sum()),
            "n_forte_baixa": int((z <= -Z_FORTE).sum()),
            "pct_forte": round(100 * float((np.abs(z) >= Z_FORTE).mean()), 4),
            "media_1t": round(float(base[f"{taxa}_1"].mean()), 5),
            "media_2t": round(float(base[f"{taxa}_2"].mean()), 5)}
    out = outs[0]
    for o in outs[1:]:
        out = out.join(o, on=CHAVE, how="full", coalesce=True)
    return out


def teste_C(d, resumo):
    """Fluxo depois das 17h (2º turno)."""
    if "n_pos17_2" not in d.columns:
        return None
    base = d.filter(pl.col("n_votos_2").is_not_null() & (pl.col("n_votos_2") >= 30))
    # C1: proporção de votos pós-17h no 2º turno vs. esperado (município + 1º turno da mesma seção)
    n2 = base["n_votos_2"].to_numpy().astype(float)
    k2 = base["n_pos17_2"].fill_null(0).to_numpy().astype(float)
    tem1 = "n_pos17_1" in base.columns
    k1 = base["n_pos17_1"].fill_null(0).to_numpy().astype(float) if tem1 else np.zeros_like(k2)
    n1 = base["n_votos_1"].fill_null(0).to_numpy().astype(float) if tem1 else np.ones_like(n2)
    mun = base.select(pl.col("n_pos17_2").fill_null(0).sum().over("cd_municipio")
                      / pl.col("n_votos_2").sum().over("cd_municipio")).to_numpy().ravel()
    # taxa esperada = média do município, ajustada (shrink) pelo histórico da seção no 1º turno
    esp = (k1 + 50 * mun) / (n1 + 50) if tem1 else mun
    esp = np.clip(esp, 1e-4, 0.5)
    lam = esp * n2
    # cauda superior de Poisson: P(X >= k2)
    p_c1 = stats.poisson.sf(k2 - 1, lam)
    # C2: ritmo após as 17h maior que o pico de qualquer hora do dia (com pelo menos 10 votos)
    raz = base["razao_taxa_pos17_pico_2"].to_numpy()
    c2 = (k2 >= 10) & (np.nan_to_num(raz) > 1.0)
    # C3: rajadas - votos com menos de 30s de intervalo depois das 17h
    raj = base["n_gap_lt30_pos17_2"].fill_null(0).to_numpy()
    rej = bh(p_c1)
    sig = rej & (k2 >= 10)
    out = base.select(CHAVE).with_columns(
        pl.Series("p_C_pos17", p_c1, nan_to_null=True), pl.Series("C_pos17_sig", sig, nan_to_null=True),
        pl.Series("C_ritmo_pos17_acima_pico", c2, nan_to_null=True), pl.Series("C_rajadas_pos17", raj, nan_to_null=True))
    def dist(col):
        s = d[col].drop_nulls()
        return {"total_votos_pos17": int(s.sum()), "secoes_com_pos17": int((s > 0).sum()),
                "secoes_ge10": int((s >= 10).sum()), "secoes_ge30": int((s >= 30).sum()),
                "max": int(s.max()) if len(s) else 0}
    resumo["C_fluxo_pos17"] = {
        "secoes_testadas": int(len(n2)),
        "pct_votos_pos17_2t": round(100 * k2.sum() / n2.sum(), 4),
        "pct_votos_pos17_1t": round(100 * k1.sum() / max(n1.sum(), 1), 4) if tem1 else None,
        "dist_2t": dist("n_pos17_2"), "dist_1t": dist("n_pos17_1") if tem1 else None,
        "n_sig_fdr_ge10": int(sig.sum()),
        "n_ritmo_pos17_acima_pico_dia": int(c2.sum()),
        "n_secoes_com_rajadas_pos17_ge5": int((raj >= 5).sum()),
        "mediana_intervalo_entre_votos_dia_s": float(d["gap_med_dia_2"].median()),
        "mediana_intervalo_entre_votos_pos17_s": float(d["gap_med_pos17_2"].median()),
        "votos_antes_8h": int(d.filter(pl.col("t_prim_voto_2") < 8 * 3600 - 300).height),
        "secoes_ultimo_voto_apos_19h": int(d.filter(pl.col("t_ult_voto_2") > 19 * 3600).height),
    }
    return out


def teste_D(d, resumo):
    """Votos sem biometria (habilitação manual após falha da digital)."""
    if "manual_dia_2" not in d.columns:
        return None
    base = d.filter(pl.col("n_votos_2").is_not_null() & (pl.col("n_votos_2") >= 30))
    m2 = (base["manual_dia_2"].fill_null(0) + base["manual_pos17_2"].fill_null(0)).to_numpy().astype(float)
    n2 = base["n_votos_2"].to_numpy().astype(float)
    res = {}
    out = base.select(CHAVE)
    # D1: 2º vs 1º turno na mesma seção
    if "manual_dia_1" in base.columns:
        ok = (base["n_votos_1"].is_not_null().to_numpy() & (base["n_votos_1"].fill_null(0).to_numpy() >= 30)
              & base["secao_estavel"].to_numpy())
        m1 = (base["manual_dia_1"].fill_null(0) + base["manual_pos17_1"].fill_null(0)).to_numpy().astype(float)
        n1 = base["n_votos_1"].fill_null(1).to_numpy().astype(float)
        dlt = m2 / n2 - m1 / n1
        # remove a variação média do município (ex.: leitor de biometria trocado na zona)
        dmun = pl.DataFrame({"g": base["cd_municipio"], "x": dlt}).select(
            pl.col("x").median().over("g")).to_numpy().ravel()
        pp = (m1 + m2) / (n1 + n2)
        sd = np.sqrt(np.clip(pp * (1 - pp), 1e-4, None) * (1 / n1 + 1 / n2))
        z = np.where(ok, (dlt - dmun) / sd, np.nan)
        z, k = z_robusto(z, 1.0)
        out = out.with_columns(pl.Series("z_D_manual_entre_turnos", z, nan_to_null=True))
        res["D1_entre_turnos"] = {
            "secoes_testadas": int(ok.sum()), "sobredispersao": round(k, 3),
            "pct_manual_1t": round(100 * float(np.nansum(m1[ok]) / np.nansum(n1[ok])), 3),
            "pct_manual_2t": round(100 * float(m2.sum() / n2.sum()), 3),
            "n_forte_aumento": int(np.nansum(z >= Z_FORTE)),
            "n_forte_queda": int(np.nansum(z <= -Z_FORTE))}
    # D2: dentro do 2º turno, última hora (16h-17h) e pós-17h vs. resto do dia
    mt = base["manual_16h_2"].fill_null(0).to_numpy().astype(float) + base["manual_pos17_2"].fill_null(0).to_numpy()
    nt = base["n_16h_2"].fill_null(0).to_numpy().astype(float) + base["n_pos17_2"].fill_null(0).to_numpy()
    p_resto = np.clip((m2 - mt) / np.maximum(n2 - nt, 1), 1e-3, 0.999)
    p_d2 = np.where(nt >= 10, stats.binom.sf(mt - 1, nt, p_resto), np.nan)
    sig = bh(p_d2)
    out = out.with_columns(pl.Series("p_D_manual_fim_dia", p_d2, nan_to_null=True), pl.Series("D_manual_fim_dia_sig", sig, nan_to_null=True))
    res["D2_fim_do_dia"] = {
        "secoes_testadas": int(np.sum(~np.isnan(p_d2))),
        "pct_manual_ate16h": round(100 * float((m2 - mt).sum() / (n2 - nt).sum()), 3),
        "pct_manual_16h_em_diante": round(100 * float(mt.sum() / max(nt.sum(), 1)), 3),
        "n_sig_fdr": int(sig.sum())}
    res["secoes_pct_manual_2t_acima_30"] = int((m2 / n2 > 0.30).sum())
    res["secoes_pct_manual_2t_acima_50"] = int((m2 / n2 > 0.50).sum())
    resumo["D_biometria"] = res
    return out


def teste_E(d, esc, resumo):
    """Correlação entre desvio de votação (A) e votos tardios/sem biometria."""
    cols = [c for c in ["d_pct_manual", "pct_pos17_2", "d_p_abst"] if c in d.columns]
    if "z_A_voto" not in esc.columns or len(cols) < 2:
        return
    j = d.join(esc.select(CHAVE + ["z_A_voto"]), on=CHAVE).drop_nulls(cols + ["z_A_voto"])
    if j.height < 1000:
        return
    X = j.select(cols).to_numpy()
    X = (X - X.mean(0)) / X.std(0)
    y = j["z_A_voto"].to_numpy()
    _, r2, beta = regressao_fe(y, X, j["cd_municipio"].to_numpy())
    resumo["E_impressao_digital"] = {
        "secoes": j.height,
        "nota": "coeficiente = variação do z_A (pró-Lula > 0) para +1 desvio-padrão do indicador; "
                "efeito fixo de município",
        "coeficientes": {c: round(float(b), 4) for c, b in zip(cols, beta)},
        "correlacoes_simples": {c: round(float(np.corrcoef(j[c].to_numpy(), y)[0, 1]), 4)
                                for c in cols}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs="+", default=["2026", "2022"])
    a = ap.parse_args()
    SAIDA.mkdir(exist_ok=True)
    for ano in a.anos:
        d = pl.read_parquet(PROC / f"indicadores_{ano}.parquet")
        # contexto: locais de votação em aldeias/escolas indígenas (voto em bloco é comum)
        d = d.with_columns(pl.col("nm_local").str.to_uppercase()
                           .str.contains(RE_INDIGENA).fill_null(False).alias("local_indigena"))
        # seção "estável" entre turnos: mesmo eleitorado (exclui seções redesenhadas/agregadas entre turnos)
        d = d.with_columns(((pl.col("aptos_1") > 0) & ((pl.col("aptos_2") - pl.col("aptos_1")).abs() <= 0.02 * pl.col("aptos_1"))
                            & (pl.col("comparecimento_1") <= 1.02 * pl.col("aptos_2"))).fill_null(False).alias("secao_estavel"))
        resumo = {"ano": int(ano), "secoes": d.height, "secoes_instaveis_excluidas_A_B_D1": int((~d["secao_estavel"]).sum()),
                  "secoes_com_log_2t": int(d["n_votos_2"].is_not_null().sum()) if "n_votos_2" in d.columns else 0,
                  "secoes_com_log_1t": int(d["n_votos_1"].is_not_null().sum()) if "n_votos_1" in d.columns else 0}
        # integridade: votos no log x comparecimento no boletim
        for t in (1, 2):
            if f"n_votos_{t}" in d.columns:
                x = d.filter(pl.col(f"n_votos_{t}").is_not_null())
                diverg = x.filter(pl.col(f"n_votos_{t}") != pl.col(f"comparecimento_{t}"))
                resumo[f"integridade_{t}t"] = {
                    "secoes_comparadas": x.height, "secoes_log_diferente_do_bu": diverg.height,
                    "soma_diferencas": int((diverg[f"n_votos_{t}"] - diverg[f"comparecimento_{t}"]).sum())}
        esc = d.select(CHAVE)
        for f in (teste_A, teste_B, teste_C, teste_D):
            o = f(d, resumo)
            if o is not None:
                esc = esc.join(o, on=CHAVE, how="left")
        teste_E(d, esc, resumo)

        # sinal forte por seção
        motivos = []
        if "z_A_voto" in esc.columns:
            motivos += [(pl.col("z_A_voto") >= Z_FORTE, "voto 2T muito acima do esperado p/ Lula"),
                        (pl.col("z_A_voto") <= -Z_FORTE, "voto 2T muito acima do esperado p/ Flávio")]
        for t in ("abst", "branco", "nulo"):
            if f"z_B_{t}" in esc.columns:
                motivos += [(pl.col(f"z_B_{t}").abs() >= Z_FORTE, f"{t} 2T fora do esperado")]
        if "C_pos17_sig" in esc.columns:
            motivos += [(pl.col("C_pos17_sig"), "excesso de votos após 17h"),
                        (pl.col("C_ritmo_pos17_acima_pico"), "ritmo após 17h acima do pico do dia"),
                        (pl.col("C_rajadas_pos17") >= 5, "rajada de votos <30s após 17h")]
        if "z_D_manual_entre_turnos" in esc.columns:
            motivos += [(pl.col("z_D_manual_entre_turnos") >= Z_FORTE, "salto de votos sem biometria vs 1T")]
        if "D_manual_fim_dia_sig" in esc.columns:
            motivos += [(pl.col("D_manual_fim_dia_sig"), "sem biometria concentrado no fim do dia")]
        esc = esc.with_columns([m.fill_null(False).alias(f"_m{i}") for i, (m, _) in enumerate(motivos)])
        mcols = [f"_m{i}" for i in range(len(motivos))]
        esc = esc.with_columns(pl.sum_horizontal(mcols).alias("n_sinais"),
                               pl.concat_str([pl.when(pl.col(c)).then(pl.lit(txt + "; ")).otherwise(pl.lit(""))
                                              for c, (_, txt) in zip(mcols, motivos)]).alias("motivos"))
        resumo["sinais_por_motivo"] = {txt: int(esc[c].sum()) for c, (_, txt) in zip(mcols, motivos)}
        resumo["secoes_com_1_sinal"] = int((esc["n_sinais"] == 1).sum())
        resumo["secoes_com_2+_sinais"] = int((esc["n_sinais"] >= 2).sum())
        resumo["secoes_com_3+_sinais"] = int((esc["n_sinais"] >= 3).sum())
        esc = esc.drop(mcols)
        esc.write_parquet(SAIDA / f"escores_{ano}.parquet")

        if "z_A_voto" in esc.columns:
            ja = esc.join(d.select(CHAVE + ["local_indigena"]), on=CHAVE).filter(pl.col("z_A_voto").abs() >= Z_FORTE)
            resumo["A_votacao"]["forte_em_local_indigena"] = int(ja["local_indigena"].sum())
            resumo["A_votacao"]["pct_secoes_pais_em_local_indigena"] = round(100 * float(d["local_indigena"].mean()), 3)
            sem = ja.filter(~pl.col("local_indigena"))
            resumo["A_votacao"]["fora_indigena_pro_13"] = int((sem["z_A_voto"] > 0).sum())
            resumo["A_votacao"]["fora_indigena_pro_22"] = int((sem["z_A_voto"] < 0).sum())
        mostrar = [c for c in [
            "nm_municipio", "nm_local", "local_indigena", "aptos_2", "comparecimento_1", "comparecimento_2",
            "p13_1", "p22_1", "p13_2", "p22_2", "p_abst_1", "p_abst_2", "p_branco_1", "p_branco_2",
            "p_nulo_1", "p_nulo_2", "n_votos_2", "n_pos17_1", "n_pos17_2", "taxa_dia_2", "taxa_pos17_2",
            "pico_hora_dia_2", "pct_manual_1", "pct_manual_2", "pct_manual_dia_2",
            "pct_manual_pos17_2", "pct_semcad_2", "contingencia_2", "n_suspensa_2",
            "t_abre_b_2", "t_encerra_b_2", "modelo_urna_2"] if c in d.columns]
        sinal = esc.filter(pl.col("n_sinais") > 0).join(d.select(CHAVE + mostrar), on=CHAVE) \
                   .sort(["n_sinais", "z_A_voto"] if "z_A_voto" in esc.columns else ["n_sinais"],
                         descending=True, nulls_last=True)
        sinal.write_csv(SAIDA / f"secoes_sinalizadas_{ano}.csv", separator=";")
        with open(SAIDA / f"resumo_{ano}.json", "w", encoding="utf-8") as f:
            json.dump(resumo, f, ensure_ascii=False, indent=2)
        print(json.dumps(resumo, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
