"""Gera relatório HTML (saida/relatorio.html) comparando 2026 com a linha de base de 2022.

Uso:  python -I scripts/06_relatorio.py
Requer: saida/resumo_{ano}.json, saida/escores_{ano}.parquet, dados/processados/indicadores_{ano}.parquet
"""
import base64
import html
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "dados" / "processados"
SAIDA = RAIZ / "saida"
CHAVE = ["uf", "cd_municipio", "nr_zona", "nr_secao"]

# paleta de referência (validada): slot 1 azul = 2026, slot 2 laranja = 2022
COR = {2026: "#2a78d6", 2022: "#eb6834"}
TXT, TXT2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SEQ = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "axes.edgecolor": GRADE,
    "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2, "text.color": TXT,
    "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "font.size": 10, "legend.frameon": False})


def fig_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def carrega(ano):
    r = json.loads((SAIDA / f"resumo_{ano}.json").read_text(encoding="utf-8"))
    e = pl.read_parquet(SAIDA / f"escores_{ano}.parquet")
    d = pl.read_parquet(PROC / f"indicadores_{ano}.parquet")
    return r, e, d


def g_hist_z(E):
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    bins = np.linspace(-12, 12, 97)
    for ano, e in E.items():
        z = e["z_A_voto"].drop_nulls().to_numpy()
        h, _ = np.histogram(np.clip(z, -12, 12), bins=bins)
        ax.step(bins[:-1], np.maximum(h / len(z), 1e-7), where="post", color=COR[ano], lw=2, label=str(ano))
    ax.set_yscale("log")
    ax.axvline(4, color=TXT2, lw=1, ls=":")
    ax.axvline(-4, color=TXT2, lw=1, ls=":")
    ax.set_xlabel("z do desvio de votação no 2º turno  (← pró-22   |   pró-13 →)")
    ax.set_ylabel("fração das seções (log)")
    ax.legend(title="Eleição")
    ax.set_title("Distribuição do desvio de votação por seção (teste A)", loc="left", fontsize=11)
    return fig_b64(fig)


def g_sinais(R):
    motivos = list(dict.fromkeys(m for r in R.values() for m in r.get("sinais_por_motivo", {})))
    fig, ax = plt.subplots(figsize=(7.5, 0.42 * len(motivos) + 1))
    y = np.arange(len(motivos))
    h = 0.38
    for i, (ano, r) in enumerate(sorted(R.items(), reverse=True)):
        n = r["secoes"]
        vals = [100 * r.get("sinais_por_motivo", {}).get(m, np.nan) / n for m in motivos]
        ax.barh(y + (i - 0.5) * h, vals, height=h - 0.04, color=COR[ano], label=str(ano))
    ax.set_yticks(y, motivos)
    ax.invert_yaxis()
    ax.set_xlabel("% das seções com sinal forte")
    ax.legend(title="Eleição")
    ax.set_title("Sinais fortes por tipo de teste (mesma metodologia nos dois anos)", loc="left", fontsize=11)
    return fig_b64(fig)


def curva(ano, turno):
    p = PROC / f"curva_horaria_{ano}_{turno}t.parquet"
    if not p.exists():
        return None
    c = pl.read_parquet(p).filter((pl.col("t15") >= 7 * 3600) & (pl.col("t15") < 19 * 3600))
    return c.group_by("t15").agg(pl.col("len").sum().alias("n"),
                                 pl.col("len").filter(pl.col("bio") == 0).sum().alias("manual")).sort("t15")


def g_curvas(turno=2):
    C = {a: curva(a, turno) for a in (2026, 2022)}
    C = {a: c for a, c in C.items() if c is not None}
    if not C:
        return None, None
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    for a, c in C.items():
        x = c["t15"].to_numpy() / 3600
        ax.plot(x, 100 * c["n"].to_numpy() / c["n"].sum(), color=COR[a], lw=2, label=str(a))
    ax.axvline(17, color=TXT2, lw=1, ls=":")
    ax.set_xlabel("horário de Brasília")
    ax.set_ylabel("% dos votos do dia (blocos de 15 min)")
    ax.legend(title="Eleição")
    ax.set_title(f"Ritmo de votação ao longo do dia — {turno}º turno", loc="left", fontsize=11)
    f1 = fig_b64(fig)
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    for a, c in C.items():
        c = c.filter(pl.col("n") >= 500)
        ax.plot(c["t15"].to_numpy() / 3600, 100 * (c["manual"] / c["n"]).to_numpy(), color=COR[a], lw=2, label=str(a))
    ax.axvline(17, color=TXT2, lw=1, ls=":")
    ax.set_xlabel("horário de Brasília")
    ax.set_ylabel("% dos votos sem biometria")
    ax.legend(title="Eleição")
    ax.set_title(f"Votos habilitados sem biometria (após falha da digital) — {turno}º turno", loc="left", fontsize=11)
    return f1, fig_b64(fig)


