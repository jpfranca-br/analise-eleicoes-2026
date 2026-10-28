# Análise seção por seção — eleição presidencial 2026 (linha de base 2022)

Busca de inconsistências estatísticas no 2º turno presidencial de 2026 (Lula 13 × Flávio Bolsonaro 22) usando os
dados oficiais do TSE de **todas as ~500 mil seções**, incluindo o **log de cada urna**, com a eleição de 2022
(Lula × Jair Bolsonaro) como linha de base calculada pelo mesmo método.

> Um sinal estatístico é **indício para verificação, não prova**. Com ~500 mil seções, centenas de casos extremos
> são esperados por acaso e por fatores locais. O que importa é (1) se 2026 difere de 2022 e (2) se sinais
> diferentes convergem nas mesmas seções e na mesma direção.

## Conteúdo

| Pasta / arquivo | O que é |
|---|---|
| `scripts/01..10` | pipeline de análise (abaixo) |
| `servidor_mcp/` | servidor MCP para outras pessoas consultarem os dados sem baixar nada |
| `dados/brutos/` | arquivos originais do TSE (~363 GB; não versionar) |
| `dados/processados/` | parquets consolidados (~2,1 GB) |
| `saida/` | relatórios, resumos e listas (~50 MB) |
| `requirements.txt` | dependências fixadas |

## Obter os dados sem rodar o pipeline

O repositório já traz o núcleo consolidado (`dados/processados/*.parquet`, ~290 MB) e todas as saídas (`saida/`).
Os votos individuais extraídos dos logs (~490 milhões de linhas, 1,9 GB) estão nos anexos da Release `dados-v1`
(`logs_2026.zip`, `logs_2022.zip`, com `SHA256SUMS.txt`):

```bash
git clone https://github.com/<dono>/<repositorio>.git && cd <repositorio>
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -I scripts/00_baixar_dados_processados.py --repo <dono>/<repositorio>   # -> dados/processados/logs
```

Os ~363 GB brutos do TSE só são necessários para refazer o pipeline do zero ou para a ferramenta `log_urna`
do servidor MCP (`scripts/01_baixar.py` baixa tudo do TSE).

