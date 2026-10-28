"""Relatório de checagem (saida/checagem.html) a partir de saida/checagem_dados.json (gerado por 08_checagem.py).

Uso:  python -I scripts/09_checagem_html.py
"""
import base64
import html
import json
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
ODS = RAIZ / "dados" / "brutos" / "odsele"
COR = {2026: "#2a78d6", 2022: "#eb6834"}
TXT, TXT2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": FUNDO, "axes.facecolor": FUNDO, "axes.edgecolor": GRADE,
                     "axes.labelcolor": TXT2, "xtick.color": TXT2, "ytick.color": TXT2,
                     "axes.grid": True, "grid.color": GRADE, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "font.size": 10})

VEREDITO = {  # rótulo -> cor de fundo (texto sempre escuro; o rótulo escrito carrega o significado)
    "CONFIRMADO": "#d5ecd5", "PARCIALMENTE CORRETO": "#fbeccb", "EXAGERADO / ENGANOSO": "#fbeccb",
    "INCORRETO": "#f6d3d3", "NÃO VERIFICÁVEL COM ESTES DADOS": "#e8e7e3", "SEM ANOMALIA DETECTADA": "#d5ecd5",
}


def b64(path_or_fig):
    import io
    buf = io.BytesIO()
    path_or_fig.savefig(buf, format="png", dpi=130, bbox_inches="tight")
    plt.close(path_or_fig)
    return base64.b64encode(buf.getvalue()).decode()


def fig_recebimento():
    """BUs recebidos por bloco de 10 minutos, três eleições em painéis separados (mesma escala)."""
    series = []
    for ano, t in ((2026, 2), (2026, 1), (2022, 2)):
        with zipfile.ZipFile(ODS / f"detalhe_votacao_secao_{ano}.zip") as z:
            d = pl.read_csv(z.read(f"detalhe_votacao_secao_{ano}_BR.csv"), separator=";", encoding="latin1",
                            columns=["NR_TURNO", "CD_CARGO", "DT_RECEBIMENTO_BU_HOR_TSE"], infer_schema_length=0)
        d = d.filter((pl.col("NR_TURNO") == str(t)) & (pl.col("CD_CARGO") == "1"))
        h = d["DT_RECEBIMENTO_BU_HOR_TSE"].str.slice(11, 2).cast(pl.Int32, strict=False)
        mi = d["DT_RECEBIMENTO_BU_HOR_TSE"].str.slice(14, 1).cast(pl.Int32, strict=False)
        x = (h + mi / 6).filter((h >= 17) & (h < 23))
        series.append((f"{ano} — {t}º turno", COR[ano], x.value_counts().sort(x.name)))
    fig, axs = plt.subplots(3, 1, figsize=(8, 6.2), sharex=True, sharey=True)
    for ax, (nome, cor, vc) in zip(axs, series):
        ax.bar(vc[vc.columns[0]].to_numpy() + 1 / 12, vc["count"].to_numpy(), width=1 / 6 - 0.012, color=cor)
        ax.set_title(nome, loc="left", fontsize=10)
        ax.set_ylabel("BUs / 10 min")
    axs[-1].set_xlabel("horário de Brasília")
    axs[-1].set_xticks(range(17, 24))
    fig.suptitle("Boletins de urna recebidos pelo TSE a cada 10 minutos", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    return b64(fig)


def fig_ufs(e26):
    ufs = [u for u in e26 if u != "ZZ"]
    ufs.sort(key=lambda u: e26[u]["p13_2t"])
    fig, ax = plt.subplots(figsize=(8, 6.5))
    for i, u in enumerate(ufs):
        v = e26[u]
        ax.plot([v["p13_1t"], v["p13_2t"]], [i, i], color=GRADE, lw=2, zorder=1)
        ax.scatter([v["p13_1t"]], [i], s=36, color="#ffffff", edgecolor=COR[2026], lw=2, zorder=2)
        ax.scatter([v["p13_2t"]], [i], s=36, color=COR[2026], edgecolor=FUNDO, lw=2, zorder=3)
    ax.axvline(50, color=TXT2, lw=1, ls=":")
    ax.set_yticks(range(len(ufs)), ufs)
    ax.set_xlabel("% de votos válidos de Lula   (○ 1º turno  → ● 2º turno)")
    ax.set_title("Lula por estado, 1º → 2º turno de 2026 (à direita de 50% = venceu no estado)", loc="left", fontsize=11)
    return b64(fig)


def ficha(n, afirmacao, veredito, texto, extra=""):
    cor = VEREDITO[veredito]
    return (f"<div class='ficha'><div class='af'><span class='n'>{n}</span> “{html.escape(afirmacao)}”</div>"
            f"<div class='ver' style='background:{cor}'>{veredito}</div><div class='tx'>{texto}</div>{extra}</div>")


def tab(cab, linhas):
    h = "".join(f"<th>{html.escape(str(c))}</th>" for c in cab)
    b = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in l) + "</tr>" for l in linhas)
    return f"<table class='t'><tr>{h}</tr>{b}</table>"


