# Parecer técnico: análise forense seção a seção do 2º turno de 2026, com 2022 como linha de base

## 1. Conclusão principal

1. **2026 apresenta menos sinais que 2022 em praticamente todos os indicadores.**
   - Divergências log × BU: 7 contra 53.
   - Seções com 2 ou mais sinais: 47 contra 102.
   - Saltos de voto sem biometria: 152 contra 1.008.
   - Excesso de votos após 17h: 12 contra 36.
   - Abstenção, brancos e nulos estão em patamar equivalente.
2. **A exceção é a assimetria do teste A** (212 pró-Lula × 56 pró-Flávio; em 2022, 175 × 134). Ela não é robusta: inverte de sinal no modelo linear (121 × 278), concentra-se em seções próximas de 100% Lula, onde a escala logit infla o z, e não converge com nenhum outro sinal.
3. **Os votos após 17h não podem ter decidido a eleição.** Foram 34.747 votos, 0,78% da margem de 4,43 mi. Cerca de 92% da virada entre turnos (6,13 de 6,65 mi) ocorreu em urnas sem nenhum voto após 17h.
4. **O que distingue 2026 é agregado e difuso:** o comparecimento subiu 2,96 mi e o crescimento de Lula ocorreu em 99% dos municípios. Isso é compatível com mobilização real e não aparece concentrado em seções anômalas.
5. **Limite dos testes:** testes seção a seção não detectam uma manipulação sistêmica e uniforme. Essa hipótese só se descarta por auditoria: BUs impressos, teste de integridade e assinaturas digitais. Os números não sustentam alegação de fraude, mas também não substituem essa auditoria.

---

## 2. Teste por teste

### A — Votação 2T condicionada ao 1T

| | 2026 | 2022 |
|---|---|---|
| Seções "fortes" | 268 (0,054%) | 309 (0,066%) |
| Pró-13 / pró-22 | 212 / 56 (3,8:1) | 175 / 134 (1,3:1) |
| Binomial de simetria | p = 1,6×10⁻²² | p = 0,023 |
| \|z\| > 6 | 29 | 42 |
| Média de z | 0,016 | −0,004 |
| Fortes em local indígena | 34 (12,7% dos fortes; esses locais são 0,21% das seções, ~59×) | 33 |
| Fora de local indígena, pró-13 / pró-22 | 180 / 54 | 147 / 129 |

**Sensibilidade à especificação (pró-13 / pró-22):**

| Especificação | 2026 | 2022 |
|---|---|---|
| Logit, efeito fixo de município | 212 / 56 | 175 / 134 |
| Logit, efeito fixo de zona | 223 / 85 | 168 / 152 |
| Logit, efeito fixo de local | 226 / 125 | 221 / 176 |
| Linear, efeito fixo de município | **121 / 278** | 114 / 179 |

**Leitura:**

- **O viés de especificação já existia em 2022.** A troca de especificação desloca a assimetria sempre na mesma direção nos dois anos: o logit tende a pró-13 e o linear a pró-22. Em 2026 os dois extremos se acentuam em sentidos opostos. Isso indica maior heterogeneidade do *swing* entre turnos, não uma anomalia unilateral.
- **Há artefato de fronteira visível.** A seção RS/Viamão 89630/59/591 (Tekoa Nhe Engatu) teve 100% Lula no 1T e 100% no 2T, e mesmo assim recebeu z = +6,03 "pró-Lula". Outras seções que só passaram de cerca de 92–99% para 100% também têm z entre 5 e 7:
  - MA/Água Doce 7005/12/145;
  - AM/Santo Antônio do Içá 2739/47/9;
  - MT/Confresa 90280/28/200;
  - MA/Turiaçu 9415/39/206;
  - AM/Juruá 2470/50/19.

  Em 2026 Lula ganhou ~6,6 p.p. no 2T e mais seções encostaram no teto. Por isso o artefato pesa mais neste ano do que em 2022.