def g_fingerprint(D):
    fig, axs = plt.subplots(1, len(D), figsize=(4 * len(D), 3.8), sharey=True)
    axs = np.atleast_1d(axs)
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(SEQ)
    for ax, (a, d) in zip(axs, sorted(D.items(), reverse=True)):
        x = (d["comparecimento_2"] / d["aptos_2"]).to_numpy()
        y = d["p13_2"].to_numpy()
        ok = np.isfinite(x) & np.isfinite(y) & (d["aptos_2"].to_numpy() >= 50)
        h, xe, ye = np.histogram2d(x[ok], y[ok], bins=80, range=[[0.3, 1.0], [0, 1]])
        ax.pcolormesh(xe, ye, np.log1p(h).T, cmap=cmap, shading="auto")
        ax.set_title(str(a), loc="left", fontsize=11)
        ax.set_xlabel("comparecimento (2º turno)")
        ax.grid(False)
    axs[0].set_ylabel("% de votos válidos para Lula (13)")
    fig.suptitle("“Impressão digital” eleitoral: comparecimento × votação por seção", x=0.02, ha="left", fontsize=11)
    return fig_b64(fig)


def linha(nome, v26, v22, fmt="{:,}"):
    def f(v):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return "—"
        return fmt.format(v).replace(",", ".") if isinstance(v, int) else fmt.format(v)
    return f"<tr><td>{html.escape(nome)}</td><td>{f(v26)}</td><td>{f(v22)}</td></tr>"


def g(r, *ks):
    for k in ks:
        if not isinstance(r, dict) or k not in r:
            return None
        r = r[k]
    return r