## Pipeline

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Linux: .venv/bin/python
PY=".venv/Scripts/python -I -X utf8"      # -I isola os dados baixados dos scripts
$PY scripts/01_baixar.py                 # baixa tudo (~250 GB de arquivos de urna + resultados), retomável
$PY scripts/02_resultados.py             # resultados por seção (Presidente) -> dados/processados/resultados_{ano}.parquet
$PY scripts/03_logs.py --todos           # logs de todas as urnas -> logs/eleitores_* e logs/secoes_* (16 processos)
$PY scripts/04_indicadores.py            # 1 linha por seção, 1º e 2º turno lado a lado -> indicadores_{ano}.parquet
$PY scripts/05_anomalias.py              # testes A–E (2026 e 2022) -> saida/escores_*, resumo_*, secoes_sinalizadas_*
$PY scripts/08_checagem.py               # dados da checagem de afirmações (exige consulta_cand_{ano}.zip em dados/brutos/odsele)
$PY scripts/10_pos17.py                  # urnas que votaram 17h–19h, divisões por horário de encerramento, lista de verificação
$PY scripts/09_checagem_html.py          # saida/checagem.html (+ trecho para o relatório final)
$PY scripts/07_ia.py                     # parecer do Claude (ANTHROPIC_API_KEY); --so-prompt só gera saida/prompt_ia.md
$PY scripts/06_relatorio.py              # saida/relatorio.html (inclui checagem e parecer da IA)
```

Tempo aproximado (20 núcleos, 64 GB RAM): download ~1h30; logs ~40 min; o restante, minutos.

### O que cada etapa lê dos logs
- Cada voto computado ("O voto do eleitor foi computado") com horário e tipo de habilitação:
  biometria; **manual após falha da digital** (dado pessoal ou mesário); **sem biometria cadastrada** (ano de nascimento).
- Abertura ("Urna pronta…"), encerramento ("Encerrar votação"; em 2022 "Inicio do Encerramento"), suspensões,
  urnas substituídas (logs aninhados de contingência são somados).
- O relógio da urna é **local**; o fuso é estimado por município pela hora de abertura (AC −2h, oeste do AM −2h etc.).
- **Validação:** nº de votos no log = comparecimento do BU em 499.170 de 499.177 seções (2026, 2º turno).
  As 7 diferenças são urnas substituídas/recuperação de dados (RED) e eleitores suspensos — ver
  `saida/verificacao_individual_2026.csv`.

## Testes (05_anomalias.py)

| | O que mede | Como |
|---|---|---|
| A | votação 13×22 no 2º turno vs. esperado pelo 1º | logit + splines, por UF, efeito fixo de município; z calibrado por faixa; **sensibilidade** com efeito fixo de zona, de local de votação e modelo linear |
| B | abstenção, brancos, nulos | idem, por taxa |
| C | fluxo após 17h (Brasília) | Poisson vs. município + mesma seção no 1º turno; ritmo vs. pico do dia; rajadas <30 s |
| D | votos sem biometria | 2º × 1º turno na mesma seção; fim do dia × resto do dia (binomial, FDR 1%) |
| E | "impressão digital" | correlação entre desvio de votação e votos tardios/sem biometria |

Seções cujo eleitorado mudou entre turnos (≈700 por ano) ficam fora dos testes A, B e D1. Locais indígenas são
identificados pelo nome do local (contexto: voto em bloco).

## Análises adicionais (pedidas durante o projeto, todas no relatório final)
- **Checagem de afirmações virais** (19 fichas): Congresso, governadores, transferências de voto (inferência ecológica),
  abstenção, municípios, estados, "35 mil votos / +6 milhões" etc. — `08_checagem.py`, `09_checagem_html.py`.
- **Parada da apuração**: horário de recebimento e totalização de cada BU (2º turno: nada recebido do Brasil entre 17h07 e 19h03).
- **Prorrogação até 19h**: urnas que receberam votos entre 17h15 e 19h — perfil de biometria, ritmo, resultado vs. vizinhas — `10_pos17.py`.

## Saídas principais (`saida/`)
| Arquivo | Conteúdo |
|---|---|
| `relatorio.html` | relatório final: 2026 × 2022, gráficos, seções sinalizadas, análises adicionais, parecer da IA |
| `checagem.html` | checagem das afirmações (versão independente) |
| `analise_ia.md` / `prompt_ia.md` | parecer do Claude e exatamente o que foi enviado |
| `resumo_{ano}.json`, `pos17_resumo.json`, `checagem_dados.json` | números agregados |
| `secoes_sinalizadas_{ano}.csv`, `escores_{ano}.parquet` | sinais e z-scores por seção |
| `verificacao_individual_2026.csv` | seções para conferência documental e o motivo |

---

## Servidor MCP — acesso compartilhado aos dados

Permite que qualquer pessoa (com o token) analise os dados brutos, consolidados e relatórios **sem baixar nada**:
as consultas rodam no servidor. Funciona com Claude Code, Claude Desktop e outros clientes MCP.

### Ferramentas
| Ferramenta | Para quê |
|---|---|
| `visao_geral` | o que é o projeto, tabelas e principais números |
| `listar_tabelas`, `descrever_tabela` | catálogo, colunas e exemplos |
| `consultar_sql` | SQL livre (DuckDB, **somente leitura**) sobre todas as tabelas — inclusive os ~490 milhões de votos dos logs |
| `buscar_municipio` | código TSE pelo nome |
| `secao` | ficha completa de uma seção (dois turnos, log, escores) |
| `linha_do_tempo_secao` | cada voto da urna: horário de Brasília, tipo de habilitação, duração |
| `log_urna` | log bruto original da urna, com filtros (requer os arquivos brutos no servidor) |
| `listar_relatorios`, `ler_relatorio` | relatórios em texto, paginados |

Tabelas SQL: `resultados_{ano}`, `candidatos_{ano}`, `indicadores_{ano}`, `escores_{ano}`, `secoes_sinalizadas_{ano}`,
`curva_horaria_{ano}`, `secoes_log`, `eleitores`, `pos17_secoes`, `verificacao_individual_2026`.

Segurança: DuckDB em memória restrito às pastas de dados (`allowed_directories`, sem acesso externo, configuração
travada); só um comando de leitura por vez; tempo máximo por consulta (`MCP_TIMEOUT_S`, padrão 60 s); no Docker os
dados são montados somente leitura; token Bearer opcional (`MCP_TOKEN`).

### Usar localmente (nesta máquina)
O arquivo `.mcp.json` na raiz já registra o servidor para o Claude Code (stdio). Teste rápido:
```bash
.venv/Scripts/python -I -X utf8 servidor_mcp/testar.py
```

### Rodar nesta máquina (Windows) e publicar via Cloudflare Tunnel
```powershell
powershell -ExecutionPolicy Bypass -File servidor_mcp\iniciar.ps1   # sobe em http://127.0.0.1:8000/mcp, em segundo plano
powershell -ExecutionPolicy Bypass -File servidor_mcp\parar.ps1     # para
```
- O token é gerado na 1ª execução em `servidor_mcp\.mcp_token` (não compartilhe o arquivo; distribua o token só a quem deve acessar).
  Para trocar o token: pare o servidor, apague o arquivo e inicie de novo.
- Logs do servidor: `logs\mcp_servidor.out.log` e `logs\mcp_servidor.err.log`.
- O servidor ouve só em `127.0.0.1`; o túnel Cloudflare deve apontar para `http://localhost:8000`
  (ex.: túnel rápido `cloudflared tunnel --url http://localhost:8000`). O endereço público para os clientes é `https://<seu-host>/mcp`.