- **O p-valor da binomial está superestimado.** Ele supõe independência, mas os casos vêm em clusters do mesmo local. Exemplo: 5 seções pró-Flávio no Colégio Equipe (SP).
- **A cauda pesada é igual à de 2022.** A curtose é 2,24 contra 1,87, e o número absoluto de casos extremos é menor.
- **Interpretação mais provável:** voto em bloco indígena e comunitário, choques locais e artefato de modelo perto dos limites 0/1. Não há assinatura de adulteração.

### B — Abstenção, brancos e nulos

| | 2026 | 2022 |
|---|---|---|
| Abstenção forte alta / baixa | 795 / 287 | 591 / 602 |
| R² do modelo de abstenção | 0,757 | 0,819 |
| Média de abstenção 1T → 2T | 20,8% → 19,1% | 20,8% → 20,6% |
| Branco forte (só alta) | 497 | 414 |
| Nulo forte (só alta) | 547 | 609 |
| Média de branco / nulo 1T → 2T | 1,82→1,10 / 2,93→2,11 | 1,57→1,40 / 2,81→3,12 |

- **A assinatura de enchimento de urna está menos presente que em 2022.** Essa assinatura seria abstenção muito abaixo do esperado: são 287 casos, contra 602 em 2022.
- **Os excessos de abstenção concentram-se em logística local.** Aparecem sobretudo em AM, AC, PA e PR rural (Coari, Carauari, Itacoatiara, Maraã, Prudentópolis). São compatíveis com transporte fluvial, acesso e mudança de local, a confirmar caso a caso.
- **Em vários desses casos Lula sobe junto com a abstenção.** Exemplo: AM/Coari 2259/8/119, onde o comparecimento caiu de 302 para 236. Esse padrão é de abstenção seletiva: os dois candidatos perdem votos, Flávio mais que Lula. É o oposto de inclusão de votos.
- **O R² mais baixo em 2026** indica mudança de comparecimento mais heterogênea, o que também alimenta a dispersão do teste A.

### C — Fluxo após 17h

| | 2026 | 2022 |
|---|---|---|
| Votos após 17h no 2T | 34.747 (0,027%) | 41.413 (0,033%) |
| Seções com ≥10 / ≥30 votos após 17h | 17 / 2 (máx. 39) | 85 / 8 (máx. 50) |
| Significativas por FDR | 12 | 36 |
| Ritmo acima do pico do dia | 6 | 40 |
| Seções com rajadas ≥5 (<30s) | 0 | 3 |
| Mediana do intervalo entre votos: dia / após 17h | 71s / 602s | 73s / 472s |
| Votos antes de 8h | 0 | 0 |
| Seções com último voto após 19h | 11 (1 voto cada) | 2 |
| 1T: votos após 17h | 3,73 mi (2,97%) | 4,34 mi (3,51%) |

- **Todos os indicadores de fila são menores que em 2022.**
- **Os casos de "ritmo acima do pico" são filas de encerramento.** Têm de 10 a 24 votos a 40–65 votos/h, cerca de 1 por minuto, o que é fisicamente compatível com fila com senha. Os z_A desses casos vão de −0,76 a +1,32: nenhum tem desvio de votação.
- **As 11 seções com voto após 19h** registraram votos entre 19h00m08s e 19h06m21s. Todas ficam nas capitais com prorrogação (Rio, São Paulo, Salvador). O padrão é compatível com eleitor na fila no horário-limite.
- **As filas massivas do 1T (3,7 mi votos após 17h)** provavelmente inflaram a abstenção do 1T em alguns locais, por desistências. Isso contamina a comparação 1T→2T: o eleitor que desistiu da fila no 1T voltou no 2T.

### D — Biometria

| | 2026 | 2022 |
|---|---|---|
| % sem biometria 1T → 2T | 6,66 → 6,73 | 8,73 → 8,06 |
| D1: aumento forte / queda forte | 152 / 300 | 1.008 / 1.123 |
| % sem biometria: até 16h / 16h em diante | 6,80 / 5,58 | 8,15 / 6,62 |
| D2: significativas | 11 | 42 |
| Seções com >30% / >50% sem biometria | 348 / 97 | 3.998 / 320 |