def dec(x, fmt):
    return format(x, fmt).replace(".", ",")


def nf(x):
    return f"{x:,}".replace(",", ".")


def mi(x):
    return f"{x / 1e6:.2f} mi".replace(".", ",")


def pc(x, nd=2):
    return f"{x:.{nd}f}%".replace(".", ",")


def main():
    D = json.loads((SAIDA / "checagem_dados.json").read_text(encoding="utf-8"))
    p26, p22 = D["presidente_2026"], D["presidente_2022"]
    t1, t2 = p26["1"], p26["2"]
    c1 = {c["nr"]: c for c in t1["candidatos"]}
    cg = D["congresso_governadores"]
    cm = D["crescimento_municipal"]
    tr26, tr22 = D["transferencias_2026"], D["transferencias_2022"]
    e26, e22 = D["estados"]["2026_todas_ufs"], D["estados"]["2022_todas_ufs"]
    ap = D["apuracao"]

    F = []
    # 1 Congresso
    dep26, dep22 = cg["DEPUTADO FEDERAL_2026"], cg["DEPUTADO FEDERAL_2022"]
    F.append(ficha(1, "Maior bancada de direita da história na Câmara e no Senado", "PARCIALMENTE CORRETO",
        f"Câmara: partidos de direita e centro-direita elegeram <b>{dep26['por_campo'].get('direita', 0)}</b> de 513 deputados, "
        f"contra {dep22['por_campo'].get('direita', 0)} em 2022; o PL elegeu {dep26['por_partido']['PL']} (98 em 2022). "
        f"Senado em 2027 (eleitos em 2026 + eleitos em 2022, pela filiação na eleição): <b>{cg['SENADO_2027_composicao']['por_campo']['direita']}</b> de 81 de direita/centro-direita. "
        "É de fato maior que a de 2022. “Da história” não dá para conferir com estes arquivos (só temos 2022 e 2026), "
        "e depende de onde se põem MDB, PSDB e PSD — ver classificação ao final.",
        tab(["Campo", "Câmara 2026", "Câmara 2022", "Senado 2027"],
            [[k, dep26["por_campo"].get(k, 0), dep22["por_campo"].get(k, 0), cg["SENADO_2027_composicao"]["por_campo"].get(k, 0)]
             for k in ("direita", "centro", "esquerda")])))
    # 2 Governadores
    g26, g22 = cg["GOVERNADOR_2026"], cg["GOVERNADOR_2022"]
    F.append(ficha(2, "Maior número de governadores de direita", "PARCIALMENTE CORRETO",
        f"<b>{g26['por_campo'].get('direita', 0)}</b> dos 27 governadores eleitos em 2026 são de partidos de direita/centro-direita "
        f"(PL 6, PSD 5, PP 4, Republicanos 4, Podemos 1), contra {g22['por_campo'].get('direita', 0)} em 2022. "
        "Maior que em 2022: confirmado. “O maior da história” não é verificável aqui."))
    # 3 Flávio na frente / único de esquerda
    esq = [c for c in t1["candidatos"] if c["ideologia"] == "extrema-esquerda/esquerda" and c["nr"] != 13]
    F.append(ficha(3, "Flávio na frente. Lula o único candidato de esquerda", "PARCIALMENTE CORRETO",
        f"Flávio liderou o 1º turno: <b>{pc(c1[22]['pct_validos'])}</b> ({mi(c1[22]['votos'])}) contra {pc(c1[13]['pct_validos'])} "
        f"de Lula ({mi(c1[13]['votos'])}), diferença de {mi(c1[22]['votos'] - c1[13]['votos'])}. "
        f"Mas Lula <b>não</b> foi o único de esquerda: " + ", ".join(f"{c['nome']} ({c['partido']})" for c in esq)
        + f" também concorreram — somaram só {pc(sum(c['pct_validos'] for c in esq))}."))
    # 4 direita dividida
    dir_ = [c for c in t1["candidatos"] if c["ideologia"] in ("direita/extrema-direita", "centro-direita") and c["nr"] != 22]
    F.append(ficha(4, "Votos da direita divididos entre 3 candidatos", "CONFIRMADO",
        "Além de Flávio, " + ", ".join(f"{c['nome']} ({c['partido']}, {pc(c['pct_validos'])})" for c in dir_ if c["pct_validos"] > 0.1)
        + f" — e candidatos menores. Augusto Cury (Avante, {pc(c1[70]['pct_validos'])}) é classificado como centro. "
        f"Fora Lula e Flávio, sobraram <b>{mi(t1['validos'] - c1[13]['votos'] - c1[22]['votos'])}</b> votos válidos em jogo no 2º turno, "
        f"além de {mi(t1['abstencoes'])} abstenções e {mi(t1['brancos'] + t1['nulos'])} brancos e nulos."))
    # 5 transferências
    def tlin(tr, nomes):
        return [[nomes.get(k, k), mi(v["votos_1t"]), pc(v["para_13"], 1), pc(v["para_22"], 1), pc(v["nao_valido"], 1)]
                for k, v in tr.items()]
    nomes26 = {"v13": "Lula", "v22": "Flávio", "v55": "Caiado", "v14": "Renan Santos", "v70": "Augusto Cury",
               "outros": "demais candidatos", "nao_valido": "abstenção + branco + nulo"}
    nomes22 = {"v13": "Lula", "v22": "Bolsonaro", "v15": "Tebet", "v12": "Ciro", "outros": "demais candidatos",
               "nao_valido": "abstenção + branco + nulo"}
    nv = tr26["nao_valido"]
    F.append(ficha(5, "Quase todos os votos dos outros candidatos de direita vão para Lula", "INCORRETO",
        f"Estimativa seção por seção (inferência ecológica, ver nota): eleitores de <b>Caiado</b> foram ~{pc(tr26['v55']['para_22'], 0)} para Flávio "
        f"e ~{pc(tr26['v55']['para_13'], 0)} para Lula; os de <b>Renan Santos</b> se dividiram (~{pc(tr26['v14']['para_13'], 0)} / ~{pc(tr26['v14']['para_22'], 0)}, "
        f"e ~{pc(tr26['v14']['nao_valido'], 0)} não votaram em ninguém). Quem foi majoritariamente para Lula foi o eleitorado de <b>Augusto Cury</b> "
        f"(~{pc(tr26['v70']['para_13'], 0)}). O que mais pesou na virada foi outra coisa: de {mi(nv['votos_1t'])} pessoas que se abstiveram ou votaram branco/nulo "
        f"no 1º turno, ~{pc(nv['para_13'], 0)} (≈ {mi(nv['votos_1t'] * nv['para_13'] / 100)}) votaram em Lula no 2º, contra ~{pc(nv['para_22'], 0)} em Flávio. "
        f"Em 2022 esse grupo se dividiu quase igualmente ({pc(tr22['nao_valido']['para_13'], 1)} Lula / {pc(tr22['nao_valido']['para_22'], 1)} Bolsonaro). "
        "<br><b>Essa mobilização desigual é real nos números e é a característica que mais distingue 2026 de 2022.</b> "
        "Os testes seção por seção não acharam concentração anômala dela: aparece espalhada pelo país, e não em poucas seções, "
        "que é como apareceria um enchimento de urnas.",
        "<p class='nota'>2026</p>" + tab(["Origem (1º turno)", "Votos", "→ Lula", "→ Flávio", "→ não votou válido"], tlin(tr26, nomes26))
        + "<p class='nota'>2022 (referência)</p>" + tab(["Origem (1º turno)", "Votos", "→ Lula", "→ Bolsonaro", "→ não votou válido"], tlin(tr22, nomes22))))
    # 6 abstenção
    a1, a2 = t1["abstencoes"], t2["abstencoes"]
    b1, b2 = p22["1"]["abstencoes"], p22["2"]["abstencoes"]
    F.append(ficha(6, "Milhões saíram da abstenção em número histórico", "PARCIALMENTE CORRETO",
        f"A abstenção caiu de {mi(a1)} ({pc(100 * a1 / t1['aptos'])}) para <b>{mi(a2)}</b> ({pc(100 * a2 / t2['aptos'])}): "
        f"<b>{mi(a1 - a2)} a menos</b>. Em 2022 a queda foi de só {mi(b1 - b2)}. “Milhões”: confirmado. "
        "“Histórico”: não verificável com estes arquivos. Nas eleições de 2014 e 2018, a abstenção <i>subiu</i> no 2º turno "
        "(informação externa, não conferida aqui). Isso torna 2026 incomum, mas não impossível."))
    # 7 virada todos os estados
    vir = [u for u, v in e26.items() if u != "ZZ" and v["lider_1t"] != v["lider_2t"]]
    l2 = sum(1 for u, v in e26.items() if u != "ZZ" and v["lider_2t"] == 13)
    f2 = sum(1 for u, v in e26.items() if u != "ZZ" and v["lider_2t"] == 22)
    l1 = sum(1 for u, v in e26.items() if u != "ZZ" and v["lider_1t"] == 13)
    cresc = sum(1 for u, v in e26.items() if u != "ZZ" and v["p13_2t"] - v["p13_1t"] > v["p22_2t"] - v["p22_1t"])
    cresc22 = sum(1 for u, v in e22.items() if u != "ZZ" and v["p22_2t"] - v["p22_1t"] > v["p13_2t"] - v["p13_1t"])
    F.append(ficha(7, "Virada histórica de Lula em todos os estados", "INCORRETO",
        f"Lula virou em <b>um único estado</b>: {', '.join(vir)}. Liderava {l1} estados no 1º turno e venceu em {l2}; "
        f"Flávio venceu em <b>{f2}</b> estados no 2º turno. O que é verdade: Lula ganhou mais pontos percentuais que Flávio em "
        f"{cresc} das 27 UFs. É o mesmo padrão de 2022 ao contrário: naquele ano Bolsonaro ganhou mais pontos que Lula em {cresc22} das 27 UFs. "
        "No 2º turno é comum um candidato atrair quase todo o crescimento em quase todos os lugares.", ""))
    # 8 municípios
    d = cm["ganho em pontos % maior que o do adversário"]
    F.append(ficha(8, "Lula cresceu em 5.838 municípios e Flávio apenas em 184", "PARCIALMENTE CORRETO",
        f"Como está escrito, é impossível: o Brasil tem <b>{nf(cm['municipios_brasil'])}</b> municípios (+{cm['cidades_exterior']} cidades no exterior), "
        "e 5.838 + 184 dá 6.022. Testamos quatro definições de “cresceu”. A que chega perto é “ganhou mais pontos percentuais que o adversário”: "
        f"<b>Lula {nf(d['lula_cresceu_so_brasil'])} municípios, Flávio {nf(d['flavio_cresceu_so_brasil'])}</b>. O 184 bate quase exatamente, "
        "e 5.838 parece ser 5.389 com os dígitos trocados. Em votos absolutos <i>os dois</i> cresceram na maioria dos municípios "
        f"(Lula {nf(cm['votos absolutos']['lula_cresceu_so_brasil'])}, Flávio {nf(cm['votos absolutos']['flavio_cresceu_so_brasil'])}). "
        "Em 2022, pela mesma definição, Bolsonaro ganhou mais pontos que Lula em 4.647 municípios e Lula em 923. "
        f"No nível municipal houve {cm['viradas_municipais'].get('22->13', 0)} viradas de Flávio para Lula e {cm['viradas_municipais'].get('13->22', 0)} no sentido contrário.",
        tab(["Definição de “cresceu”", "Lula", "Flávio"],
            [[k, f"{v['lula_cresceu_so_brasil']:,}".replace(",", "."), f"{v['flavio_cresceu_so_brasil']:,}".replace(",", ".")]
             for k, v in cm.items() if isinstance(v, dict) and "lula_cresceu_so_brasil" in v])))
    # 9 pesquisas / mapa azul
    F.append(ficha(9, "Mapa do primeiro turno majoritariamente azul", "CONFIRMADO",
        f"No 1º turno Flávio liderou em {27 - l1} dos 27 estados e em <b>{cm['lider_1t_municipios']['22']:,}</b> municípios ".replace(",", ".")
        + f"(Lula em {cm['lider_1t_municipios']['13']:,}).".replace(",", ".") + f" Os municípios liderados por Flávio somam {mi(cm['lider_1t_aptos']['22'])} eleitores "
        f"de {mi(cm['lider_1t_aptos']['22'] + cm['lider_1t_aptos']['13'])}. Mas a vantagem total era pequena, 1,9 ponto. "
        "As pesquisas citadas não estão nos dados do TSE e não foram conferidas."))
    F.append(ficha(10, "Pesquisas (Datafolha e mais 18) davam vitória ao Flávio e erraram o vencedor", "NÃO VERIFICÁVEL COM ESTES DADOS",
        "Pesquisas não fazem parte dos arquivos do TSE baixados. Para conferir: registros no PesqEle (TSE) e os números publicados pelos institutos."))
    F.append(ficha(11, "4º mandato de um presidente nada popular", "PARCIALMENTE CORRETO",
        "Será o 4º mandato de Lula (2003, 2007, 2023, 2027): fato. Popularidade é dado de pesquisa, não verificável aqui."))
    F.append(ficha(12, "Virada inédita do 1º para o 2º turno", "CONFIRMADO",
        f"Quem liderou o 1º turno (Flávio, {pc(c1[22]['pct_validos'])}) perdeu o 2º (Lula {pc(t2['candidatos'][0]['pct_validos'])}). "
        "Pelo histórico das eleições presidenciais desde 1989, o líder do 1º turno sempre venceu (informação externa; estes arquivos só cobrem 2022 e 2026). "
        "Ser inédito não indica irregularidade por si só: a diferença no 1º turno era de 1,9 ponto, e havia 9,3 milhões de votos válidos em outros "
        "candidatos, mais 39 milhões de abstenções, brancos e nulos."))
    bn1, bn2 = t1["brancos"] + t1["nulos"], t2["brancos"] + t2["nulos"]
    bn1_22, bn2_22 = p22["1"]["brancos"] + p22["1"]["nulos"], p22["2"]["brancos"] + p22["2"]["nulos"]
    F.append(ficha(13, "Queda histórica de nulos e brancos", "PARCIALMENTE CORRETO",
        f"Brancos + nulos caíram de {mi(bn1)} ({pc(100 * bn1 / t1['comparecimento'])} dos votantes) para <b>{mi(bn2)}</b> "
        f"({pc(100 * bn2 / t2['comparecimento'])}), {mi(bn1 - bn2)} a menos. Em 2022 subiram ({pc(100 * bn1_22 / p22['1']['comparecimento'])} → "
        f"{pc(100 * bn2_22 / p22['2']['comparecimento'])}). Queda grande: confirmada. “Histórica”: não verificável com estes arquivos."))
    F.append(ficha(14, "Ex-advogado do candidato no STF interrompendo a apuração / usurpação de competência do TSE / fiscais expulsos da sala-cofre",
        "NÃO VERIFICÁVEL COM ESTES DADOS",
        "São afirmações sobre decisões judiciais e fatos presenciais. Não aparecem em dados de votação. Para conferir: "
        "o texto das decisões (STF/TSE), as atas e os relatos de fiscais dos partidos."))
    r2, r1, r22 = ap["2026_2t"]["rec"], ap["2026_1t"]["rec"], ap["2022_2t"]["rec"]
    F.append(ficha(15, "Suspensão da apuração após o início", "CONFIRMADO",
        "Os horários de recebimento de cada boletim de urna no TSE mostram que, no 2º turno de 2026, entre <b>17h03 e 17h07</b> chegaram "
        "1.870 boletins (778 do exterior e o resto de vários estados). Depois disso, <b>de 17h07 até 19h03, nenhum boletim de seção do Brasil foi recebido</b> "
        "(só 39 do exterior) e <b>nenhuma seção foi totalizada</b>. A retomada foi às 19h03 e a apuração chegou a 99% às 21h10. "
        f"Em comparação, no 1º turno metade dos boletins já tinha chegado às {r1['p50'][11:16]} e no 2º turno de 2022 às {r22['p50'][11:16]}; "
        f"no 2º turno de 2026, às {r2['p50'][11:16]}. "
        f"O 1º turno de 2026 também teve uma pausa, menor: cerca de {r1['maior_pausa_min_ate_99pct']:.0f} minutos sem recebimento a partir de {r1['maior_pausa_inicio'][11:16]}. "
        "<br><b>O que os dados mostram:</b> houve uma interrupção de cerca de 2 horas no recebimento e na totalização. "
        "Segundo a informação recebida, às 17h01 uma decisão do ministro Zanin mandou a votação continuar até 19h (não conferido nestes dados); "
        "a retomada às 19h03 e as urnas que votaram até ~19h01 (ficha 19) são coerentes com isso: a totalização só recomeçou quando terminou a votação. "
        "<b>O que não mostram:</b> o motivo, e se ela mudou algum resultado. Os boletins são gerados e impressos na própria seção às 17h, "
        "antes da interrupção, e assinados digitalmente pela urna. A forma objetiva de verificar é comparar o arquivo de BU de cada urna "
        "(que estamos baixando) e a imagem do BU impresso com o resultado publicado. Até agora, em todas as seções processadas, "
        "o número de votantes registrado no log de cada urna bate exatamente com o publicado.",
        f"<img src='data:image/png;base64,{fig_recebimento()}'>"))
    F.append(ficha(16, "Fenômeno absoluto em estados conservadores como GO, MT, SC, PR e RS", "INCORRETO",
        "Lula <b>perdeu nos cinco estados</b>, por margens largas: " + "; ".join(
            f"{u} {pc(e26[u]['p13_2t'], 1)} × {pc(e26[u]['p22_2t'], 1)}" for u in ("GO", "MT", "SC", "PR", "RS"))
        + ". O ganho dele entre os turnos foi parecido com a média nacional (+" + f"{t2['candidatos'][0]['pct_validos'] - c1[13]['pct_validos']:.1f}".replace(".", ",") + " pontos), "
        + "exceto em Goiás (+9,3 pontos). Lá Caiado, governador do estado, teve 12,3% no 1º turno, contra 1% a 5% nos outros estados, "
        "e por isso havia muito mais votos em disputa; em GO Flávio também teve seu maior ganho do país (+6,1). Em MT o ganho de Lula foi um dos menores (+4,8).",
        f"<img src='data:image/png;base64,{fig_ufs(e26)}'>"))
    ev = ap["2026_2t"]["evolucao_pct_lula_por_secoes_totalizadas"]
    F.append(ficha(17, "Em poucas horas Lula vira o maior fenômeno eleitoral da história", "EXAGERADO / ENGANOSO",
        f"Durante a totalização, Lula tinha {pc(ev['10%']['pct_lula'], 1)} com 10% das seções apuradas, {pc(ev['25%']['pct_lula'], 1)} com 25% "
        f"e {pc(ev['50%']['pct_lula'], 1)} com 50%, e terminou com {pc(ev['100%']['pct_lula'], 1)}. Foi uma vitória por 3,6 pontos, a mesma ordem de grandeza "
        "das margens de 2014 (3,3) e 2022 (1,8). A mudança gradual do placar conforme regiões diferentes são apuradas também aconteceu em 2022 "
        "(Bolsonaro liderou no início e Lula passou à frente com cerca de 2/3 apurados). Nos testes estatísticos seção por seção, 2026 teve "
        "<b>menos</b> seções com desvio forte de votação que 2022 (0,054% contra 0,068%)."))

    P = json.loads((SAIDA / "pos17_resumo.json").read_text(encoding="utf-8")) if (SAIDA / "pos17_resumo.json").exists() else None
    if P:
        dv = P["divisao_por_encerramento"]["2026"]
        ar = dv["agrupado_por_area"]["alguma urna encerrou depois de 17h15 — por zona"]
        def lin(nome, g):
            return [nome, nf(g["até"]["urnas"]), f"{dec(g['até']['margem_13_2t_mi'], '+.2f')}", f"{dec(g['até']['margem_13_1t_mi'], '+.2f')}",
                    nf(g["depois"]["urnas"]), f"{dec(g['depois']['margem_13_2t_mi'], '+.2f')}", f"{dec(g['depois']['margem_13_1t_mi'], '+.2f')}"]
        cortes = [k for k in dv if k.startswith("encerrou") or k.startswith("teve voto")]
        F.append(ficha(18, "Nas urnas fechadas após 17h, só 35 mil votos entre 17h e 19h; mas nessas urnas Lula teve vantagem de mais de "
                       "6 milhões, ao contrário das urnas fechadas às 17h, onde Flávio venceu por 1,8 milhão",
            "EXAGERADO / ENGANOSO",
            f"<b>O número de votos está certo:</b> os logs das urnas registram <b>{nf(dv['votos_apos_17h'])}</b> votos depois das 17h (horário de Brasília) no 2º turno. "
            f"Desses, {nf(P['votos_por_grupo_apos_17h'].get('FILA', 0))} foram da fila das 17h00–17h15 e só <b>{nf(P['votos_17h15_19h_total'])}</b> "
            "ao longo da prorrogação até 19h. Nenhum voto depois de 19h05."
            "<br><b>A divisão em dois grupos depende de como se define “fechou às 17h”.</b> O encerramento leva cerca de um minuto, "
            f"então {nf(dv['encerrou depois de 17h00:00']['depois']['urnas'])} das {nf(dv['secoes_com_log'])} urnas fecharam depois de 17h00min00s. "
            "Pela urna, nenhum corte reproduz “+6 mi × −1,8 mi”. O que chega perto é agrupar <b>zonas eleitorais inteiras</b> que tiveram alguma urna "
            f"encerrada depois de 17h15: Lula {dec(ar['sim']['margem_13_2t_mi'], '+.2f')} mi nessas zonas e Flávio {dec(-ar['não']['margem_13_2t_mi'], '+.2f')} mi nas demais."
            "<br><b>O ponto decisivo é o 1º turno:</b> nas mesmas urnas e zonas, sem prorrogação nenhuma, o padrão já era o mesmo. "
            f"As zonas “tardias” já davam Lula {dec(ar['sim']['margem_13_1t_mi'], '+.2f')} mi e as demais Flávio {dec(-ar['não']['margem_13_1t_mi'], '.2f')} mi de vantagem. "
            "Urnas que fecham mais tarde são as que têm fila: seções grandes e urbanas, em boa parte do Nordeste, do Rio e de São Paulo, onde Lula é mais forte. "
            "Entre os turnos, Lula ganhou praticamente o mesmo nos dois grupos. Não há “caminho inverso” criado pela prorrogação.",
            tab(["Corte (2º turno)", "urnas até", "margem Lula 2T", "margem Lula 1T", "urnas depois", "margem Lula 2T", "margem Lula 1T"],
                [lin(k, dv[k]) for k in cortes])
            + "<p class='nota'>Margens em milhões de votos (Lula − adversário). “1T” = mesmas urnas no 1º turno.</p>"
            + tab(["Agrupamento por área", "grupo", "urnas", "margem Lula 2T", "margem Lula 1T"],
                  [[k, g, nf(v["urnas"]), f"{dec(v['margem_13_2t_mi'], '+.2f')}", f"{dec(v['margem_13_1t_mi'], '+.2f')}"]
                   for k, gs in dv["agrupado_por_area"].items() for g, v in sorted(gs.items(), reverse=True)])))
        pe = P["perfil_urnas_estendidas"]
        rm = P["resultado_mesmos_municipios"]
        F.append(ficha(19, "As urnas que continuaram votando entre 17h e 19h mostram alguma anomalia?", "SEM ANOMALIA DETECTADA",
            f"<b>{nf(P['urnas_por_grupo'].get('ESTENDIDA', 0))}</b> urnas receberam votos depois de 17h15 "
            f"(principalmente RJ {P['estendidas_por_uf'].get('RJ', 0)}, SP {P['estendidas_por_uf'].get('SP', 0)}, BA {P['estendidas_por_uf'].get('BA', 0)}, "
            f"PE {P['estendidas_por_uf'].get('PE', 0)}), em média 1 a 2 votos cada (máximo {P['estendidas_distribuicao_votos_1715']['max']}). "
            f"Encerraram por volta de 19h01. {P['votos_apos_19h']} votos foram registrados entre 19h00 e 19h05 e nenhum depois; "
            f"{P['urnas_com_voto_apos_encerramento']} urna tem voto registrado após o próprio encerramento (para verificação individual)."
            "<ul>"
            f"<li><b>Biometria:</b> votos sem biometria após falha da digital: {pc(pe['17h15-19h']['pct_sem_biometria_apos_falha'])} na prorrogação contra "
            f"{pc(pe['8h-17h']['pct_sem_biometria_apos_falha'])} durante o dia, nas mesmas urnas (<i>menor</i>, não maior). Eleitores sem biometria cadastrada: "
            f"{pc(pe['17h15-19h']['pct_sem_biometria_cadastrada'])} contra {pc(pe['8h-17h']['pct_sem_biometria_cadastrada'])}.</li>"
            f"<li><b>Ritmo:</b> intervalo mediano entre eleitores de {dec(pe['17h15-19h']['intervalo_mediano_entre_eleitores_s'] / 60, '.0f')} minutos na prorrogação, "
            f"e só {pc(pe['17h15-19h']['pct_intervalo_menor_30s'])} dos votos com menos de 30 s de intervalo. <b>Nenhuma urna</b> teve rajada de 5 ou mais votos seguidos. "
            "Esse é o padrão de eleitores chegando aos poucos, não de alguém votando em sequência.</li>"
            f"<li><b>Resultado:</b> nos mesmos municípios, Lula cresceu {dec(rm['ESTENDIDA']['delta_lula_medio_pp'], '.1f')} pontos entre os turnos nas urnas estendidas, "
            f"{dec(rm['FILA']['delta_lula_medio_pp'], '.1f')} nas que só tiveram fila e {dec(rm['NORMAL']['delta_lula_medio_pp'], '.1f')} nas que fecharam às 17h. "
            f"O desvio de votação não difere entre os grupos (p = {dec(P['teste_z_A_estendida_vs_normal_mesmos_municipios']['mannwhitney_p'], '.2f')}) "
            f"e não cresce com a fração de votos feitos na prorrogação (ρ = {dec(P['correlacao_frac_votos_prorrogacao_x_desvio_voto']['spearman'], '.3f')}).</li>"
            f"<li><b>1º turno:</b> as mesmas urnas já tiveram {pc(P['estendidas_no_1t']['pct_votos_apos_17h_1t'])} dos votos depois das 17h no 1º turno, por causa de fila. "
            "São lugares que costumam fechar tarde.</li></ul>",
            f"<img src='data:image/png;base64,{base64.b64encode((SAIDA / 'fig_pos17' / 'votos_16h_19h30.png').read_bytes()).decode()}'>"
            if (SAIDA / "fig_pos17" / "votos_16h_19h30.png").exists() else ""))

    clas = D["classificacao_ideologica"]
    doc = f"""<!doctype html><html lang="pt-br"><meta charset="utf-8"><title>Checagem — mensagem sobre a eleição de 2026</title>
<style>
body{{font-family:system-ui,Segoe UI,sans-serif;max-width:900px;margin:2em auto;padding:0 1em;color:{TXT};background:{FUNDO};line-height:1.5}}
h1{{font-size:1.45em}} .nota{{color:{TXT2};font-size:.88em}}
.ficha{{border:1px solid {GRADE};border-radius:8px;padding:.9em 1em;margin:1.1em 0;background:#fff}}
.af{{font-weight:600}} .n{{display:inline-block;min-width:1.6em;color:{TXT2}}}
.ver{{display:inline-block;margin:.5em 0;padding:2px 10px;border-radius:4px;font-size:.8em;font-weight:700;letter-spacing:.03em;color:{TXT}}}
.t{{border-collapse:collapse;font-size:.85em;margin:.6em 0}} .t td,.t th{{border-bottom:1px solid {GRADE};padding:3px 8px;text-align:left}}
.t th{{color:{TXT2}}} img{{max-width:100%;margin-top:.6em}}
</style>
<h1>Checagem das afirmações sobre a eleição presidencial de 2026</h1>
<p class="nota">Fonte: arquivos oficiais do TSE (resultados por seção, candidatos eleitos, horários de recebimento e totalização de
cada boletim de urna), 2026 e 2022. Afirmações sobre fatos que não aparecem nesses dados (pesquisas, decisões judiciais,
relatos presenciais) estão marcadas como não verificáveis. Quando usamos informação externa aos dados, isso é dito no texto.</p>
<h2>Resumo</h2>
<ul>
<li><b>Verdadeiro:</b> Flávio liderou o 1º turno; o Congresso e os governos estaduais eleitos são mais à direita que os de 2022; a abstenção e os brancos/nulos caíram bastante; quem liderou o 1º turno perdeu o 2º.</li>
<li><b>Falso:</b> “virada de Lula em todos os estados” (virou só em MG; Flávio venceu em 14 estados); “fenômeno em GO, MT, SC, PR, RS” (Lula perdeu nos cinco); “quase todos os votos da direita foram para Lula” (os de Caiado foram majoritariamente para Flávio).</li>
<li><b>Número impossível:</b> 5.838 + 184 municípios passa do total do país. O 184 bate com “ganhou mais pontos percentuais”, e 5.838 parece ser 5.389 com dígitos trocados.</li>
<li><b>Confirmado e merece explicação oficial:</b> no 2º turno o recebimento e a totalização dos boletins ficaram parados de 17h07 a 19h03. Os dados não mostram a causa nem indicam alteração de resultado; a verificação objetiva é comparar os arquivos de BU das urnas com o resultado publicado.</li>
<li><b>Urnas que votaram entre 17h e 19h (fichas 18 e 19):</b> foram ~35 mil votos, como diz a mensagem, mas só ~3.900 na prorrogação em si. Essas urnas não mostram anomalia de biometria, ritmo ou resultado. A “vantagem de 6 milhões” vem de agrupar áreas onde Lula já liderava no 1º turno.</li>
<li><b>O que de fato explica a virada:</b> mobilização de quem se absteve ou votou branco/nulo no 1º turno (≈5 milhões de votos líquidos para Lula, pela estimativa) e os eleitores de Augusto Cury. É um padrão incomum em relação a 2022 e está espalhado pelo país, não concentrado em poucas seções.</li>
</ul>
{''.join(F)}
<h2>Notas de método</h2>
<ul class="nota">
<li><b>Inferência ecológica</b> (ficha 5): estima para onde foram os votos de cada grupo comparando, dentro de cada estado, a composição do 1º e do 2º turno em ~500 mil seções (mínimos quadrados com coeficientes não negativos). É uma estimativa: não se sabe o voto individual, e as taxas podem variar dentro do estado.</li>
<li><b>Classificação ideológica</b> dos partidos baseada em Bolognesi, Ribeiro & Codato (2023), <i>Dados</i> 66(2). “Direita” aqui = direita + centro-direita; “centro” inclui MDB, PSDB, Avante, Solidariedade e Cidadania. {html.escape(json.dumps(clas, ensure_ascii=False))}</li>
<li>Senado 2027 = eleitos em 2026 (54) + eleitos em 2022 (27), pela filiação na época da eleição; trocas de partido posteriores não são captadas.</li>
<li>Horários de recebimento e totalização: campos DT_RECEBIMENTO_BU_HOR_TSE e DT_PRIM_TOT_PARCIAL_HOR_TSE do arquivo “detalhe da votação por seção” do TSE (horário de Brasília).</li>
</ul></html>"""
    (SAIDA / "checagem.html").write_text(doc, encoding="utf-8")
    # trecho para o relatório final (06_relatorio.py)
    i, j = doc.index("<h2>Resumo</h2>"), doc.index("</html>")
    (SAIDA / "checagem_fragmento.html").write_text(doc[i:j], encoding="utf-8")
    print("ok:", SAIDA / "checagem.html")


if __name__ == "__main__":
    main()