- Não reinicia sozinho após reboot do Windows: rode `iniciar.ps1` de novo (ou crie uma tarefa agendada "Ao fazer logon").

### Publicar num servidor
Requisitos: Linux com Docker; ~4 GB de disco (só consolidados) ou ~370 GB (com brutos, para `log_urna`); 16 GB RAM.
```bash
# 1. copiar o projeto (sem os brutos, se não quiser log_urna)
rsync -av --exclude '.venv' --exclude 'dados/brutos' ./ usuario@servidor:/srv/eleicoes/
rsync -av dados/brutos/arqurna/ usuario@servidor:/srv/eleicoes/dados/brutos/arqurna/   # opcional, 362 GB
# 2. no servidor
cd /srv/eleicoes
export MCP_TOKEN=$(openssl rand -hex 24); echo "$MCP_TOKEN"     # distribua só a quem deve acessar
# edite servidor_mcp/Caddyfile com seu domínio (HTTPS automático)
docker compose -f servidor_mcp/docker-compose.yml up -d --build
```
Sem Docker: `MCP_TOKEN=... python -I servidor_mcp/servidor.py --http --host 0.0.0.0 --porta 8000` (use um proxy HTTPS).

### Conectar como usuário
Claude Code:
```bash
claude mcp add --transport http eleicoes-2026 https://eleicoes.seudominio.com.br/mcp --header "Authorization: Bearer <TOKEN>"
```
Ou em `.mcp.json` / configuração do cliente:
```json
{"mcpServers": {"eleicoes-2026": {"type": "http", "url": "https://eleicoes.seudominio.com.br/mcp",
  "headers": {"Authorization": "Bearer <TOKEN>"}}}}
```
**Claude na web (claude.ai)**: os conectores personalizados não aceitam cabeçalhos, então use o token no caminho da URL.
Em Configurações → Conectores → *Adicionar conector personalizado*, informe só a URL (deixe OAuth em branco):
```
https://eleicoes.seudominio.com.br/<TOKEN>/mcp
```
Essa URL equivale a uma senha: compartilhe-a com o mesmo cuidado que o token.

Verificação de saúde (sem token): `GET /saude`. O servidor não usa OAuth; rotas `/.well-known/*` respondem 404.

---
Fontes: TSE — Portal de Dados Abertos (resultados, detalhe da apuração por seção, candidatos, arquivos de urna).