- **Melhora clara em relação a 2022.** A assinatura de manipulação seria um salto de votos sem biometria no fim do dia, e o padrão observado é o inverso: a taxa cai após 16h.
- **Os casos fortes do topo da lista têm, em geral, `contingencia=True`,** isto é, urna substituída e provável falha de leitor.
- **Verificação útil do aumento de comparecimento** (estimativa aproximada, sujeita à ponderação das médias):
  - Votos sem biometria no 1T: 6,66% × 125,28 mi ≈ 8,34 mi.
  - Votos sem biometria no 2T: 6,73% × 128,24 mi ≈ 8,63 mi.
  - Diferença: cerca de +0,29 mi.
  - Conclusão: dos +2,96 mi eleitores adicionais, cerca de 2,7 mi ou mais se identificaram por digital.
  - Um comparecimento extra fabricado por habilitação do mesário teria elevado a taxa sem biometria para cerca de 8,8%.

### E — "Impressão digital": desvios convergindo nas mesmas seções

| Coeficiente (desvio-padrão de z_A por +1 desvio-padrão do indicador) | 2026 | 2022 |
|---|---|---|
| Variação do % sem biometria | −0,002 | 0,000 |
| % de votos após 17h | +0,014 | −0,004 |
| Variação da abstenção | −0,020 | −0,035 |

- **A assinatura de fraude pró-Lula seria** coeficiente positivo para biometria, positivo para votos após 17h e fortemente negativo para variação da abstenção. O observado é nulo, minúsculo e menor que em 2022, respectivamente.
- **O +0,014 em votos após 17h** pode ser estatisticamente "significativo" com n ≈ 500 mil, mas é substantivamente irrelevante.
  - A explicação mais plausível é causal invertida: onde a mobilização foi maior houve mais fila. O grupo FILA teve variação de abstenção de −2,49 p.p. contra −2,15 p.p. no NORMAL.
  - De todo modo, esses votos somam 34,7 mil.

---

## 3. Seções que merecem verificação individual

### Prioridade 1 — anomalia de procedimento (independente do resultado)

- **MG 46256 / zona 131 / seção 46**
  - 125 votos registrados após o encerramento do log.
  - Encerramento registrado 386 minutos antes das 17h, por volta de 10h34.
  - Hipóteses: troca de urna com logs mesclados ou relógio errado.
  - Conferir ata da mesa, log das duas urnas, RDV e BU impresso.
- **ES 57932 / 9 / 85**
  - Log com 612 votos, BU com 308; BU gerado por RED (Recuperador de Dados).
  - Provável duplicação de log de urna substituta; precisa ser documentada.
- **MA 8893 / 47 / 609** (BU com 36 votos a mais que o log) e **BA 35653 / 173 / 235** (13 a mais).
  - Ambas têm contingência.
  - Verificar se o log da urna de contingência está completo.
- **PI 11533/3/216, BA 34711/21/178 e PB 21750/2/254**
  - Diferença de 1 voto **sem contingência** — sem explicação óbvia.
  - Pode ser problema de parsing do log; conferir o log bruto.
- **RS 89060 / 17 / 191** (diferença de 2 votos, com contingência).

### Prioridade 2 — desvio de voto combinado com procedimento ou cluster

- **AM / Ipixuna 2399 / 45 / 63**
  - z_A = +28,7, o maior do país; Lula passou de 64,9% para 98,8%.
  - Abstenção subiu de 32% para 41%; nulos de 8% para 14%.
  - **Contingência e uma suspensão**; é uma das duas únicas seções com 3 sinais.
  - A seção vizinha **45/52** (mesmo local, Aldeia Piau) tem nulo de 11,9% → 27% e uma suspensão.
  - Voto em bloco indígena é plausível, mas a combinação com troca de urna justifica conferir BU impresso, RDV e log.
