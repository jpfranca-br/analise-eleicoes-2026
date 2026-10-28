"""Envia o resumo estatístico para leitura crítica pelo Claude e salva saida/analise_ia.md.

Uso:
    python -I scripts/07_ia.py              # chama a API (requer ANTHROPIC_API_KEY ou `ant auth login`)
    python -I scripts/07_ia.py --so-prompt  # só grava saida/prompt_ia.md, sem chamar a API

Envia apenas agregados (resumo_2026.json, resumo_2022.json) e as ~80 seções com mais sinais;
nenhum dado pessoal de eleitor (os logs não têm identificação de eleitor).
Depois rode 06_relatorio.py de novo para incluir a análise no HTML.
"""
import argparse
import json
from pathlib import Path

import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "saida"
MODELO = "claude-opus-5-5"

SISTEMA = """Você é um estatístico especializado em forense eleitoral, revisando uma análise seção por seção
da eleição presidencial brasileira de 2026 (2º turno: Lula, nº 13, x Flávio Bolsonaro, nº 22), com a eleição de
2022 (Lula x Jair Bolsonaro) como linha de base calculada com a mesma metodologia.

Seu papel é dar uma leitura crítica, imparcial e tecnicamente rigorosa. Diferencie com cuidado:
- anomalia estatística esperada pelo acaso (centenas de casos extremos em ~500 mil seções são normais);
- anomalia explicável por fatores conhecidos (aldeias indígenas com voto em bloco, seções pequenas, mudanças de
  local de votação, filas no 1º turno, defeitos de leitor biométrico, urnas substituídas);
- padrões que de fato exigiriam investigação (sinais que diferem de 2022, que convergem nas mesmas seções e na
  mesma direção, ou que mostram a assinatura de manipulação, como votos após 17h sem biometria em seções com
  desvio de votação).
Não declare fraude nem descarte fraude além do que os números sustentam. Aponte limitações da metodologia e
verificações concretas (ex.: conferir boletins impressos, RDV, log completo de seções específicas)."""

PEDIDO = """Abaixo estão os resultados. Escreva, em português, um parecer com:
1. Conclusão principal em 3–5 frases: 2026 apresenta mais/menos/os mesmos sinais que 2022, e o que isso indica.
2. Teste por teste (A votação, B abstenção/brancos/nulos, C fluxo após 17h, D biometria, E impressão digital):
   o que o número mostra, comparação com 2022 e a interpretação mais provável.
3. Seções ou grupos de seções que merecem verificação individual, e por quê (cite UF/município/zona/seção).
4. Limitações e possíveis vieses da metodologia (incluindo sensibilidade do teste A à especificação do modelo).
5. Próximos passos de verificação.
6. Análises adicionais: (a) a interrupção do recebimento/totalização de BUs entre ~17h07 e 19h03 no 2º turno, no contexto
   da prorrogação da votação até 19h; (b) as urnas que receberam votos entre 17h e 19h; (c) a afirmação viral de que nessas
   urnas Lula teve +6 milhões e nas fechadas às 17h Flávio teve +1,8 milhão; (d) as demais afirmações checadas.
Seja direto; use números."""


def monta_dados():
    partes = []
    for ano in (2026, 2022):
        p = SAIDA / f"resumo_{ano}.json"
        if p.exists():
            partes.append(f"## resumo_{ano}.json\n```json\n{p.read_text(encoding='utf-8')}\n```")
    p = SAIDA / "secoes_sinalizadas_2026.csv"
    if p.exists():
        s = pl.read_csv(p, separator=";", infer_schema_length=10000)
        s = s.with_columns(pl.col("z_A_voto").abs().alias("_az")).sort(
            ["n_sinais", "_az"], descending=True, nulls_last=True).head(80).drop("_az")
        s = s.with_columns(pl.col(pl.Float64).round(4))
        partes.append("## 80 seções de 2026 com mais sinais (CSV ';')\n```\n" + s.write_csv(separator=";") + "```")
    # análises adicionais pedidas pelo usuário (checagem de mensagem viral, parada da apuração, urnas 17h-19h)
    for nome, titulo in [("pos17_resumo.json", "Urnas que votaram entre 17h e 19h (prorrogação) e afirmação sobre margens por horário de encerramento"),
                         ("checagem_dados.json", "Checagem de afirmações de mensagem viral (dados agregados)")]:
        p = SAIDA / nome
        if p.exists():
            dados = json.loads(p.read_text(encoding="utf-8"))
            if nome == "checagem_dados.json":
                dados = {k: v for k, v in dados.items() if k != "classificacao_ideologica"}
            partes.append(f"## {titulo} ({nome})\n```json\n{json.dumps(dados, ensure_ascii=False, default=str)}\n```")
    nota = (SAIDA / "notas_analista.md")
    if nota.exists():
        partes.append("## Notas do analista\n" + nota.read_text(encoding="utf-8"))
    return "\n\n".join(partes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-prompt", action="store_true")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    a = ap.parse_args()
    dados = monta_dados()
    conteudo = f"{PEDIDO}\n\n{dados}"
    (SAIDA / "prompt_ia.md").write_text(f"# SISTEMA\n{SISTEMA}\n\n# USUÁRIO\n{conteudo}", encoding="utf-8")
    print(f"prompt gravado em saida/prompt_ia.md ({len(conteudo):,} caracteres)")
    if a.so_prompt:
        return

    import anthropic
    client = anthropic.Anthropic()
    try:
        with client.beta.messages.stream(
            model=MODELO,
            max_tokens=64000,
            system=SISTEMA,
            thinking={"type": "adaptive"},
            output_config={"effort": a.effort},
            # se o modelo recusar por política, a API refaz a chamada num modelo alternativo
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": conteudo}],
        ) as stream:
            resp = stream.get_final_message()
    except anthropic.AuthenticationError:
        raise SystemExit("Sem credencial: defina ANTHROPIC_API_KEY (ou rode `ant auth login`).")
    except anthropic.RateLimitError as e:
        raise SystemExit(f"Limite de taxa atingido; tente novamente em instantes. ({e})")
    except anthropic.APIStatusError as e:
        raise SystemExit(f"Erro da API ({e.status_code}): {e.message}")
    except anthropic.APIConnectionError as e:
        raise SystemExit(f"Falha de conexão com a API: {e}")

    if resp.stop_reason == "refusal":
        raise SystemExit(f"Pedido recusado: {resp.stop_details}")
    texto = "".join(b.text for b in resp.content if b.type == "text")
    if resp.stop_reason == "max_tokens":
        texto += "\n\n[resposta truncada por max_tokens]"
    (SAIDA / "analise_ia.md").write_text(texto, encoding="utf-8")
    u = resp.usage
    print(f"análise gravada em saida/analise_ia.md | modelo {resp.model} | "
          f"tokens entrada {u.input_tokens:,} saída {u.output_tokens:,}")


if __name__ == "__main__":
    main()