def main():
    R, E, D = {}, {}, {}
    for a in (2026, 2022):
        if (SAIDA / f"resumo_{a}.json").exists():
            R[a], E[a], D[a] = carrega(a)
    r26, r22 = R.get(2026, {}), R.get(2022, {})
    imgs = {"z": g_hist_z(E), "sinais": g_sinais(R), "fp": g_fingerprint(D)}
    imgs["ritmo"], imgs["bio"] = g_curvas(2)

    T = [linha("Seções no 2º turno", r26.get("secoes"), r22.get("secoes")),
         linha("Seções com log do 2º turno processado", r26.get("secoes_com_log_2t"), r22.get("secoes_com_log_2t")),
         linha("Seções onde nº de votos no log ≠ comparecimento do BU (2º turno)",
               g(r26, "integridade_2t", "secoes_log_diferente_do_bu"), g(r22, "integridade_2t", "secoes_log_diferente_do_bu")),
         linha("A · seções com desvio forte de votação (|z|≥4)", g(r26, "A_votacao", "n_forte"), g(r22, "A_votacao", "n_forte")),
         linha("   … a favor do 13", g(r26, "A_votacao", "forte_pro_13"), g(r22, "A_votacao", "forte_pro_13")),
         linha("   … a favor do 22", g(r26, "A_votacao", "forte_pro_22"), g(r22, "A_votacao", "forte_pro_22")),
         linha("   … em local de votação indígena", g(r26, "A_votacao", "forte_em_local_indigena"), g(r22, "A_votacao", "forte_em_local_indigena")),
         linha("B · abstenção fora do esperado", g(r26, "sinais_por_motivo", "abst 2T fora do esperado"), g(r22, "sinais_por_motivo", "abst 2T fora do esperado")),
         linha("B · brancos fora do esperado", g(r26, "sinais_por_motivo", "branco 2T fora do esperado"), g(r22, "sinais_por_motivo", "branco 2T fora do esperado")),
         linha("B · nulos fora do esperado", g(r26, "sinais_por_motivo", "nulo 2T fora do esperado"), g(r22, "sinais_por_motivo", "nulo 2T fora do esperado")),
         linha("C · % dos votos após 17h (2º turno)", g(r26, "C_fluxo_pos17", "pct_votos_pos17_2t"), g(r22, "C_fluxo_pos17", "pct_votos_pos17_2t"), "{:.3f}%"),
         linha("C · % dos votos após 17h (1º turno)", g(r26, "C_fluxo_pos17", "pct_votos_pos17_1t"), g(r22, "C_fluxo_pos17", "pct_votos_pos17_1t"), "{:.3f}%"),
         linha("C · seções com excesso significativo de votos após 17h", g(r26, "C_fluxo_pos17", "n_sig_fdr_ge10"), g(r22, "C_fluxo_pos17", "n_sig_fdr_ge10")),
         linha("C · seções com ritmo após 17h acima do pico do dia", g(r26, "C_fluxo_pos17", "n_ritmo_pos17_acima_pico_dia"), g(r22, "C_fluxo_pos17", "n_ritmo_pos17_acima_pico_dia")),
         linha("D · % votos sem biometria, 1º turno", g(r26, "D_biometria", "D1_entre_turnos", "pct_manual_1t"), g(r22, "D_biometria", "D1_entre_turnos", "pct_manual_1t"), "{:.2f}%"),
         linha("D · % votos sem biometria, 2º turno", g(r26, "D_biometria", "D1_entre_turnos", "pct_manual_2t"), g(r22, "D_biometria", "D1_entre_turnos", "pct_manual_2t"), "{:.2f}%"),
         linha("D · seções com salto forte de votos sem biometria vs 1º turno", g(r26, "D_biometria", "D1_entre_turnos", "n_forte_aumento"), g(r22, "D_biometria", "D1_entre_turnos", "n_forte_aumento")),
         linha("D · seções com votos sem biometria concentrados no fim do dia", g(r26, "D_biometria", "D2_fim_do_dia", "n_sig_fdr"), g(r22, "D_biometria", "D2_fim_do_dia", "n_sig_fdr")),
         linha("Seções com 2+ sinais simultâneos", r26.get("secoes_com_2+_sinais"), r22.get("secoes_com_2+_sinais")),
         linha("Seções com 3+ sinais simultâneos", r26.get("secoes_com_3+_sinais"), r22.get("secoes_com_3+_sinais")),
         ]

    top = ""
    p = SAIDA / "secoes_sinalizadas_2026.csv"
    if p.exists():
        s = pl.read_csv(p, separator=";", infer_schema_length=10000)
        s = s.with_columns(pl.col("z_A_voto").abs().alias("_az")).sort(["n_sinais", "_az"], descending=True, nulls_last=True).head(60)
        cols = [c for c in ["uf", "nm_municipio", "nr_zona", "nr_secao", "n_sinais", "z_A_voto", "p13_1", "p13_2",
                            "p_abst_1", "p_abst_2", "n_pos17_2", "pct_manual_1", "pct_manual_2",
                            "local_indigena", "motivos"] if c in s.columns]
        cab = "".join(f"<th>{c}</th>" for c in cols)
        lin = []
        for row in s.select(cols).iter_rows():
            cel = []
            for c, v in zip(cols, row):
                if isinstance(v, float):
                    v = f"{v:.1f}" if c.startswith("z_") else (f"{100 * v:.1f}%" if c.startswith("p") else f"{v:.2f}")
                cel.append(f"<td>{html.escape('' if v is None else str(v))}</td>")
            lin.append("<tr>" + "".join(cel) + "</tr>")
        top = f"<table class='t'><tr>{cab}</tr>{''.join(lin)}</table>"

    img = lambda k: f"<img src='data:image/png;base64,{imgs[k]}'>" if imgs.get(k) else "<p><i>(sem dados de log ainda)</i></p>"
    analise_ia = ""
    if (SAIDA / "analise_ia.md").exists():
        analise_ia = ("<h2>Leitura crítica (IA)</h2><pre class='ia'>"
                      + html.escape((SAIDA / "analise_ia.md").read_text(encoding="utf-8")) + "</pre>")
    extra = ""
    if (SAIDA / "checagem_fragmento.html").exists():
        extra = ("<h1 style='margin-top:2.5em'>Análises adicionais: checagem de afirmações, parada da apuração e urnas de 17h–19h</h1>"
                 + (SAIDA / "checagem_fragmento.html").read_text(encoding="utf-8"))
    doc = f"""<!doctype html><html lang="pt-br"><meta charset="utf-8">
<title>Inconsistências estatísticas por seção — Presidente 2026</title>
<style>
body{{font-family:system-ui,Segoe UI,sans-serif;max-width:1000px;margin:2em auto;padding:0 1em;color:{TXT};background:{FUNDO};line-height:1.5}}
h1{{font-size:1.5em}} h2{{font-size:1.2em;margin-top:2em;border-bottom:1px solid {GRADE}}}
.t{{border-collapse:collapse;font-size:.82em;width:100%}} .t td,.t th{{border-bottom:1px solid {GRADE};padding:3px 6px;text-align:left}}
.t th{{color:{TXT2};font-weight:600}} img{{max-width:100%}} .nota{{color:{TXT2};font-size:.9em}}
.ficha{{border:1px solid {GRADE};border-radius:8px;padding:.9em 1em;margin:1.1em 0;background:#fff}}
.af{{font-weight:600}} .n{{display:inline-block;min-width:1.6em;color:{TXT2}}}
.ver{{display:inline-block;margin:.5em 0;padding:2px 10px;border-radius:4px;font-size:.8em;font-weight:700;color:{TXT}}}
pre.ia{{white-space:pre-wrap;font-family:inherit;background:#f3f2ef;padding:1em;border-radius:6px}}
</style>
<h1>Inconsistências estatísticas por seção — eleição presidencial 2026</h1>
<p class="nota">Fontes: TSE (resultados por seção e arquivos de log de todas as urnas, 1º e 2º turno). Linha de base: eleição de 2022,
com a mesma metodologia. Um sinal estatístico é um <b>indício para verificação</b>, não prova de fraude: com ~500 mil seções,
centenas de casos extremos são esperados por acaso e por fatores locais. O que importa é (1) se 2026 difere de 2022 e
(2) se os sinais diferentes convergem nas mesmas seções e na mesma direção.</p>
<h2>Resumo: 2026 vs 2022</h2>
<table class="t"><tr><th>Indicador</th><th>2026</th><th>2022</th></tr>{''.join(T)}</table>
{analise_ia}
<h2>Sinais por teste</h2>{img('sinais')}
<h2>A · Votação no 2º turno vs. esperado pelo 1º turno</h2>
<p class="nota">Modelo por UF, em escala logit, com splines na votação de Lula e de Flávio/Bolsonaro no 1º turno, demais candidatos,
abstenção/brancos/nulos e efeito fixo de município. z = desvio em unidades de erro amostral, calibrado pela dispersão observada.</p>
{img('z')}
{img('fp')}
<h2>C · Ritmo de votação e votos após as 17h</h2>{img('ritmo')}
<h2>D · Votos sem biometria ao longo do dia</h2>{img('bio')}
<h2>Seções com mais sinais (2026)</h2>
<p class="nota">Lista completa: saida/secoes_sinalizadas_2026.csv. p13 = % de votos válidos para Lula; abst = abstenção;
n_pos17 = votos após 17h; pct_manual = % de eleitores habilitados sem biometria após falha da digital.</p>
{top}
{extra}
<h2>Metodologia</h2>
<ul class="nota">
<li>Logs: cada voto computado é lido do log da urna (horário, tipo de habilitação). A contagem do log foi conferida com o comparecimento do boletim de urna em todas as seções.</li>
<li>Horário de Brasília: o relógio da urna é local; a diferença é estimada por município pela hora de abertura.</li>
<li>Sem biometria = habilitação manual (dado pessoal ou digital do mesário) após falha da digital. Eleitores sem biometria cadastrada são contados à parte.</li>
<li>Testes de contagem (C, D) usam Poisson/binomial com correção de Benjamini-Hochberg (FDR 1%).</li>
<li>Locais indígenas identificados pelo nome do local de votação (aldeia, escola indígena, etnias).</li>
</ul>
</html>"""
    (SAIDA / "relatorio.html").write_text(doc, encoding="utf-8")
    print("relatório:", SAIDA / "relatorio.html")


if __name__ == "__main__":
    main()