- **AM / Barcelos, zona 18 — seções 37, 39 e 40**
  - Mesmo local, sentidos opostos: na 37 Lula foi de 17% para 54% (z +12,1); na 39 caiu de 28% para 19% (z −5,3).
  - Nulos altos nas três seções, até 21%.
  - Hipótese: eleitores trocados entre seções ou erro de cadastro. Verificar a lista de aptos dos dois turnos.
- **AC / Manoel Urbano 1554 / 3 / 160 e 100** (Aldeia Buaçú)
  - Na 160, Lula caiu de 67% para 32% (z −13,2).
  - Nulos subiram para 12–18%.
  - Provável mudança de orientação de liderança local.
- **SP / São Paulo, zona 2, Colégio Equipe — seções 491, 506, 519, 532 e 539**
  - Cinco seções pró-Flávio, com z entre −5,9 e −7,0.
  - Abstenção caiu de 32–36% para 17–22%, sem fila no 1T.
  - Abstenção de 1T anormalmente alta para essa região sugere mudança de local ou problema de acesso no 1T.
  - Verificar ocorrências no TRE-SP.
  - Observação: o desvio é contra o vencedor.
- **PR / Prudentópolis, zona 30 — seções 37 e 122**
  - Na 37 a abstenção foi de 22% para 54% (comparecimento 264 → 155).
  - Verificar acesso, clima e mudança de local.
- **AM / Coari, zona 8 — seções 119 e 173**
  - Abstenção +15 p.p. e +11 p.p.
  - A 119 é a outra seção com 3 sinais.
  - Atenção: os sinais A, abstenção e nulo descrevem o mesmo evento e não são independentes.

### Prioridade 3 — biometria

- **BA / Lauro de Freitas 36854 / 180 / 149**
  - Sem biometria passou de 16% para 69%, com contingência; abstenção de 35% para 18%.
  - Houve 94 votos após 17h no 1T, o que indica abstenção inflada por fila.
  - z_A = −2,3, levemente pró-Flávio.
- **BA / Candeias 34290 / 127 / 55**
  - Sem biometria de 2% para 9,6%; abstenção de 33% para 16%; z_A +1,46.
  - É o caso mais próximo da assinatura de enchimento, ainda que fraco.
  - Houve 82 votos após 17h no 1T, o que sugere a mesma explicação de fila no 1T.
  - Conferir ata e habilitações manuais.
- **RS / Ivoti 87173 / 118 / 143**
  - Sem biometria de 11% para 42%, concentrado no fim do dia; contingência e duas suspensões.
- **CE / Camocim 13510 / 32 / 189** (14% → 28%, fim do dia, contingência).
- **SP / Guarulhos 64777 / 394 / 417**
  - Sem biometria de 4% para 27%, fim do dia, **sem contingência registrada**.
  - É o caso de biometria menos explicado.

### Prioridade 4 — votos após 17h

- **BA / São Miguel das Matas 38873 / 36 / 199**
  - Encerramento às 18h51, 10 suspensões, 22 votos após 17h, contingência.
  - Defeito de urna gerando fila é a hipótese provável; z_A −0,76.
- **SP / Guarujá 64750 / 310 / 303** (4 rajadas, contingência).
- **SP / São Paulo 71072 / 247 / 724** (24 votos após 17h, 2 rajadas).
- **PE / Água Preta 23078 / 38 / 55** e **CE / Jaguaretama 14354 / 72 / 96**.
- **A única urna estendida com biometria anômala** (p < 0,001): não está identificada no resumo e deve ser identificada e conferida.

### Prioridade 5 — votação extrema fora de local indígena

- **Pró-Flávio:**
  - PI / Santo Antônio de Lisboa 11878/28/99: Lula de 78% para 54%, z −9,2.
  - MG / Fruta de Leite 42080/244/72: 3 suspensões.
  - SC / Mafra 81990/22/69: contingência.
- **Pró-Lula:**
  - AP / Itaubal 6041/10/408: abstenção de 7,6% para 33,8%. A abstenção de 1T é suspeitamente baixa.
  - CE / Caucaia 13730/120/361: z +7,2, brancos subindo.
- **Seções não indígenas com 0 voto para Flávio no 2T:**
  - Água Doce do Maranhão 7005/12/145 (193 votos);
  - Santo Antônio do Içá 2739/47/9 (330 votos);
  - Juruá 2470/50/19;
  - Turiaçu 9415/39/206.

  No 1T, Flávio tinha de 3 a 5 votos nessas seções. A verificação é barata: basta um eleitor que declare ter votado nele, ou o BU impresso.

### Seções redesenhadas entre turnos (28)

Nelas o comparecimento do 1T supera os aptos do 2T. Exemplos:

- PE 24910/117/16 (210 > 136) e /417 (201 > 139);
- PE 25313, zona 5: seções 21, 22, 509, 516 e 517;
- MA 9210, zonas 2 e 89: seções 511, 512, 513, 532 e 534;
- BA 34134/170/262 (107 > 68).

O total nacional de aptos é idêntico nos dois turnos (158.745.502), então houve realocação de eleitores entre seções. Essas seções devem ficar fora dos testes 1T→2T, e o motivo deve ser documentado pelo TRE.

---

## 4. Limitações e vieses da metodologia

1. **Especificação do teste A.** A direção da assimetria muda com o modelo (logit 212/56; linear 121/278).
   - O logit infla desvios perto de 0 e 1, como mostra o caso Viamão 100%→100% com z = +6.
   - O modelo linear é mal especificado nas bordas e é heterocedástico.
   - Recomendação: usar p-valores preditivos em contagens (beta-binomial), verificar calibração com histograma PIT por faixa de p13 previsto e reportar os casos fortes por decil do valor previsto.
2. **Parâmetro de "sobredispersão" menor que 1 (0,618).** Se ele escala a variância binomial para baixo, os z ficam inflados. A definição precisa ser explicitada.
3. **Independência.** O teste binomial de simetria e a contagem de "sinais" ignoram clusters por local e por zona. Além disso, os sinais A, abstenção, branco e nulo são mecanicamente correlacionados, de modo que "3 sinais" pode ser um único evento.
4. **O que os testes não detectam.** Os testes procuram manipulação localizada. Uma alteração uniforme, por exemplo x% em todas as urnas via software, seria absorvida pelo *swing* esperado e pelos efeitos fixos. Para essa hipótese, só a auditoria é informativa.
5. **Log e BU vêm da mesma urna.** A concordância entre eles (99,999%) exclui erro de transmissão e de totalização, mas não valida o software da urna.
6. **Covariáveis limitadas.** O modelo usa apenas o resultado do 1T. Choques locais (transporte, clima, liderança comunitária, mudança de local, filas do 1T) aparecem como "anomalia".
7. **Transferências entre candidatos** são inferência ecológica, com incerteza alta e sujeita à falácia ecológica.
8. **Comparabilidade entre anos.**
   - O evento de encerramento difere: "Encerrar votação" em 2026 contra "Início do Encerramento" em 2022, o que explica 228.708 urnas encerradas até 17h01 contra 2.791.
   - Houve prorrogação até 19h apenas em 2026.
   - Os candidatos e o desenho do 1T são diferentes.
9. **Seleção do topo.** A lista das 80 seções ordena pelo número de sinais, o que favorece seções pequenas e rurais, de alta variância.
10. **Seções do exterior (ZZ)** não têm biometria (100% sem cadastro) e têm abstenção altíssima. Exemplo: Porto, 30341/1/1894, z +5,9. Deveriam ser analisadas à parte.

---

## 5. Próximos passos de verificação

1. **Comparar BU impresso com BU publicado.** Usar os QR codes fotografados por fiscais e partidos. Fazer amostra aleatória estratificada de pelo menos alguns milhares de seções, mais todas as seções listadas na seção 3, priorizando BUs recebidos durante e após a pausa de 17h07–19h03.
2. **Verificar criptografia.** Conferir a assinatura digital de todos os BUs e logs com as chaves das urnas, e o hash dos sistemas com o lacrado na cerimônia.
3. **Auditar fluxo e contingências.** Obter RDV, log completo das duas urnas e ata da mesa para:
   - MG 46256/131/46;
   - ES 57932/9/85;
   - MA 8893/47/609;
   - BA 35653/173/235;
   - Ipixuna 45/63;
   - Lauro de Freitas 180/149;
   - Ivoti 118/143.
4. **Conferir o horário de emissão do BU.** Comparar o horário registrado no próprio BU com o encerramento do log. Um BU emitido após 19h por urna que encerrou às 17h seria sinal relevante.
5. **Obter os relatórios oficiais.** Pedir os resultados do teste de integridade (votação paralela) e da modalidade com biometria do 2T.
6. **Usar o registro individual de comparecimento.** Para os cerca de 3 mi eleitores que se abstiveram no 1T e votaram no 2T, medir a taxa de identificação biométrica.
7. **Reestimar o teste A.**
   - Usar modelo beta-binomial com efeito fixo de local e interação do *swing* com o nível de p13 no 1T e com a região.
   - Excluir seções redesenhadas e do exterior.
   - Rodar um placebo 2018→2022 para calibrar quantos casos fortes são esperados.
8. **Contar seções com 0 voto para um dos candidatos** no 2T de 2026 e comparar com o 2T de 2022.
9. **Desagregar o teste A por UF,** em especial RJ, SP, BA e PE (UFs com prorrogação) e RJ (estado de origem de Flávio, onde sua fatia ficou estável: 53,01% → 53,10%).
10. **Obter os documentos da prorrogação:** o ato oficial que a justificou, as UFs abrangidas e a instrução sobre transmissão de BUs durante a janela.

---

## 6. Análises adicionais

### (a) Pausa na totalização entre 17h07 e 19h03

- **O que os dados mostram:**
  - A totalização ficou parada 115,3 minutos (17:07:37 → 19:02:54), e essa foi a única pausa maior que 5 minutos.
  - O recebimento de BUs continuou, com pausas: a maior durou 34 minutos (17:59–18:33), e houve 5 pausas acima de 5 minutos.
  - Em 2022 a maior pausa de totalização foi de 1 minuto, mas todas as seções fecharam às 17h.
- **Interpretação mais provável:** retenção deliberada da divulgação parcial enquanto havia seções votando até 19h. É a mesma lógica de não divulgar resultados com urnas abertas. A pausa termina 3 minutos após o horário da prorrogação, o que é coerente.
- **Ponto que merece esclarecimento oficial:** a mediana de recebimento foi 20h26, contra 18h44 no 1T e 18h26 em 2022. Apenas 10% das seções estavam totalizadas às 19h38. Isso indica que a transmissão também ficou majoritariamente retida, não só a totalização.
- **Por que o atraso, por si só, não altera o resultado:** o BU é impresso e assinado na seção no encerramento (~17h), antes da transmissão. A integridade pode ser verificada pelos passos 1, 2 e 4 da seção 5.
- **As 45 trocas de líder** acompanham a série de % de Lula: 50,5% (10%) → 49,49% (25%) → 50,12% (50%) → 51,08% → 51,79%. Uma série cumulativa oscilando em torno de 50% gera muitos cruzamentos. A ordem de chegada dependeu da liberação após 19h. O resultado final é a soma dos BUs e independe da ordem.

### (b) Urnas que receberam votos entre 17h e 19h

| Grupo | Urnas | Votos após 17h | Estatística |
|---|---|---|---|
| NORMAL | 469.071 | 0 | — |
| FILA (até ~17h15) | 27.312 | 30.110 | — |
| ESTENDIDA (até 19h) | 2.794 | 4.637 (3.918 entre 17h15 e 19h) | mediana 1 voto por urna; p90 2; máx. 27; 10 urnas com ≥10; nenhuma com ≥30 |

- **Concentração geográfica:** 97% das urnas estendidas estão em RJ (1.181), SP (849), BA (399), PE (198) e PB (86). Essas mesmas urnas já tinham 3,77% de votos após 17h no 1T, o que indica locais com problema crônico de fila.
- **Perfil dos votos na prorrogação comparado ao dia:**
  - Intervalo mediano entre eleitores: 3.088s contra 65s.
  - Intervalos menores que 30s: 0,08% contra 1,54%.
  - Duração mediana do voto: 10s nos dois casos.
  - Sem biometria após falha: 4,95% contra 6,19%.
  - Habilitação pelo mesário: 2,91% contra 4,04%.
  - Única diferença: mais eleitores sem biometria cadastrada (9,37% contra 6,58%; p = 0,001). Isso equivale a cerca de 110 votos.
  - Não há rajadas.
- **Resultado comparado às urnas normais dos mesmos municípios:**
  - Mediana de z_A: 0,005 contra −0,009 (Mann-Whitney p = 0,59).
  - Variação de Lula entre turnos: 7,78 p.p. contra 7,57 p.p.
  - Correlação entre fração de votos na prorrogação e desvio de voto: Spearman 0,0007 (p = 0,80).
  - Nenhuma urna estendida tem z_A forte (0%, contra 0,037% nas normais).
- **Abstenção menor nas estendidas** (z −0,23; −3,22 p.p.) é esperada mecanicamente: a prorrogação existe para permitir que mais pessoas votem.
- **Conclusão:** a prorrogação teve efeito prático mínimo e nenhuma assinatura de manipulação. Uma urna estendida com biometria anômala, entre 21 testáveis, deve ser identificada e conferida.

### (c) Afirmação viral: "+6 mi para Lula nas urnas com voto entre 17h e 19h; +1,8 mi para Flávio nas fechadas às 17h"

**A afirmação é falsa no nível de urna.** Os números só se reproduzem quando se agrega **por zona eleitoral**: nas zonas onde *alguma* urna encerrou após 17h15, Lula tem +6,404 mi; nas demais, Flávio tem +1,974 mi.

1. **Confusão entre zona e urna.** Os "+6 mi" são votos do dia inteiro em 230.998 urnas dessas zonas, não votos dados após 17h. No nível de urna:
   - Urnas com algum voto após 17h (30.105): Lula +0,641 mi.
   - Urnas sem nenhum voto após 17h (469.068): **Lula +3,789 mi**.
   - Urnas com último voto após 17h15 (2.794): Lula +0,091 mi.
2. **Efeito de geografia.** As mesmas zonas já davam Lula +2,756 mi no 1T, sem prorrogação. As outras davam Flávio +4,98 mi. São grandes metrópoles e o Nordeste contra o resto do país.
3. **A virada ocorreu onde não houve voto tardio.**
   - As urnas encerradas até 17h01 (228.708) passaram de Flávio +2,611 mi no 1T para Lula +0,093 mi no 2T. É uma virada de 2,7 mi com apenas 2.054 votos após 17h.
   - No total, 92% da virada nacional ocorreu em urnas sem voto após 17h.
4. **Limite aritmético.** Todos os votos após 17h somam 34.745. Mesmo que fossem todos de Lula, não produziriam 6 mi.
5. **A mesma agregação em 2022 dá o mesmo "padrão".** Por zona: Lula +3,72 mi contra Bolsonaro +1,58 mi. Por local de votação, os locais com voto após 17h favoreceram **Bolsonaro** (−0,947 mi). Pela mesma lógica viral, isso "provaria" fraude a favor dele.
6. **A conclusão depende do nível escolhido.** Em 2026, por município, Lula vence nos dois grupos (+3,885 e +0,545 mi). Por local de votação, também (+0,973 e +3,458 mi). Isso é escolha seletiva do nível de agregação.

### (d) Demais afirmações checadas

- **"Lula cresceu em quase todos os municípios, o que seria impossível."**
  - É verdade: cresceu em 5.698 de 5.757 em % dos válidos e em 5.621 em votos absolutos.
  - Em 2022 Bolsonaro cresceu em 5.590 de 5.751 em votos absolutos.
  - É o padrão normal de 2T: o candidato que absorve mais do eleitorado não decidido cresce de forma quase uniforme. Uma fraude localizada não produziria um crescimento tão difuso.
- **"Congresso e governadores de direita são incompatíveis com a vitória de Lula."**
  - Câmara: 335 de direita em 2026 contra 315 em 2022, quando Lula também venceu.
  - Governadores: 20 contra 13. Senado em 2027: 55 de direita.
  - Voto dividido é rotineiro no Brasil e não constitui evidência.
  - Ressalva: a classificação ideológica do arquivo (por exemplo, PT como "extrema-esquerda") é discutível e irrelevante para a análise forense.
- **"Salto suspeito de Lula no Sul e no Centro-Oeste" (GO +9,3 p.p.).**
  - O 2T de 2026 é quase idêntico ao de 2022:

    | UF | Lula 2T 2026 | Lula 2T 2022 |
    |---|---|---|
    | GO | 40,34% | 41,29% |
    | SC | 30,58% | 30,73% |
    | PR | 37,42% | 37,60% |
    | RS | 42,16% | 43,65% |
    | MT | 33,94% | 34,92% |

  - O "salto" reflete um 1T fragmentado. Em GO, 15,3% dos válidos foram para outros candidatos, com Caiado, ex-governador do estado, na disputa.
- **"Eleitores de direita migraram para Lula."**
  - As estimativas ecológicas são Caiado 36,8% e Renan Santos 36,9% para Lula. Em 2022, Tebet e Ciro se dividiram quase igualmente entre os dois.
  - É plausível, mas incerto. Deve ser confrontado com pesquisas e boca de urna.
- **"Abstenção caiu e quem voltou votou em Lula."**
  - Do eleitorado não válido no 1T, 12,9% foi para Lula e 1,3% para Flávio. Em 2022 foram 2,9% e 4,1%.
  - A abstenção caiu de 21,1% para 19,2%; houve +2,96 mi votantes e −1,82 mi brancos e nulos.
  - **É o traço mais distintivo de 2026**, e também a razão pela qual a fatia de Flávio nos válidos caiu levemente em várias UFs do Nordeste (CE, MA, PB, PE, RN, SE, AL) e ficou estável no RJ.
  - Esse aumento de comparecimento é difuso:
    - seções com abstenção muito abaixo do esperado: 287, contra 602 em 2022;
    - vínculo entre queda da abstenção e desvio pró-Lula: −0,020, contra −0,035 em 2022;
    - os votos adicionais vieram em grande parte com digital (cerca de 2,7 mi ou mais de 2,96 mi).
  - É compatível com mobilização real. A verificação definitiva é o passo 6 da seção 5.
- **"Minas virou."** É a única UF com troca de líder entre turnos: Lula com 50,43%, contra 50,20% em 2022. Em 2022 o Amapá virou no sentido oposto. É normal.
- **"Virada na apuração / 45 trocas de liderança."** É efeito da ordem de chegada dos BUs após a liberação às 19h, como explicado no item (a). Não é evidência.

**Síntese:** nenhuma das afirmações virais encontra suporte nos dados seção a seção. As poucas anomalias reais são procedimentais e localizadas, sobretudo a seção MG 46256/131/46 e as 7 divergências entre log e BU. Elas devem ser esclarecidas individualmente, mas, somadas, não alcançam ordem de grandeza capaz de afetar uma margem de 4,43 milhões de votos.