# SISTEMA
Você é um estatístico especializado em forense eleitoral, revisando uma análise seção por seção
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
verificações concretas (ex.: conferir boletins impressos, RDV, log completo de seções específicas).

# USUÁRIO
Abaixo estão os resultados. Escreva, em português, um parecer com:
1. Conclusão principal em 3–5 frases: 2026 apresenta mais/menos/os mesmos sinais que 2022, e o que isso indica.
2. Teste por teste (A votação, B abstenção/brancos/nulos, C fluxo após 17h, D biometria, E impressão digital):
   o que o número mostra, comparação com 2022 e a interpretação mais provável.
3. Seções ou grupos de seções que merecem verificação individual, e por quê (cite UF/município/zona/seção).
4. Limitações e possíveis vieses da metodologia (incluindo sensibilidade do teste A à especificação do modelo).
5. Próximos passos de verificação.
6. Análises adicionais: (a) a interrupção do recebimento/totalização de BUs entre ~17h07 e 19h03 no 2º turno, no contexto
   da prorrogação da votação até 19h; (b) as urnas que receberam votos entre 17h e 19h; (c) a afirmação viral de que nessas
   urnas Lula teve +6 milhões e nas fechadas às 17h Flávio teve +1,8 milhão; (d) as demais afirmações checadas.
Seja direto; use números.

## resumo_2026.json
```json
{
  "ano": 2026,
  "secoes": 499248,
  "secoes_instaveis_excluidas_A_B_D1": 700,
  "secoes_com_log_2t": 499177,
  "secoes_com_log_1t": 499176,
  "integridade_1t": {
    "secoes_comparadas": 499176,
    "secoes_log_diferente_do_bu": 9,
    "soma_diferencas": -59
  },
  "integridade_2t": {
    "secoes_comparadas": 499177,
    "secoes_log_diferente_do_bu": 7,
    "soma_diferencas": 250
  },
  "A_sensibilidade": {
    "logit+splines, por UF, efeito fixo de município (principal)": {
      "n_forte": 268,
      "pro_13": 212,
      "pro_22": 56
    },
    "logit+splines, por UF, efeito fixo de zona": {
      "n_forte": 308,
      "pro_13": 223,
      "pro_22": 85
    },
    "logit+splines, por UF, efeito fixo de local de votação": {
      "n_forte": 351,
      "pro_13": 226,
      "pro_22": 125
    },
    "linear simples nas proporções, efeito fixo de município": {
      "n_forte": 399,
      "pro_13": 121,
      "pro_22": 278
    }
  },
  "A_votacao": {
    "secoes_testadas": 498344,
    "r2_modelo": 0.9298,
    "sobredispersao": 0.618,
    "variaveis_1t": [
      "p13_1",
      "p14_1",
      "p22_1",
      "p55_1",
      "p70_1",
      "p_abst_1",
      "p_branco_1",
      "p_nulo_1",
      "p_outros_1",
      "outros"
    ],
    "n_forte": 268,
    "pct_forte": 0.0538,
    "forte_pro_13": 212,
    "forte_pro_22": 56,
    "n_abs_z_maior_6": 29,
    "media_z": 0.0156,
    "teste_simetria_binomial_p": 1.5548500555482181e-22,
    "curtose": 2.243,
    "forte_em_local_indigena": 34,
    "pct_secoes_pais_em_local_indigena": 0.214,
    "fora_indigena_pro_13": 180,
    "fora_indigena_pro_22": 54
  },
  "B_abst": {
    "secoes_testadas": 498423,
    "r2_modelo": 0.7565,
    "sobredispersao": 0.836,
    "n_forte_alta": 795,
    "n_forte_baixa": 287,
    "pct_forte": 0.2171,
    "media_1t": 0.20816,
    "media_2t": 0.19099
  },
  "B_branco": {
    "secoes_testadas": 498423,
    "r2_modelo": 0.154,
    "sobredispersao": 0.958,
    "n_forte_alta": 497,
    "n_forte_baixa": 0,
    "pct_forte": 0.0997,
    "media_1t": 0.01819,
    "media_2t": 0.01104
  },
  "B_nulo": {
    "secoes_testadas": 498423,
    "r2_modelo": 0.2075,
    "sobredispersao": 0.981,
    "n_forte_alta": 547,
    "n_forte_baixa": 0,
    "pct_forte": 0.1097,
    "media_1t": 0.02929,
    "media_2t": 0.02105
  },
  "C_fluxo_pos17": {
    "secoes_testadas": 499029,
    "pct_votos_pos17_2t": 0.0271,
    "pct_votos_pos17_1t": 2.974,
    "dist_2t": {
      "total_votos_pos17": 34747,
      "secoes_com_pos17": 30106,
      "secoes_ge10": 17,
      "secoes_ge30": 2,
      "max": 39
    },
    "dist_1t": {
      "total_votos_pos17": 3725600,
      "secoes_com_pos17": 222314,
      "secoes_ge10": 104807,
      "secoes_ge30": 47729,
      "max": 177
    },
    "n_sig_fdr_ge10": 12,
    "n_ritmo_pos17_acima_pico_dia": 6,
    "n_secoes_com_rajadas_pos17_ge5": 0,
    "mediana_intervalo_entre_votos_dia_s": 71.0,
    "mediana_intervalo_entre_votos_pos17_s": 602.0,
    "votos_antes_8h": 0,
    "secoes_ultimo_voto_apos_19h": 11
  },
  "D_biometria": {
    "D1_entre_turnos": {
      "secoes_testadas": 498341,
      "sobredispersao": 0.888,
      "pct_manual_1t": 6.66,
      "pct_manual_2t": 6.732,
      "n_forte_aumento": 152,
      "n_forte_queda": 300
    },
    "D2_fim_do_dia": {
      "secoes_testadas": 371630,
      "pct_manual_ate16h": 6.795,
      "pct_manual_16h_em_diante": 5.576,
      "n_sig_fdr": 11
    },
    "secoes_pct_manual_2t_acima_30": 348,
    "secoes_pct_manual_2t_acima_50": 97
  },
  "E_impressao_digital": {
    "secoes": 498330,
    "nota": "coeficiente = variação do z_A (pró-Lula > 0) para +1 desvio-padrão do indicador; efeito fixo de município",
    "coeficientes": {
      "d_pct_manual": -0.0022,
      "pct_pos17_2": 0.0137,
      "d_p_abst": -0.0195
    },
    "correlacoes_simples": {
      "d_pct_manual": -0.0016,
      "pct_pos17_2": 0.013,
      "d_p_abst": -0.0124
    }
  },
  "sinais_por_motivo": {
    "voto 2T muito acima do esperado p/ Lula": 212,
    "voto 2T muito acima do esperado p/ Flávio": 56,
    "abst 2T fora do esperado": 1082,
    "branco 2T fora do esperado": 497,
    "nulo 2T fora do esperado": 547,
    "excesso de votos após 17h": 12,
    "ritmo após 17h acima do pico do dia": 6,
    "rajada de votos <30s após 17h": 0,
    "salto de votos sem biometria vs 1T": 152,
    "sem biometria concentrado no fim do dia": 11
  },
  "secoes_com_1_sinal": 2479,
  "secoes_com_2+_sinais": 47,
  "secoes_com_3+_sinais": 2
}
```

## resumo_2022.json
```json
{
  "ano": 2022,
  "secoes": 472075,
  "secoes_instaveis_excluidas_A_B_D1": 692,
  "secoes_com_log_2t": 471983,
  "secoes_com_log_1t": 471859,
  "integridade_1t": {
    "secoes_comparadas": 471859,
    "secoes_log_diferente_do_bu": 100,
    "soma_diferencas": -2371
  },
  "integridade_2t": {
    "secoes_comparadas": 471983,
    "secoes_log_diferente_do_bu": 53,
    "soma_diferencas": -912
  },
  "A_sensibilidade": {
    "logit+splines, por UF, efeito fixo de município (principal)": {
      "n_forte": 309,
      "pro_13": 175,
      "pro_22": 134
    },
    "logit+splines, por UF, efeito fixo de zona": {
      "n_forte": 320,
      "pro_13": 168,
      "pro_22": 152
    },
    "logit+splines, por UF, efeito fixo de local de votação": {
      "n_forte": 397,
      "pro_13": 221,
      "pro_22": 176
    },
    "linear simples nas proporções, efeito fixo de município": {
      "n_forte": 293,
      "pro_13": 114,
      "pro_22": 179
    }
  },
  "A_votacao": {
    "secoes_testadas": 471190,
    "r2_modelo": 0.9336,
    "sobredispersao": 0.585,
    "variaveis_1t": [
      "p12_1",
      "p13_1",
      "p15_1",
      "p22_1",
      "p30_1",
      "p44_1",
      "p_abst_1",
      "p_branco_1",
      "p_nulo_1",
      "p_outros_1",
      "outros"
    ],
    "n_forte": 309,
    "pct_forte": 0.0656,
    "forte_pro_13": 175,
    "forte_pro_22": 134,
    "n_abs_z_maior_6": 42,
    "media_z": -0.0038,
    "teste_simetria_binomial_p": 0.022720716177490594,
    "curtose": 1.874,
    "forte_em_local_indigena": 33,
    "pct_secoes_pais_em_local_indigena": 0.154,
    "fora_indigena_pro_13": 147,
    "fora_indigena_pro_22": 129
  },
  "B_abst": {
    "secoes_testadas": 471269,
    "r2_modelo": 0.8185,
    "sobredispersao": 0.768,
    "n_forte_alta": 591,
    "n_forte_baixa": 602,
    "pct_forte": 0.2531,
    "media_1t": 0.20823,
    "media_2t": 0.20558
  },
  "B_branco": {
    "secoes_testadas": 471269,
    "r2_modelo": 0.1577,
    "sobredispersao": 0.962,
    "n_forte_alta": 414,
    "n_forte_baixa": 0,
    "pct_forte": 0.0878,
    "media_1t": 0.01568,
    "media_2t": 0.01404
  },
  "B_nulo": {
    "secoes_testadas": 471269,
    "r2_modelo": 0.2624,
    "sobredispersao": 0.983,
    "n_forte_alta": 607,
    "n_forte_baixa": 2,
    "pct_forte": 0.1292,
    "media_1t": 0.02807,
    "media_2t": 0.03123
  },
  "C_fluxo_pos17": {
    "secoes_testadas": 471860,
    "pct_votos_pos17_2t": 0.0333,
    "pct_votos_pos17_1t": 3.5092,
    "dist_2t": {
      "total_votos_pos17": 41413,
      "secoes_com_pos17": 34980,
      "secoes_ge10": 85,
      "secoes_ge30": 8,
      "max": 50
    },
    "dist_1t": {
      "total_votos_pos17": 4338575,
      "secoes_com_pos17": 215697,
      "secoes_ge10": 114045,
      "secoes_ge30": 56080,
      "max": 234
    },
    "n_sig_fdr_ge10": 36,
    "n_ritmo_pos17_acima_pico_dia": 40,
    "n_secoes_com_rajadas_pos17_ge5": 3,
    "mediana_intervalo_entre_votos_dia_s": 73.0,
    "mediana_intervalo_entre_votos_pos17_s": 472.0,
    "votos_antes_8h": 0,
    "secoes_ultimo_voto_apos_19h": 2
  },
  "D_biometria": {
    "D1_entre_turnos": {
      "secoes_testadas": 471027,
      "sobredispersao": 0.955,
      "pct_manual_1t": 8.728,
      "pct_manual_2t": 8.062,
      "n_forte_aumento": 1008,
      "n_forte_queda": 1123
    },
    "D2_fim_do_dia": {
      "secoes_testadas": 374090,
      "pct_manual_ate16h": 8.147,
      "pct_manual_16h_em_diante": 6.617,
      "n_sig_fdr": 42
    },
    "secoes_pct_manual_2t_acima_30": 3998,
    "secoes_pct_manual_2t_acima_50": 320
  },
  "E_impressao_digital": {
    "secoes": 471019,
    "nota": "coeficiente = variação do z_A (pró-Lula > 0) para +1 desvio-padrão do indicador; efeito fixo de município",
    "coeficientes": {
      "d_pct_manual": -0.0,
      "pct_pos17_2": -0.0039,
      "d_p_abst": -0.0353
    },
    "correlacoes_simples": {
      "d_pct_manual": -0.0006,
      "pct_pos17_2": -0.0039,
      "d_p_abst": -0.023
    }
  },
  "sinais_por_motivo": {
    "voto 2T muito acima do esperado p/ Lula": 175,
    "voto 2T muito acima do esperado p/ Flávio": 134,
    "abst 2T fora do esperado": 1193,
    "branco 2T fora do esperado": 414,
    "nulo 2T fora do esperado": 609,
    "excesso de votos após 17h": 36,
    "ritmo após 17h acima do pico do dia": 40,
    "rajada de votos <30s após 17h": 3,
    "salto de votos sem biometria vs 1T": 1008,
    "sem biometria concentrado no fim do dia": 42
  },
  "secoes_com_1_sinal": 3446,
  "secoes_com_2+_sinais": 102,
  "secoes_com_3+_sinais": 4
}
```

## 80 seções de 2026 com mais sinais (CSV ';')
```
uf;cd_municipio;nr_zona;nr_secao;z_A_voto;z_B_abst;z_B_branco;z_B_nulo;p_C_pos17;C_pos17_sig;C_ritmo_pos17_acima_pico;C_rajadas_pos17;z_D_manual_entre_turnos;p_D_manual_fim_dia;D_manual_fim_dia_sig;n_sinais;motivos;nm_municipio;nm_local;local_indigena;aptos_2;comparecimento_1;comparecimento_2;p13_1;p22_1;p13_2;p22_2;p_abst_1;p_abst_2;p_branco_1;p_branco_2;p_nulo_1;p_nulo_2;n_votos_2;n_pos17_1;n_pos17_2;taxa_dia_2;taxa_pos17_2;pico_hora_dia_2;pct_manual_1;pct_manual_2;pct_manual_dia_2;pct_manual_pos17_2;pct_semcad_2;contingencia_2;n_suspensa_2;t_abre_b_2;t_encerra_b_2;modelo_urna_2
AM;2399;45;63;28.7344;4.1864;-1.1074;4.3707;1.0;false;false;0;1.1718;;false;3;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; nulo 2T fora do esperado; ";IPIXUNA;E. M. MARECHAL CANDIDO RONDON ALDEIA PIAU;true;335;227;197;0.649;0.2933;0.9882;0.0118;0.3224;0.4119;0.0;0.0;0.0837;0.1421;197;81;0;21.8896;;43;0.0264;0.0406;0.0406;NaN;0.1675;true;1;28801;61273;UE 2020
AM;2259;8;119;5.8104;7.3642;-0.6757;5.7835;1.0;false;false;0;0.4585;;false;3;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; nulo 2T fora do esperado; ";COARI;E. M. HUMBELINA DE SOUZA;false;454;302;236;0.8658;0.1275;0.9498;0.0502;0.3348;0.4802;0.0066;0.0;0.0066;0.072;236;61;0;26.223;;63;0.0497;0.0551;0.0551;NaN;0.0424;false;0;28801;61247;UE 2020
AC;1554;3;160;-13.2164;-2.6228;-0.5364;5.2998;1.0;false;false;0;-0.6087;;false;2;"voto 2T muito acima do esperado p/ Flávio; nulo 2T fora do esperado; ";MANOEL URBANO;POSTO DE SAÚDE (ALDEIA BUAÇÚ);true;236;170;173;0.6707;0.3293;0.3158;0.6842;0.2857;0.2669;0.0;0.0;0.0176;0.1214;173;0;0;19.2228;;44;0.1353;0.1156;0.1156;NaN;0.0925;false;0;28801;61301;UE 2020
AM;2097;18;37;12.0963;2.8497;1.3696;8.0749;1.0;false;false;0;-0.0427;;false;2;"voto 2T muito acima do esperado p/ Lula; nulo 2T fora do esperado; ";BARCELOS;E. M. MANUEL SALES;false;377;231;190;0.1713;0.7917;0.5419;0.4581;0.3873;0.496;0.0043;0.0105;0.0606;0.1737;190;78;0;21.2067;;47;0.0563;0.0526;0.0526;NaN;0.0;false;0;28946;61212;UE 2022
CE;13730;120;361;7.1725;0.8244;5.1565;-0.3726;1.0;false;false;0;-0.3969;0.6244;false;2;"voto 2T muito acima do esperado p/ Lula; branco 2T fora do esperado; ";CAUCAIA;E.E.I.E.F. NOSSA SENHORA DA CONCEICÃO;false;349;312;313;0.8133;0.1633;0.92;0.08;0.106;0.1032;0.0128;0.0288;0.0256;0.0128;313;69;0;34.7799;;71;0.0513;0.0479;0.0479;NaN;0.0543;false;0;28802;61226;UE 2022
AM;2216;21;76;6.9612;4.9067;0.0923;-1.1543;1.0;false;false;0;1.8103;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";CARAUARI;COM. ROQUE - E. M. SEBASTIÃO SALVINO CARNEIRO;false;364;310;270;0.7974;0.1765;0.9211;0.0789;0.1484;0.2582;0.0032;0.0037;0.0097;0.0111;270;43;0;30.0009;;50;0.0258;0.0519;0.0519;NaN;0.0519;false;0;28801;61277;UE 2022
SP;71072;2;532;-6.5769;-5.6366;2.1366;-1.7699;1.0;false;false;0;0.2699;0.6711;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";SÃO PAULO;COLÉGIO EQUIPE;false;387;264;323;0.5898;0.2812;0.5623;0.4377;0.3178;0.1654;0.0076;0.0217;0.0227;0.0093;323;0;0;35.89;;62;0.0909;0.096;0.096;NaN;0.0093;false;0;28801;61234;UE 2015
SP;71072;2;539;-6.5595;-5.8593;-1.3635;-0.8353;1.0;false;false;0;0.5298;;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";SÃO PAULO;COLÉGIO EQUIPE;false;385;253;317;0.6829;0.2114;0.641;0.359;0.3429;0.1766;0.0158;0.0032;0.0119;0.0126;317;0;0;35.2233;;51;0.0751;0.0852;0.0852;NaN;0.0505;false;0;28801;61260;UE 2015
PA;5835;106;330;6.5221;-7.1671;-0.3211;0.3567;0.9999;false;false;0;1.0414;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";PARAUAPEBAS;EMEF INDÍGENA BEP KAROTI XIKRIN;true;325;128;212;0.9844;0.0156;1.0;0.0;0.6062;0.3477;0.0;0.0;0.0;0.0;212;8;1;23.4452;12.0;47;0.0234;0.0425;0.0427;0.0;0.0;false;0;28801;61703;UE 2020
SP;71072;2;491;-6.4856;-5.4454;0.0453;-0.5993;1.0;false;false;0;-0.2631;1.0;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";SÃO PAULO;COLÉGIO EQUIPE;false;387;257;317;0.5569;0.3577;0.513;0.487;0.3359;0.1809;0.0117;0.0095;0.0311;0.0189;317;0;0;35.2244;;52;0.0817;0.0757;0.0757;NaN;0.0032;false;0;28802;61295;UE 2015
AM;2054;42;29;6.0673;-4.134;0.4919;0.139;1.0;false;false;0;-0.8683;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";ATALAIA DO NORTE;E. M. BRAZ TUKUNA;true;441;289;335;0.9648;0.0141;1.0;0.0;0.3447;0.2404;0.0;0.003;0.0173;0.0269;335;60;1;37.2156;12.0;55;0.0069;0.006;0.006;0.0;0.1463;false;0;28891;61295;UE 2022
PR;77917;30;37;-6.0487;18.0556;-0.1071;-0.348;1.0;false;false;0;0.2504;;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";PRUDENTÓPOLIS;PAVILHÃO DA IGREJA DE PATOS VELHOS;false;339;264;155;0.2738;0.6865;0.1842;0.8158;0.2212;0.5428;0.0114;0.0065;0.0341;0.0129;155;0;0;17.2228;;38;0.0606;0.0645;0.0645;NaN;0.0065;false;0;28801;61230;UE 2022
AM;2410;3;118;5.918;4.7505;-0.3683;0.124;1.0;false;false;0;-0.1958;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";ITACOATIARA;GRUPO ESCOLAR PRIMAVERA;false;227;177;143;0.8046;0.1839;0.9214;0.0786;0.2203;0.37;0.0;0.0;0.0169;0.021;143;11;0;15.8894;;30;0.0508;0.049;0.049;NaN;0.0699;false;0;28801;61207;UE 2022
SP;71072;2;506;-5.9006;-5.0075;1.0799;0.3858;1.0;false;false;0;0.0434;;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";SÃO PAULO;COLÉGIO EQUIPE;false;390;248;307;0.525;0.3583;0.5;0.5;0.3641;0.2128;0.0202;0.0195;0.0121;0.0228;307;0;0;34.1132;;61;0.1169;0.1173;0.1173;NaN;0.0293;false;0;28802;61294;UE 2015
PA;5452;53;218;5.6098;-6.9069;-0.3876;-1.283;1.0;false;false;0;0.5393;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";SÃO FÉLIX DO XINGU;EM INDIGENA CAPITÃO BEP NOX;true;318;221;273;0.9907;0.0046;1.0;0.0;0.305;0.1415;0.0;0.0;0.0226;0.0;273;26;0;30.3343;;51;0.0045;0.011;0.011;NaN;0.1136;false;0;28801;61290;UE 2022
AM;2097;18;39;-5.3417;4.3542;0.525;3.3539;1.0;false;false;0;0.4869;;false;2;"voto 2T muito acima do esperado p/ Flávio; abst 2T fora do esperado; ";BARCELOS;E. M. MANUEL SALES;false;173;107;75;0.2771;0.6627;0.1897;0.8103;0.3815;0.5665;0.0187;0.0133;0.2056;0.2133;75;0;0;8.3786;;29;0.0093;0.0133;0.0133;NaN;0.0;false;0;28975;61364;UE 2022
MT;91979;16;86;5.1839;-4.7066;-0.7773;1.2103;1.0;false;false;0;2.4709;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";SANTA TEREZINHA;ESCOLA ESTADUAL INDÍGENA ITXALÁ;true;317;282;297;0.9679;0.025;0.9966;0.0034;0.1104;0.0631;0.0;0.0;0.0071;0.0101;297;32;0;33.001;;75;0.039;0.0673;0.0673;NaN;0.0505;false;0;28801;61290;UE 2022
AC;1040;4;223;4.9138;7.5333;1.3561;-0.0805;1.0;false;false;0;-0.4386;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";MARECHAL THAUMATURGO;ESCOLA JOSÉ PINTO PEREIRA;false;270;232;127;0.2379;0.7357;0.3884;0.6116;0.1407;0.5296;0.0043;0.0157;0.0172;0.0315;127;0;0;14.1115;;46;0.0991;0.0866;0.0866;NaN;0.0787;false;0;28801;61441;UE 2022
AM;2259;8;173;4.7241;5.3;1.0241;-0.639;1.0;false;false;0;-0.173;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";COARI;E. M. MANOEL SOARES DA FONSECA;false;319;168;133;0.8;0.1879;0.9154;0.0846;0.4734;0.5831;0.0;0.0075;0.0179;0.015;133;0;0;14.7782;;45;0.0357;0.0301;0.0301;NaN;0.0752;false;0;28801;61438;UE 2020
AM;2836;19;34;4.7074;4.843;-0.0818;-0.2704;1.0;false;false;0;0.0953;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";SÃO GABRIEL DA CACHOEIRA;E. M. DA FOZ DO IÇANA;true;417;303;263;0.9037;0.0963;0.9538;0.0462;0.2734;0.3693;0.0;0.0;0.0066;0.0114;263;35;0;29.2231;;54;0.033;0.0342;0.0342;NaN;0.057;false;0;28801;61217;UE 2022
SC;81990;22;69;-4.6958;-0.8851;-0.2372;4.9453;1.0;false;false;0;-1.4859;;false;2;"voto 2T muito acima do esperado p/ Flávio; nulo 2T fora do esperado; ";MAFRA;ESCOLA ISOLADA PASSO DA CRUZ;false;283;227;239;0.3249;0.6091;0.3134;0.6866;0.1979;0.1555;0.1013;0.0293;0.0308;0.0628;239;0;0;26.5564;;55;0.2026;0.1506;0.1506;NaN;0.0167;true;0;28801;61216;UE 2013
AM;2593;49;27;4.5797;6.0576;-0.2842;-0.5605;1.0;false;false;0;0.002;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";MARAÃ;C. E. SÃO FRANCISCO DO CAPIVARA;false;238;156;113;0.7434;0.2434;0.8829;0.1171;0.3445;0.5252;0.0064;0.0;0.0192;0.0177;113;0;0;12.5559;;35;0.0385;0.0354;0.0354;NaN;0.0531;false;0;28801;61318;UE 2022
CE;15458;54;183;4.5044;4.5569;0.2446;0.8881;1.0;false;false;0;-0.3783;0.5324;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";SANTA QUITÉRIA;E. E. F. ABÍLIO MESQUITA MARTINS;false;222;190;172;0.8811;0.0811;0.9583;0.0417;0.1441;0.2252;0.0053;0.0058;0.0211;0.0174;172;0;0;19.1117;;43;0.0421;0.0407;0.0407;NaN;0.0407;false;0;28801;61221;UE 2020
BA;35211;187;30;4.4263;4.0123;-0.9056;3.6051;1.0;false;false;0;-1.6346;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";FORMOSA DO RIO PRETO;GRUPO ESCOLAR CEL. FRANCISCO ÂNGELO;false;258;184;170;0.65;0.3333;0.7744;0.2256;0.2868;0.3411;0.0054;0.0;0.0163;0.0353;170;0;0;18.8895;;37;0.0707;0.0353;0.0353;NaN;0.0353;false;0;28801;61368;UE 2022
AM;2550;68;511;4.3317;9.2991;0.0835;-0.2744;1.0;false;false;0;0.8316;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";MANAUS;E. M. PROF. ELIZABETH SIQUEIRA FERREIRA;false;230;195;153;0.7143;0.2222;0.8456;0.1544;0.1522;0.3348;0.0051;0.0065;0.0256;0.0196;153;0;0;17.0005;;41;0.041;0.0588;0.0588;NaN;0.0327;false;0;28801;61227;UE 2020
AP;6122;7;181;4.2337;5.2941;-0.4741;-1.4782;1.0;false;false;0;1.4721;1.0;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";VITÓRIA DO JARI;ESCOLA ESTADUAL JARILÂNDIA;false;262;228;165;0.6682;0.3;0.8061;0.1939;0.1298;0.3702;0.0044;0.0;0.0307;0.0;165;0;0;18.3339;;36;0.0263;0.0485;0.0485;NaN;0.0061;false;0;28801;61207;UE 2020
MA;7935;15;326;4.2059;4.0384;1.0109;0.992;1.0;false;false;0;2.1209;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";GRAJAÚ;ESCOLA INDÍGENA YRIKAMIRI;true;189;146;130;0.913;0.0797;0.976;0.024;0.2275;0.3122;0.0;0.0077;0.0548;0.0308;130;0;0;14.4449;;36;0.0205;0.0692;0.0692;NaN;0.1846;false;0;28801;61372;UE 2022
PA;5355;83;188;4.0575;5.7099;0.2099;1.4102;1.0;false;false;0;0.3544;;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";SANTARÉM;EMEF SÃO SEBASTIÃO;false;204;148;120;0.7746;0.1901;0.8966;0.1034;0.2745;0.4118;0.0135;0.0083;0.027;0.025;120;0;0;13.3432;;34;0.0338;0.0417;0.0417;NaN;0.0;false;0;28824;61371;UE 2022
PA;5010;22;69;4.036;4.001;-0.5946;-1.7547;1.0;false;false;0;1.9517;0.6932;false;2;"voto 2T muito acima do esperado p/ Lula; abst 2T fora do esperado; ";ÓBIDOS;EMEIF NOSSA SENHORA DE NAZARÉ;false;211;182;156;0.7778;0.2047;0.8846;0.1154;0.1374;0.2607;0.0055;0.0;0.0549;0.0;156;0;0;17.3344;;50;0.1813;0.2564;0.2564;NaN;0.0192;false;0;28802;61228;UE 2015
BA;36854;180;149;-2.2852;-4.7523;1.8776;0.4352;1.0;false;false;0;14.0566;0.1616;false;2;"abst 2T fora do esperado; salto de votos sem biometria vs 1T; ";LAURO DE FREITAS;ESCOLA MUNICIPAL DA VILA PRAIANA;false;391;253;319;0.6203;0.3291;0.6513;0.3487;0.3529;0.1841;0.0198;0.0188;0.0435;0.0282;319;94;1;35.3344;12.0;59;0.1621;0.6865;0.6855;1.0;0.0752;true;0;28801;61481;UE 2013
AC;1554;3;100;-1.8097;-4.1859;-0.6381;8.5894;1.0;false;false;0;0.0803;;false;2;"abst 2T fora do esperado; nulo 2T fora do esperado; ";MANOEL URBANO;POSTO DE SAÚDE (ALDEIA BUAÇÚ);true;243;185;195;0.382;0.618;0.3438;0.6562;0.2387;0.1975;0.0;0.0;0.0378;0.1795;195;0;0;21.6673;;45;0.0703;0.0718;0.0718;NaN;0.1026;false;0;28801;61264;UE 2020
BA;34290;127;55;1.4577;-5.3342;-0.6782;1.7159;1.0;false;false;0;4.0171;0.2714;false;2;"abst 2T fora do esperado; salto de votos sem biometria vs 1T; ";CANDEIAS;ESCOLA MUNICIPAL JULIETA VIANA;false;387;259;324;0.7927;0.1585;0.8673;0.1327;0.3307;0.1628;0.0154;0.0062;0.0347;0.0401;324;82;0;36.0011;;61;0.0193;0.0957;0.0957;NaN;0.0679;false;0;28801;61531;UE 2013
SP;64750;310;303;1.3159;0.6885;0.8268;-0.778;0.0;true;true;4;0.931;0.0085;false;2;"excesso de votos após 17h; ritmo após 17h acima do pico do dia; ";GUARUJÁ;E.M. PROFª JACIREMA DOS SANTOS FORTES;false;375;274;280;0.4157;0.5294;0.5185;0.4815;0.2693;0.2533;0.0365;0.0214;0.0328;0.0143;280;0;10;30.0009;64.5161;41;0.0438;0.0607;0.0556;0.2;0.0679;true;0;28801;61799;UE 2020
AL;27855;54;307;-1.2493;-4.3805;4.9187;0.1152;1.0;false;false;0;0.5601;0.7512;false;2;"abst 2T fora do esperado; branco 2T fora do esperado; ";MACEIÓ;E.M. PROFA. HÉVIA VALÉRIA MAIA AMORIM;false;489;361;411;0.4428;0.509;0.491;0.509;0.2618;0.1595;0.0194;0.0316;0.0609;0.0268;411;101;0;45.7457;;72;0.0526;0.0633;0.0633;NaN;0.0195;false;0;28856;61249;UE 2022
RS;87173;118;143;1.1698;-0.0263;1.6517;0.6014;1.0;false;false;0;9.9505;0.0;true;2;"salto de votos sem biometria vs 1T; sem biometria concentrado no fim do dia; ";IVOTI;E.M.E.F. JARDIM PANORÂMICO;false;372;328;331;0.2578;0.6491;0.3188;0.6812;0.1183;0.1102;0.003;0.0151;0.0152;0.0181;331;0;0;36.7789;;59;0.1128;0.423;0.423;NaN;0.0272;true;2;28801;61587;UE 2013
CE;13510;32;189;-0.9609;0.1184;0.2527;-0.6369;1.0;false;false;0;4.1735;0.0;true;2;"salto de votos sem biometria vs 1T; sem biometria concentrado no fim do dia; ";CAMOCIM;POLO EDUCACIONAL JOSE RODRIGUES ALEXANDRINO - PEDRA BRANCA;false;318;262;268;0.7787;0.1598;0.8231;0.1769;0.1761;0.1572;0.0305;0.0149;0.0382;0.0149;268;32;0;30.4497;;56;0.1412;0.2799;0.2799;NaN;0.0448;true;0;29515;61317;UE 2013
PR;77917;30;122;-0.8423;4.2372;-0.3125;4.2621;1.0;false;false;0;-0.0273;;false;2;"abst 2T fora do esperado; nulo 2T fora do esperado; ";PRUDENTÓPOLIS;PAVILHÃO DA IGREJA BRASILEIRA DE HERVAL FRAQUEZA;false;152;128;111;0.16;0.704;0.1942;0.8058;0.1579;0.2697;0.0156;0.009;0.0078;0.0631;111;0;0;12.3337;;26;0.1016;0.0991;0.0991;NaN;0.0;false;0;28801;61484;UE 2022
BA;38873;36;199;-0.7586;0.1239;-0.6598;-0.8763;0.0;true;true;1;-1.5254;0.8125;false;2;"excesso de votos após 17h; ritmo após 17h acima do pico do dia; ";SÃO MIGUEL DAS MATAS;ESCOLA MUNICIPAL PROFESSORA MARLENE SANTOS;false;260;228;234;0.7752;0.1881;0.7835;0.2165;0.1231;0.1;0.0219;0.0043;0.0219;0.0085;234;3;22;23.9;48.4108;40;0.1184;0.0812;0.0802;0.0909;0.0256;true;10;29267;67856;UE 2020
SP;64777;394;417;0.7424;0.1511;-1.3071;2.2114;1.0;false;false;0;8.8949;0.0;true;2;"salto de votos sem biometria vs 1T; sem biometria concentrado no fim do dia; ";GUARULHOS;EE. PASTOR E VEREADOR ANTONIO GROTKOWSKI;false;390;311;317;0.453;0.4077;0.5709;0.4291;0.2026;0.1872;0.0257;0.0063;0.0514;0.0599;317;0;0;35.2233;;48;0.0418;0.2713;0.2713;NaN;0.0158;false;0;28801;61223;UE 2013
AM;2410;3;134;-0.7156;2.7385;5.9837;4.0978;1.0;false;false;0;0.1339;;false;2;"branco 2T fora do esperado; nulo 2T fora do esperado; ";ITACOATIARA;E. M. BENJAMIM CONSTANT;false;303;235;205;0.5598;0.3828;0.6185;0.3815;0.2244;0.3234;0.0128;0.0439;0.0979;0.1122;205;0;0;22.7785;;42;0.0298;0.0341;0.0341;NaN;0.0195;false;0;28801;61427;UE 2022
PE;23078;38;55;0.6539;1.977;0.1676;-0.0464;0.0;true;true;0;1.7962;0.9759;false;2;"excesso de votos após 17h; ritmo após 17h acima do pico do dia; ";ÁGUA PRETA;COLEGIO MUNICIPAL TEREZINHA  PESSOA DE QUEIROZ;false;273;231;224;0.6909;0.2773;0.7431;0.2569;0.1538;0.1795;0.013;0.0089;0.0346;0.0179;224;0;20;22.6674;52.4781;44;0.0996;0.1518;0.1618;0.05;0.0536;false;0;28801;62899;UE 2013
AM;2399;45;52;0.5368;4.4165;-1.2246;9.8916;1.0;false;false;0;1.0736;;false;2;"abst 2T fora do esperado; nulo 2T fora do esperado; ";IPIXUNA;E. M. MARECHAL CANDIDO RONDON ALDEIA PIAU;true;333;227;196;0.86;0.045;0.965;0.035;0.3183;0.4114;0.0;0.0;0.1189;0.2704;196;64;0;21.7784;;41;0.0661;0.0867;0.0867;NaN;0.0561;false;1;28801;61233;UE 2020
AC;1040;4;326;-0.3925;-4.5841;-0.6819;4.3985;1.0;false;false;0;-1.3074;;false;2;"abst 2T fora do esperado; nulo 2T fora do esperado; ";MARECHAL THAUMATURGO;ESCOLA INDIGENA BOA VISTA;true;279;206;190;0.9901;0.0099;0.9885;0.0115;0.2616;0.319;0.0;0.0;0.0146;0.0842;190;0;0;21.2159;;46;0.0485;0.0263;0.0263;NaN;0.0526;false;0;28960;61207;UE 2022
CE;14354;72;96;-0.3685;-2.2504;-0.1318;-0.0557;0.0;true;true;0;-0.4278;0.866;false;2;"excesso de votos após 17h; ritmo após 17h acima do pico do dia; ";JAGUARETAMA;UNIDADE BÁSICA DE SAÚDE JOAQUIM SIMÃO DE MELO;false;92;82;88;0.8442;0.1429;0.8605;0.1395;0.1087;0.0435;0.0;0.0;0.061;0.0227;88;0;14;8.2225;44.1718;18;0.2317;0.2159;0.2297;0.1429;0.0568;true;4;28801;62492;UE 2015
AC;1074;4;415;0.3652;4.1236;4.0006;1.8375;1.0;false;false;0;-0.0017;;false;2;"abst 2T fora do esperado; branco 2T fora do esperado; ";CRUZEIRO DO SUL;ESCOLA RAINHA DA FLORESTA;false;263;210;168;0.2723;0.6832;0.3158;0.6842;0.2015;0.3612;0.0095;0.0357;0.0286;0.0595;168;0;0;18.6672;;38;0.1429;0.1429;0.1429;NaN;0.0476;false;0;28801;61213;UE 2022
SP;71072;247;724;0.0816;-1.3993;1.2967;0.1735;0.0;true;true;2;1.0735;0.8585;false;2;"excesso de votos após 17h; ritmo após 17h acima do pico do dia; ";SÃO PAULO;EE. PROF. ARLINDO PINTO DA SILVA;false;361;287;305;0.4423;0.4731;0.5331;0.4669;0.205;0.1551;0.0523;0.0295;0.0418;0.0295;305;0;24;31.2232;52.2054;47;0.0453;0.0623;0.0676;0.0;0.082;false;0;28801;62927;UE 2020
AM;2097;18;40;-0.0695;-4.037;1.0237;8.2668;1.0;false;false;0;2.3426;;false;2;"abst 2T fora do esperado; nulo 2T fora do esperado; ";BARCELOS;E. M. INDÍGENA AJURICABA;true;351;137;170;0.9845;0.0078;0.9928;0.0072;0.6097;0.5157;0.0;0.0059;0.0584;0.1765;170;15;0;19.1435;;41;0.0219;0.0706;0.0706;NaN;0.0059;false;0;29231;61245;UE 2022
AM;2615;5;176;19.3723;-3.7385;0.0031;-0.7209;1.0;false;false;0;0.5647;;false;1;"voto 2T muito acima do esperado p/ Lula; ";MAUÉS;E. M. INDÍGENA UNIAWASAPI;true;382;331;337;0.9422;0.0486;1.0;0.0;0.1335;0.1178;0.0;0.0;0.006;0.0119;337;107;0;37.4456;;62;0.0151;0.0178;0.0178;NaN;0.0089;false;0;28801;61524;UE 2022
AM;2755;22;70;17.1002;-1.301;-0.3997;-0.377;1.0;false;false;0;0.9123;;false;1;"voto 2T muito acima do esperado p/ Lula; ";SÃO PAULO DE OLIVENÇA;E. M. INDÍGENA TIKUNA DUGUE SEBASTIÃO GASPAR ATCHIGUCUNGUTCHAUCU;true;195;183;184;0.8556;0.1111;0.9945;0.0055;0.0615;0.0564;0.0;0.0;0.0164;0.0163;184;0;0;20.4451;;48;0.0164;0.0272;0.0272;NaN;0.0326;false;0;28801;61490;UE 2022
PA;4723;80;254;14.5622;-0.1842;-0.1376;-0.2504;1.0;false;false;0;-1.5215;;false;1;"voto 2T muito acima do esperado p/ Lula; ";ANAPU;EMEF TRINCHEIRA BACAJÁ;true;238;158;162;0.8141;0.1859;0.9753;0.0247;0.3361;0.3193;0.0;0.0;0.0127;0.0;162;0;0;18.3865;;45;0.1456;0.0988;0.0988;NaN;0.0432;false;0;29481;61220;UE 2015
AC;1031;3;95;12.935;-1.3618;-1.1787;-2.0405;1.0;false;false;0;0.8382;;false;1;"voto 2T muito acima do esperado p/ Lula; ";SANTA ROSA DO PURUS;UNIDADE BÁSICA DE SAÚDE ALDEIA MARONAWA;true;337;220;228;0.4722;0.4861;0.7873;0.2127;0.351;0.3234;0.0045;0.0;0.0136;0.0307;228;0;0;25.3341;;49;0.0318;0.057;0.057;NaN;0.057;false;0;28801;61268;UE 2020
AC;1139;7;67;10.646;3.051;-0.5167;1.9291;1.0;false;false;0;0.5047;;false;1;"voto 2T muito acima do esperado p/ Lula; ";FEIJÓ;ALDEIA NOVA FLORESTA;true;155;98;73;0.3723;0.6277;0.7879;0.2121;0.3677;0.529;0.0;0.0;0.0408;0.0959;73;0;0;8.1114;;30;0.0714;0.0959;0.0959;NaN;0.1507;false;0;28801;61274;UE 2022
MA;8974;70;403;9.7071;2.9614;-0.3982;0.9774;0.0;false;false;0;-1.1118;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";SANTA LUZIA;ZEMUEHAN TENTENHAR TEREPIUR;true;166;143;129;0.6714;0.3214;0.8819;0.1181;0.1386;0.2229;0.0;0.0;0.021;0.0155;129;0;5;13.7782;40.1786;23;0.1608;0.124;0.129;0.0;0.0543;false;0;28801;61793;UE 2020
PI;11878;28;99;-9.2378;-0.1919;1.5697;-0.9492;1.0;false;false;0;-2.0367;;false;1;"voto 2T muito acima do esperado p/ Flávio; ";SANTO ANTÔNIO DE LISBOA;U.E.M. PE. JOAO PEDRO (POV. SÃO JOSE - SITIO SALVADOR);false;312;287;273;0.7782;0.2036;0.5448;0.4552;0.0801;0.125;0.0105;0.011;0.0314;0.0073;273;29;0;30.3343;;56;0.1045;0.0659;0.0659;NaN;0.0073;false;0;28801;61212;UE 2022
AP;6041;10;408;9.0379;0.5077;-0.053;-0.2577;1.0;false;false;0;1.9342;;false;1;"voto 2T muito acima do esperado p/ Lula; ";ITAUBAL;ESCOLA ESTADUAL ADELANO NUNES LACERDA;false;210;194;139;0.8073;0.1719;0.964;0.036;0.0762;0.3381;0.0;0.0;0.0103;0.0;139;0;0;15.4449;;36;0.0567;0.1079;0.1079;NaN;0.0432;false;0;28801;61241;UE 2022
SP;71072;2;519;-7.0148;-2.9216;-0.1834;0.589;1.0;false;false;0;-1.0502;1.0;false;1;"voto 2T muito acima do esperado p/ Flávio; ";SÃO PAULO;COLÉGIO EQUIPE;false;392;263;304;0.6063;0.2874;0.5529;0.4471;0.3291;0.2245;0.0152;0.0099;0.019;0.0263;304;0;0;33.7799;;46;0.0646;0.0461;0.0461;NaN;0.0559;false;0;28802;61237;UE 2015
MA;7005;12;145;6.9408;-1.7398;-0.9302;0.6335;1.0;false;false;0;-0.0387;;false;1;"voto 2T muito acima do esperado p/ Lula; ";ÁGUA DOCE DO MARANHÃO;UNIDADE ESCOLAR JOSÉ DA SILVA AGUIAR;false;230;186;193;0.9605;0.0226;1.0;0.0;0.1913;0.1609;0.0054;0.0;0.043;0.0207;193;15;0;21.4451;;47;0.0753;0.0777;0.0777;NaN;0.0674;false;0;28801;61265;UE 2022
AM;2356;17;22;6.6572;-0.5897;-0.4152;-1.1015;1.0;false;false;0;0.2826;;false;1;"voto 2T muito acima do esperado p/ Lula; ";HUMAITÁ;E. E. TUPA JAKUI - TENHARINS;true;308;276;274;0.9188;0.0738;0.9779;0.0221;0.1039;0.1104;0.0036;0.0;0.0145;0.0073;274;21;0;30.4454;;66;0.0254;0.0292;0.0292;NaN;0.1095;false;0;28801;61223;UE 2022
MA;9415;39;206;6.4904;-0.6176;1.1546;-1.3661;1.0;false;false;0;-0.1598;;false;1;"voto 2T muito acima do esperado p/ Lula; ";TURIAÇU;ESCOLA MUNICIPAL BATISTA AMORIM - BANANAL;false;134;98;92;0.9451;0.0549;1.0;0.0;0.2687;0.3134;0.0102;0.0109;0.0612;0.0;92;0;0;10.2225;;32;0.0408;0.0326;0.0326;NaN;0.0217;false;0;28801;61456;UE 2022
MA;8133;74;66;6.1664;-0.0499;-1.293;-1.5545;1.0;false;false;0;-0.9752;;false;1;"voto 2T muito acima do esperado p/ Lula; ";LAGO DA PEDRA;UNIDADE ESCOLAR NOSSA SENHORA DAS GRACAS;false;299;232;233;0.5636;0.3909;0.7328;0.2672;0.2241;0.2207;0.0129;0.0;0.0388;0.0043;233;13;0;25.8897;;51;0.0776;0.0601;0.0601;NaN;0.0215;false;0;28801;61223;UE 2020
MT;91391;47;239;6.1473;-1.5727;0.3075;-0.5619;1.0;false;false;0;0.9451;;false;1;"voto 2T muito acima do esperado p/ Lula; ";POXORÉU;ALDEIAS INDÍGENAS (ALMINHAS);true;283;204;218;0.1827;0.8173;0.3302;0.6698;0.2792;0.2297;0.0049;0.0046;0.0294;0.0092;218;11;0;24.223;;63;0.0294;0.0413;0.0413;NaN;0.0046;false;1;28801;61561;UE 2022
PA;4049;100;315;6.1376;0.1112;-0.6385;-1.0379;1.0;false;false;0;-3.5977;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";BOM JESUS DO TOCANTINS;EIEF KAUKUJURE PARAKATEJE (ALDEIA INDÍGENA PARAKATEJE);true;302;228;228;0.7727;0.2;0.8899;0.1101;0.245;0.245;0.0219;0.0044;0.0132;0.0;228;19;0;25.3341;;57;0.057;0.0088;0.0088;NaN;0.0;false;0;28801;61224;UE 2020
PE;23736;116;103;6.0926;-0.8325;-0.2837;1.0126;1.0;false;false;0;0.7779;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";CANHOTINHO;ESCOLA MUNICIPAL VEREADOR CÍCERO SÁTIRO DE OLIVEIRA;false;222;174;183;0.6744;0.3198;0.8056;0.1944;0.2162;0.1757;0.0;0.0;0.0115;0.0164;183;0;0;20.334;;38;0.046;0.071;0.071;NaN;0.082;false;0;28801;61207;UE 2015
RS;89630;59;591;6.0284;0.1794;0.0355;1.6454;1.0;false;false;0;0.3783;;false;1;"voto 2T muito acima do esperado p/ Lula; ";VIAMÃO;COMUNIDADE TEKOA NHE ENGATU;true;70;65;66;1.0;0.0;1.0;0.0;0.0714;0.0571;0.0;0.0;0.0;0.0152;66;0;0;7.3336;;22;0.0308;0.0455;0.0455;NaN;0.0;false;0;28801;61315;UE 2020
AM;2577;16;57;6.0172;0.045;-0.9761;0.9641;1.0;false;false;0;1.8122;;false;1;"voto 2T muito acima do esperado p/ Lula; ";MANICORÉ;E. M. SAO FRANCISCO;false;274;202;202;0.8141;0.1307;0.9391;0.0609;0.2628;0.2628;0.005;0.0;0.0099;0.0248;202;0;0;22.4451;;45;0.005;0.0198;0.0198;NaN;0.0297;false;0;28801;61407;UE 2020
PA;5258;3;78;5.9954;1.6462;-0.7742;-0.9552;1.0;false;false;0;0.457;;false;1;"voto 2T muito acima do esperado p/ Lula; ";SALVATERRA;EMEIF DE MANGUEIRAS;false;290;251;229;0.9218;0.07;0.9782;0.0218;0.1345;0.2103;0.008;0.0;0.0239;0.0;229;9;0;25.446;;53;0.0239;0.0306;0.0306;NaN;0.0175;false;0;28802;61221;UE 2022
ZZ;30341;1;1894;5.9284;3.365;-1.6127;0.8278;1.0;false;false;0;0.0;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";PORTO;ISEP - R. DR. ANTONIO BERNARDINO / R. DE SÃO TOMÉ (ENTRADAS SEPARADAS);false;797;221;245;0.4882;0.3744;0.6987;0.3013;0.7227;0.6926;0.0317;0.0041;0.0136;0.0204;245;2;0;28.3228;;41;0.0;0.0;0.0;NaN;1.0;false;0;30059;61914;UE 2013
AM;2739;47;9;5.916;-1.7477;-0.1969;-2.1806;1.0;false;false;0;-1.4572;;false;1;"voto 2T muito acima do esperado p/ Lula; ";SANTO ANTÔNIO DO IÇÁ;E. E. D. PEDRO I;false;362;326;330;0.9846;0.0123;1.0;0.0;0.0994;0.0884;0.0;0.0;0.0061;0.003;330;87;0;36.6678;;63;0.0675;0.0455;0.0455;NaN;0.0;false;0;28801;62880;UE 2022
MG;46337;132;259;5.8464;-0.7525;-0.3053;-0.4808;1.0;false;false;0;0.4763;;false;1;"voto 2T muito acima do esperado p/ Lula; ";ITABIRA;PONTO DE APOIO DA COMUNIDADE DOS MACHADOS;false;203;163;174;0.7086;0.2649;0.8521;0.1479;0.197;0.1429;0.0184;0.0057;0.0552;0.023;174;0;0;19.3345;;37;0.1534;0.1724;0.1724;NaN;0.0517;false;0;28802;61251;UE 2015
MA;7994;31;32;5.7591;0.6916;-0.1631;-1.5586;1.0;false;false;0;0.1907;;false;1;"voto 2T muito acima do esperado p/ Lula; ";ICATU;ESCOLA MUNICIPAL OLAVO BILAC;false;219;185;156;0.9213;0.0674;0.9872;0.0128;0.1553;0.2877;0.0;0.0;0.0378;0.0;156;0;0;17.3339;;50;0.0541;0.0641;0.0641;NaN;0.0;false;0;28801;61330;UE 2022
CE;14133;39;27;5.7589;-1.0098;0.2427;-0.2875;1.0;false;false;0;-0.1233;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";INDEPENDÊNCIA;E.E.F. FRANCISCO ALVES DE ARAUJO;false;213;188;187;0.6906;0.2928;0.8152;0.1848;0.1174;0.1221;0.0106;0.0053;0.0266;0.0107;187;0;0;20.7784;;45;0.0691;0.0695;0.0695;NaN;0.0428;false;0;28801;61515;UE 2020
AM;2470;50;19;5.7115;-2.1294;0.4093;2.0729;1.0;false;false;0;-0.1995;;false;1;"voto 2T muito acima do esperado p/ Lula; ";JURUÁ;E. M. LEONEL;false;223;162;168;0.9085;0.0211;1.0;0.0;0.2735;0.2466;0.0062;0.0119;0.1173;0.1012;168;0;0;18.6672;;46;0.0309;0.0238;0.0238;NaN;0.119;false;0;28801;61279;UE 2022
MG;42080;244;72;-5.6484;1.702;-0.0277;-1.5616;1.0;false;false;0;1.8626;1.0;false;1;"voto 2T muito acima do esperado p/ Flávio; ";FRUTA DE LEITE;ESCOLA ESTADUAL ANÍBAL GONÇALVES DAS NEVES;false;330;189;189;0.6012;0.3179;0.5484;0.4516;0.4273;0.4273;0.0106;0.0106;0.0741;0.0053;189;0;0;21.0006;;40;0.0;0.037;0.037;NaN;0.1164;false;3;28801;61240;UE 2020
CE;13471;63;60;5.5775;2.65;0.1852;1.7027;1.0;false;false;0;-0.1013;1.0;false;1;"voto 2T muito acima do esperado p/ Lula; ";BOA VIAGEM;EEF PEDRO SOARES DE ALMEIDA;false;284;242;223;0.7595;0.1814;0.9032;0.0968;0.1479;0.2148;0.0165;0.009;0.0041;0.0179;223;0;0;24.7785;;48;0.0785;0.0807;0.0807;NaN;0.0224;false;0;28801;61222;UE 2020
MT;90280;28;200;5.5644;-3.6737;-0.2807;-0.2953;1.0;false;false;0;1.8324;;false;1;"voto 2T muito acima do esperado p/ Lula; ";CONFRESA;ESCOLA ESTADUAL TAPIITAWA;true;315;297;309;0.9966;0.0;1.0;0.0;0.0571;0.019;0.0;0.0;0.0;0.0;309;16;0;34.3344;;74;0.0707;0.1003;0.1003;NaN;0.0065;false;0;28801;61348;UE 2022
CE;98574;65;197;5.4862;0.2056;0.3958;-0.3386;1.0;false;false;0;-1.5321;;false;1;"voto 2T muito acima do esperado p/ Lula; ";VARJOTA;E.E.I. JOSÉ NEVES DAMASCENO - CRECHE BALNEÁRIO;false;300;250;250;0.6524;0.2446;0.8285;0.1715;0.1667;0.1667;0.012;0.016;0.056;0.028;250;17;1;27.6684;12.0;61;0.128;0.096;0.0964;0.0;0.068;false;0;28802;61243;UE 2015
CE;13773;108;98;5.4299;-0.5173;1.1796;0.328;1.0;false;false;0;0.612;;false;1;"voto 2T muito acima do esperado p/ Lula; ";CHAVAL;ANEXO DA E.E.F. MONSENHOR CARNEIRO;false;275;234;240;0.8673;0.0973;0.9487;0.0513;0.1491;0.1273;0.0085;0.0083;0.0256;0.0167;240;52;0;26.6683;;51;0.1581;0.1833;0.1833;NaN;0.0;false;0;28802;61237;UE 2015
BA;38253;182;63;5.3994;0.5206;0.2863;-0.3102;1.0;false;false;0;0.8931;;false;1;"voto 2T muito acima do esperado p/ Lula; ";RIACHÃO DAS NEVES;ESCOLA MUNICIPAL JOÃO GALDINO DOS SANTOS;false;278;231;232;0.7175;0.2601;0.8326;0.1674;0.1691;0.1655;0.0043;0.0043;0.0303;0.0172;232;25;0;25.7786;;43;0.0476;0.069;0.069;NaN;0.0647;false;0;28801;61395;UE 2020
AM;2690;4;203;5.3878;1.423;-0.3596;-1.4435;1.0;false;false;0;0.3178;;false;1;"voto 2T muito acima do esperado p/ Lula; ";PARINTINS;E. M. NOSSA SENHORA DE NAZARE;false;193;136;127;0.8731;0.097;0.9685;0.0315;0.2953;0.342;0.0;0.0;0.0147;0.0;127;0;0;14.1115;;51;0.0221;0.0315;0.0315;NaN;0.0551;false;0;28801;61285;UE 2022
MG;52213;252;251;5.3481;2.5153;-0.5206;-0.2418;1.0;false;false;0;-1.4571;;false;1;"voto 2T muito acima do esperado p/ Lula; ";SÃO FRANCISCO;ESCOLA ESTADUAL PASSAGEM FUNDA - BURITI DO MEIO;false;269;195;188;0.8615;0.1179;0.9412;0.0588;0.2751;0.3011;0.0;0.0;0.0;0.0053;188;0;0;20.8895;;37;0.0667;0.0319;0.0319;NaN;0.0957;false;0;28801;61364;UE 2020
```

## Urnas que votaram entre 17h e 19h (prorrogação) e afirmação sobre margens por horário de encerramento (pos17_resumo.json)
```json
{"ufs_com_log": ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"], "urnas_por_grupo": {"NORMAL": 469071, "FILA": 27312, "ESTENDIDA": 2794}, "votos_por_grupo_apos_17h": {"NORMAL": 0, "FILA": 30110, "ESTENDIDA": 4637}, "votos_17h15_19h_total": 3918, "votos_apos_19h": 11, "votos_apos_19h05": 2, "urnas_com_voto_apos_encerramento": 1, "estendidas_por_uf": {"RJ": 1181, "SP": 849, "BA": 399, "PE": 198, "PB": 86, "SE": 13, "MA": 10, "CE": 8, "MG": 7, "PA": 6, "RN": 4, "DF": 4, "GO": 4, "ZZ": 4, "PI": 4, "AM": 4, "PR": 3, "AL": 3, "RS": 2, "MT": 2, "SC": 1, "MS": 1, "ES": 1}, "estendidas_distribuicao_votos_1715": {"mediana": 1.0, "p90": 2.0, "max": 27, "urnas_com_10+": 10, "urnas_com_30+": 0}, "horario_encerramento": {"NORMAL": {"p50": 17.017777777777777, "p99": 17.601944444444445}, "FILA": {"p50": 17.05, "p99": 19.025}, "ESTENDIDA": {"p50": 19.015833333333333, "p99": 19.155277777777776}}, "perfil_urnas_estendidas": {"8h-17h": {"votos": 834865, "pct_sem_biometria_apos_falha": 6.19, "pct_sem_biometria_cadastrada": 6.58, "pct_mesario_habilitou": 4.04, "duracao_mediana_voto_s": 10.0, "intervalo_mediano_entre_eleitores_s": 65.0, "pct_intervalo_menor_30s": 1.54}, "17h15-19h": {"votos": 3918, "pct_sem_biometria_apos_falha": 4.95, "pct_sem_biometria_cadastrada": 9.37, "pct_mesario_habilitou": 2.91, "duracao_mediana_voto_s": 10.0, "intervalo_mediano_entre_eleitores_s": 3088.5, "pct_intervalo_menor_30s": 0.08}, "teste_sem_biometria_p": 0.0011084975353746781, "teste_duracao_mannwhitney_p": 0.00026876083648453344}, "urnas_estendidas_testaveis_5+_votos_prorrogacao": 21, "urnas_estendidas_sem_biometria_anomala_p<0.001": 1, "urnas_estendidas_com_rajadas_5+": 0, "resultado_mesmos_municipios": {"FILA": {"secoes": 10557, "z_A_medio": 0.085, "pct_z_A_forte": 0.038, "z_abst_medio": -0.022, "delta_lula_medio_pp": 7.95, "delta_abstencao_media_pp": -2.49}, "NORMAL": {"secoes": 112818, "z_A_medio": 0.009, "pct_z_A_forte": 0.037, "z_abst_medio": 0.015, "delta_lula_medio_pp": 7.57, "delta_abstencao_media_pp": -2.15}, "ESTENDIDA": {"secoes": 2794, "z_A_medio": 0.024, "pct_z_A_forte": 0.0, "z_abst_medio": -0.234, "delta_lula_medio_pp": 7.78, "delta_abstencao_media_pp": -3.22}}, "correlacao_frac_votos_prorrogacao_x_desvio_voto": {"spearman": 0.0007, "p": 0.7981102143136458}, "teste_z_A_estendida_vs_normal_mesmos_municipios": {"mannwhitney_p": 0.5945911541058573, "mediana_estendida": 0.005, "mediana_normal": -0.009}, "estendidas_no_1t": {"pct_votos_apos_17h_1t": 3.77, "ultimo_voto_mediano_1t_h": 17.06833333333333}, "divisao_por_encerramento": {"2026": {"nota": "Em 2022 o log não registra 'Encerrar votação'; o encerramento usa 'Inicio do Encerramento' (~2 min depois). Para comparar anos, use os cortes marcados como comparáveis (baseados no horário do último voto).", "secoes_com_log": 499173, "ufs": ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"], "margem_total_2t_mi": 4.43, "votos_apos_17h": 34745, "encerrou depois de 17h00:00": {"até": {"urnas": 516, "votos_apos_17h": 0, "margem_13_2t_mi": -0.002, "margem_13_1t_mi": -0.009, "pct13_2t": 49.21, "pct13_1t_entre_13_e_22": 46.17}, "depois": {"urnas": 498657, "votos_apos_17h": 34745, "margem_13_2t_mi": 4.432, "margem_13_1t_mi": -2.216, "pct13_2t": 51.79, "pct13_1t_entre_13_e_22": 48.99}}, "encerrou depois de 17h01": {"até": {"urnas": 228708, "votos_apos_17h": 2054, "margem_13_2t_mi": 0.093, "margem_13_1t_mi": -2.611, "pct13_2t": 50.08, "pct13_1t_entre_13_e_22": 47.37}, "depois": {"urnas": 270465, "votos_apos_17h": 32691, "margem_13_2t_mi": 4.337, "margem_13_1t_mi": 0.387, "pct13_2t": 53.17, "pct13_1t_entre_13_e_22": 50.32}}, "encerrou depois de 17h05": {"até": {"urnas": 452304, "votos_apos_17h": 22168, "margem_13_2t_mi": 2.864, "margem_13_1t_mi": -2.974, "pct13_2t": 51.28, "pct13_1t_entre_13_e_22": 48.5}, "depois": {"urnas": 46869, "votos_apos_17h": 12577, "margem_13_2t_mi": 1.566, "margem_13_1t_mi": 0.749, "pct13_2t": 56.36, "pct13_1t_entre_13_e_22": 53.48}}, "encerrou depois de 17h15": {"até": {"urnas": 488511, "votos_apos_17h": 28815, "margem_13_2t_mi": 4.082, "margem_13_1t_mi": -2.371, "pct13_2t": 51.68, "pct13_1t_entre_13_e_22": 48.9}, "depois": {"urnas": 10662, "votos_apos_17h": 5930, "margem_13_2t_mi": 0.348, "margem_13_1t_mi": 0.147, "pct13_2t": 55.92, "pct13_1t_entre_13_e_22": 52.88}}, "teve voto depois de 17h": {"até": {"urnas": 469068, "votos_apos_17h": 0, "margem_13_2t_mi": 3.789, "margem_13_1t_mi": -2.345, "pct13_2t": 51.63, "pct13_1t_entre_13_e_22": 48.86}, "depois": {"urnas": 30105, "votos_apos_17h": 34745, "margem_13_2t_mi": 0.641, "margem_13_1t_mi": 0.12, "pct13_2t": 54.01, "pct13_1t_entre_13_e_22": 50.86}}, "último voto depois de 17h15 (comparável 2022×2026)": {"até": {"urnas": 496379, "votos_apos_17h": 30108, "margem_13_2t_mi": 4.339, "margem_13_1t_mi": -2.255, "pct13_2t": 51.76, "pct13_1t_entre_13_e_22": 48.97}, "depois": {"urnas": 2794, "votos_apos_17h": 4637, "margem_13_2t_mi": 0.091, "margem_13_1t_mi": 0.031, "pct13_2t": 55.64, "pct13_1t_entre_13_e_22": 52.21}}, "agrupado_por_area": {"alguma urna encerrou depois de 17h15 — por zona": {"não": {"urnas": 268175, "margem_13_2t_mi": -1.974, "margem_13_1t_mi": -4.98}, "sim": {"urnas": 230998, "margem_13_2t_mi": 6.404, "margem_13_1t_mi": 2.756}}, "alguma urna encerrou depois de 17h15 — por município": {"não": {"urnas": 242232, "margem_13_2t_mi": 0.545, "margem_13_1t_mi": -2.087}, "sim": {"urnas": 256941, "margem_13_2t_mi": 3.885, "margem_13_1t_mi": -0.137}}, "alguma urna encerrou depois de 17h15 — por local de votação": {"não": {"urnas": 470186, "margem_13_2t_mi": 3.458, "margem_13_1t_mi": -2.662}, "sim": {"urnas": 28987, "margem_13_2t_mi": 0.973, "margem_13_1t_mi": 0.437}}, "alguma urna teve voto depois de 17h — por zona": {"não": {"urnas": 13777, "margem_13_2t_mi": -0.21, "margem_13_1t_mi": -0.318}, "sim": {"urnas": 485396, "margem_13_2t_mi": 4.641, "margem_13_1t_mi": -1.907}}, "alguma urna teve voto depois de 17h — por município": {"não": {"urnas": 49931, "margem_13_2t_mi": 0.43, "margem_13_1t_mi": -0.021}, "sim": {"urnas": 449242, "margem_13_2t_mi": 4.0, "margem_13_1t_mi": -2.203}}, "alguma urna teve voto depois de 17h — por local de votação": {"não": {"urnas": 323087, "margem_13_2t_mi": 2.814, "margem_13_1t_mi": -1.049}, "sim": {"urnas": 176086, "margem_13_2t_mi": 1.616, "margem_13_1t_mi": -1.175}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por zona": {"não": {"urnas": 421665, "margem_13_2t_mi": 1.323, "margem_13_1t_mi": -3.882}, "sim": {"urnas": 77508, "margem_13_2t_mi": 3.108, "margem_13_1t_mi": 1.658}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por município": {"não": {"urnas": 373004, "margem_13_2t_mi": 1.316, "margem_13_1t_mi": -3.057}, "sim": {"urnas": 126169, "margem_13_2t_mi": 3.114, "margem_13_1t_mi": 0.832}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por local de votação": {"não": {"urnas": 488398, "margem_13_2t_mi": 4.038, "margem_13_1t_mi": -2.398}, "sim": {"urnas": 10775, "margem_13_2t_mi": 0.392, "margem_13_1t_mi": 0.173}}}, "por_uf_encerrou_ate_17h01": {"SP": {"urnas": 37174, "margem_13_2t_mi": -1.416}, "MG": {"urnas": 30554, "margem_13_2t_mi": 0.037}, "RS": {"urnas": 18251, "margem_13_2t_mi": -0.785}, "PR": {"urnas": 16493, "margem_13_2t_mi": -1.046}, "BA": {"urnas": 13056, "margem_13_2t_mi": 1.372}, "CE": {"urnas": 12952, "margem_13_2t_mi": 1.239}, "SC": {"urnas": 12361, "margem_13_2t_mi": -1.303}, "RJ": {"urnas": 10736, "margem_13_2t_mi": -0.246}, "PA": {"urnas": 9642, "margem_13_2t_mi": 0.242}, "GO": {"urnas": 9370, "margem_13_2t_mi": -0.465}, "MA": {"urnas": 7556, "margem_13_2t_mi": 0.646}, "PE": {"urnas": 6430, "margem_13_2t_mi": 0.753}, "ES": {"urnas": 6095, "margem_13_2t_mi": -0.184}, "PB": {"urnas": 5682, "margem_13_2t_mi": 0.514}, "PI": {"urnas": 5196, "margem_13_2t_mi": 0.569}, "RN": {"urnas": 3880, "margem_13_2t_mi": 0.321}, "MS": {"urnas": 3876, "margem_13_2t_mi": -0.166}, "MT": {"urnas": 3216, "margem_13_2t_mi": -0.239}, "SE": {"urnas": 3103, "margem_13_2t_mi": 0.295}, "AM": {"urnas": 2928, "margem_13_2t_mi": 0.085}, "AL": {"urnas": 2771, "margem_13_2t_mi": 0.172}, "TO": {"urnas": 2112, "margem_13_2t_mi": -0.013}, "RO": {"urnas": 1749, "margem_13_2t_mi": -0.155}, "AC": {"urnas": 1362, "margem_13_2t_mi": -0.084}, "AP": {"urnas": 901, "margem_13_2t_mi": 0.013}, "RR": {"urnas": 640, "margem_13_2t_mi": -0.055}, "DF": {"urnas": 535, "margem_13_2t_mi": -0.011}, "ZZ": {"urnas": 87, "margem_13_2t_mi": 0.002}}}, "2022": {"nota": "Em 2022 o log não registra 'Encerrar votação'; o encerramento usa 'Inicio do Encerramento' (~2 min depois). Para comparar anos, use os cortes marcados como comparáveis (baseados no horário do último voto).", "secoes_com_log": 471935, "ufs": ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"], "margem_total_2t_mi": 2.138, "votos_apos_17h": 41399, "encerrou depois de 17h00:00": {"depois": {"urnas": 471935, "votos_apos_17h": 41399, "margem_13_2t_mi": 2.138, "margem_13_1t_mi": 6.185, "pct13_2t": 50.9, "pct13_1t_entre_13_e_22": 52.85}}, "encerrou depois de 17h01": {"até": {"urnas": 2791, "votos_apos_17h": 17, "margem_13_2t_mi": 0.024, "margem_13_1t_mi": 0.05, "pct13_2t": 51.71, "pct13_1t_entre_13_e_22": 53.92}, "depois": {"urnas": 469144, "votos_apos_17h": 41382, "margem_13_2t_mi": 2.114, "margem_13_1t_mi": 6.135, "pct13_2t": 50.9, "pct13_1t_entre_13_e_22": 52.85}}, "encerrou depois de 17h05": {"até": {"urnas": 331579, "votos_apos_17h": 13642, "margem_13_2t_mi": 0.317, "margem_13_1t_mi": 3.257, "pct13_2t": 50.19, "pct13_1t_entre_13_e_22": 52.17}, "depois": {"urnas": 140356, "votos_apos_17h": 27757, "margem_13_2t_mi": 1.82, "margem_13_1t_mi": 2.928, "pct13_2t": 52.51, "pct13_1t_entre_13_e_22": 54.42}}, "encerrou depois de 17h15": {"até": {"urnas": 467723, "votos_apos_17h": 38261, "margem_13_2t_mi": 2.0, "margem_13_1t_mi": 6.019, "pct13_2t": 50.85, "pct13_1t_entre_13_e_22": 52.8}, "depois": {"urnas": 4212, "votos_apos_17h": 3138, "margem_13_2t_mi": 0.138, "margem_13_1t_mi": 0.166, "pct13_2t": 56.26, "pct13_1t_entre_13_e_22": 58.23}}, "teve voto depois de 17h": {"até": {"urnas": 436957, "votos_apos_17h": 0, "margem_13_2t_mi": 2.051, "margem_13_1t_mi": 5.775, "pct13_2t": 50.94, "pct13_1t_entre_13_e_22": 52.89}, "depois": {"urnas": 34978, "votos_apos_17h": 41399, "margem_13_2t_mi": 0.086, "margem_13_1t_mi": 0.41, "pct13_2t": 50.46, "pct13_1t_entre_13_e_22": 52.39}}, "último voto depois de 17h15 (comparável 2022×2026)": {"até": {"urnas": 471717, "votos_apos_17h": 39816, "margem_13_2t_mi": 2.129, "margem_13_1t_mi": 6.175, "pct13_2t": 50.9, "pct13_1t_entre_13_e_22": 52.85}, "depois": {"urnas": 218, "votos_apos_17h": 1583, "margem_13_2t_mi": 0.008, "margem_13_1t_mi": 0.01, "pct13_2t": 57.73, "pct13_1t_entre_13_e_22": 59.55}}, "agrupado_por_area": {"alguma urna encerrou depois de 17h15 — por zona": {"não": {"urnas": 172872, "margem_13_2t_mi": -1.583, "margem_13_1t_mi": 0.089}, "sim": {"urnas": 299063, "margem_13_2t_mi": 3.72, "margem_13_1t_mi": 6.096}}, "alguma urna encerrou depois de 17h15 — por município": {"não": {"urnas": 176464, "margem_13_2t_mi": 1.237, "margem_13_1t_mi": 2.783}, "sim": {"urnas": 295471, "margem_13_2t_mi": 0.9, "margem_13_1t_mi": 3.402}}, "alguma urna encerrou depois de 17h15 — por local de votação": {"não": {"urnas": 445221, "margem_13_2t_mi": 1.723, "margem_13_1t_mi": 5.561}, "sim": {"urnas": 26714, "margem_13_2t_mi": 0.414, "margem_13_1t_mi": 0.624}}, "alguma urna teve voto depois de 17h — por zona": {"não": {"urnas": 8081, "margem_13_2t_mi": 0.065, "margem_13_1t_mi": 0.139}, "sim": {"urnas": 463854, "margem_13_2t_mi": 2.073, "margem_13_1t_mi": 6.046}}, "alguma urna teve voto depois de 17h — por município": {"não": {"urnas": 41716, "margem_13_2t_mi": 1.1, "margem_13_1t_mi": 1.428}, "sim": {"urnas": 430219, "margem_13_2t_mi": 1.037, "margem_13_1t_mi": 4.757}}, "alguma urna teve voto depois de 17h — por local de votação": {"não": {"urnas": 277176, "margem_13_2t_mi": 3.085, "margem_13_1t_mi": 5.324}, "sim": {"urnas": 194759, "margem_13_2t_mi": -0.947, "margem_13_1t_mi": 0.861}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por zona": {"não": {"urnas": 427539, "margem_13_2t_mi": 1.378, "margem_13_1t_mi": 5.094}, "sim": {"urnas": 44396, "margem_13_2t_mi": 0.76, "margem_13_1t_mi": 1.091}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por município": {"não": {"urnas": 371590, "margem_13_2t_mi": 1.759, "margem_13_1t_mi": 5.064}, "sim": {"urnas": 100345, "margem_13_2t_mi": 0.379, "margem_13_1t_mi": 1.121}}, "alguma urna teve voto depois de 17h15 (comparável 2022×2026) — por local de votação": {"não": {"urnas": 470265, "margem_13_2t_mi": 2.126, "margem_13_1t_mi": 6.159}, "sim": {"urnas": 1670, "margem_13_2t_mi": 0.012, "margem_13_1t_mi": 0.026}}}, "por_uf_encerrou_ate_17h01": {"RS": {"urnas": 545, "margem_13_2t_mi": -0.015}, "MG": {"urnas": 229, "margem_13_2t_mi": 0.0}, "SP": {"urnas": 222, "margem_13_2t_mi": -0.006}, "CE": {"urnas": 214, "margem_13_2t_mi": 0.024}, "BA": {"urnas": 172, "margem_13_2t_mi": 0.02}, "PA": {"urnas": 156, "margem_13_2t_mi": 0.007}, "AM": {"urnas": 149, "margem_13_2t_mi": -0.006}, "SC": {"urnas": 143, "margem_13_2t_mi": -0.016}, "PR": {"urnas": 140, "margem_13_2t_mi": -0.008}, "GO": {"urnas": 117, "margem_13_2t_mi": -0.005}, "PB": {"urnas": 90, "margem_13_2t_mi": 0.006}, "RJ": {"urnas": 87, "margem_13_2t_mi": -0.004}, "PE": {"urnas": 72, "margem_13_2t_mi": 0.008}, "MS": {"urnas": 66, "margem_13_2t_mi": -0.002}, "MA": {"urnas": 64, "margem_13_2t_mi": 0.007}, "PI": {"urnas": 64, "margem_13_2t_mi": 0.008}, "SE": {"urnas": 64, "margem_13_2t_mi": 0.005}, "ES": {"urnas": 64, "margem_13_2t_mi": -0.002}, "AL": {"urnas": 30, "margem_13_2t_mi": 0.002}, "RN": {"urnas": 24, "margem_13_2t_mi": 0.002}, "MT": {"urnas": 22, "margem_13_2t_mi": -0.001}, "AC": {"urnas": 19, "margem_13_2t_mi": -0.001}, "TO": {"urnas": 16, "margem_13_2t_mi": 0.0}, "RR": {"urnas": 8, "margem_13_2t_mi": 0.0}, "RO": {"urnas": 7, "margem_13_2t_mi": -0.0}, "AP": {"urnas": 4, "margem_13_2t_mi": 0.0}, "DF": {"urnas": 3, "margem_13_2t_mi": -0.0}}}}, "encerramento_ate_17h00": {"exatamente_17h00m00s": 499, "1_a_60s_antes": 16, "mais_de_1min_antes": 1}, "verificacao_individual": {"total": 48, "por_motivo": {"voto após encerramento": 1, "encerramento antes de 17h": 1, "seção redesenhada entre turnos": 28, "log ≠ BU": 7, "voto após 19h": 11}, "lista": [{"uf": "BA", "cd_municipio": 35653, "nr_zona": 173, "nr_secao": 235, "motivo": "log com 204 votos, BU com 217 (contingência=True, origem=Urna Eletrônica)"}, {"uf": "RS", "cd_municipio": 89060, "nr_zona": 17, "nr_secao": 191, "motivo": "log com 90 votos, BU com 92 (contingência=True, origem=Urna Eletrônica)"}, {"uf": "PI", "cd_municipio": 11533, "nr_zona": 3, "nr_secao": 216, "motivo": "log com 258 votos, BU com 259 (contingência=False, origem=Urna Eletrônica)"}, {"uf": "BA", "cd_municipio": 34711, "nr_zona": 21, "nr_secao": 178, "motivo": "log com 233 votos, BU com 234 (contingência=False, origem=Urna Eletrônica)"}, {"uf": "PB", "cd_municipio": 21750, "nr_zona": 2, "nr_secao": 254, "motivo": "log com 303 votos, BU com 304 (contingência=False, origem=Urna Eletrônica)"}, {"uf": "ES", "cd_municipio": 57932, "nr_zona": 9, "nr_secao": 85, "motivo": "log com 612 votos, BU com 308 (contingência=True, origem=BU gerado por RED em urna de seção *** RED - Recuperador de dados)"}, {"uf": "MA", "cd_municipio": 8893, "nr_zona": 47, "nr_secao": 609, "motivo": "log com 188 votos, BU com 224 (contingência=True, origem=Urna Eletrônica)"}, {"uf": "MG", "cd_municipio": 46256, "nr_zona": 131, "nr_secao": 46, "motivo": "125 voto(s) registrados depois do horário de encerramento do log"}, {"uf": "BA", "cd_municipio": 38490, "nr_zona": 5, "nr_secao": 449, "motivo": "1 voto(s) depois de 19h (último às 19h01m30s)"}, {"uf": "SP", "cd_municipio": 71072, "nr_zona": 350, "nr_secao": 604, "motivo": "1 voto(s) depois de 19h (último às 19h00m57s)"}, {"uf": "SP", "cd_municipio": 71072, "nr_zona": 1, "nr_secao": 247, "motivo": "1 voto(s) depois de 19h (último às 19h00m25s)"}, {"uf": "RJ", "cd_municipio": 60011, "nr_zona": 17, "nr_secao": 397, "motivo": "1 voto(s) depois de 19h (último às 19h01m56s)"}, {"uf": "RJ", "cd_municipio": 60011, "nr_zona": 238, "nr_secao": 183, "motivo": "1 voto(s) depois de 19h (último às 19h00m08s)"}, {"uf": "SP", "cd_municipio": 71072, "nr_zona": 375, "nr_secao": 734, "motivo": "1 voto(s) depois de 19h (último às 19h05m14s)"}, {"uf": "RJ", "cd_municipio": 60011, "nr_zona": 245, "nr_secao": 223, "motivo": "1 voto(s) depois de 19h (último às 19h00m53s)"}, {"uf": "SP", "cd_municipio": 71072, "nr_zona": 2, "nr_secao": 37, "motivo": "1 voto(s) depois de 19h (último às 19h00m08s)"}, {"uf": "BA", "cd_municipio": 38490, "nr_zona": 10, "nr_secao": 909, "motivo": "1 voto(s) depois de 19h (último às 19h01m48s)"}, {"uf": "RJ", "cd_municipio": 60011, "nr_zona": 234, "nr_secao": 5, "motivo": "1 voto(s) depois de 19h (último às 19h00m18s)"}, {"uf": "SP", "cd_municipio": 71072, "nr_zona": 1, "nr_secao": 405, "motivo": "1 voto(s) depois de 19h (último às 19h06m21s)"}, {"uf": "MG", "cd_municipio": 46256, "nr_zona": 131, "nr_secao": 46, "motivo": "encerramento registrado 386 min antes das 17h"}, {"uf": "MA", "cd_municipio": 9210, "nr_zona": 89, "nr_secao": 534, "motivo": "seção redesenhada? comparecimento 1T 287 > aptos 2T 276"}, {"uf": "CE", "cd_municipio": 15598, "nr_zona": 121, "nr_secao": 315, "motivo": "seção redesenhada? comparecimento 1T 31 > aptos 2T 28"}, {"uf": "MA", "cd_municipio": 9210, "nr_zona": 2, "nr_secao": 513, "motivo": "seção redesenhada? comparecimento 1T 168 > aptos 2T 141"}, {"uf": "MA", "cd_municipio": 9377, "nr_zona": 19, "nr_secao": 622, "motivo": "seção redesenhada? comparecimento 1T 229 > aptos 2T 220"}, {"uf": "PE", "cd_municipio": 24910, "nr_zona": 117, "nr_secao": 16, "motivo": "seção redesenhada? comparecimento 1T 210 > aptos 2T 136"}, {"uf": "SC", "cd_municipio": 80810, "nr_zona": 94, "nr_secao": 393, "motivo": "seção redesenhada? comparecimento 1T 288 > aptos 2T 246"}, {"uf": "AL", "cd_municipio": 27855, "nr_zona": 2, "nr_secao": 445, "motivo": "seção redesenhada? comparecimento 1T 297 > aptos 2T 291"}, {"uf": "SP", "cd_municipio": 69213, "nr_zona": 406, "nr_secao": 368, "motivo": "seção redesenhada? comparecimento 1T 30 > aptos 2T 27"}, {"uf": "PE", "cd_municipio": 25313, "nr_zona": 5, "nr_secao": 516, "motivo": "seção redesenhada? comparecimento 1T 327 > aptos 2T 310"}, {"uf": "DF", "cd_municipio": 97012, "nr_zona": 18, "nr_secao": 419, "motivo": "seção redesenhada? comparecimento 1T 35 > aptos 2T 33"}, {"uf": "SP", "cd_municipio": 72036, "nr_zona": 175, "nr_secao": 138, "motivo": "seção redesenhada? comparecimento 1T 70 > aptos 2T 60"}, {"uf": "SP", "cd_municipio": 61085, "nr_zona": 205, "nr_secao": 81, "motivo": "seção redesenhada? comparecimento 1T 34 > aptos 2T 27"}, {"uf": "PE", "cd_municipio": 25313, "nr_zona": 5, "nr_secao": 509, "motivo": "seção redesenhada? comparecimento 1T 331 > aptos 2T 311"}, {"uf": "SP", "cd_municipio": 63894, "nr_zona": 149, "nr_secao": 119, "motivo": "seção redesenhada? comparecimento 1T 34 > aptos 2T 27"}, {"uf": "SC", "cd_municipio": 81051, "nr_zona": 100, "nr_secao": 528, "motivo": "seção redesenhada? comparecimento 1T 150 > aptos 2T 147"}, {"uf": "GO", "cd_municipio": 92274, "nr_zona": 132, "nr_secao": 548, "motivo": "seção redesenhada? comparecimento 1T 56 > aptos 2T 47"}, {"uf": "PE", "cd_municipio": 25313, "nr_zona": 5, "nr_secao": 22, "motivo": "seção redesenhada? comparecimento 1T 328 > aptos 2T 310"}, {"uf": "BA", "cd_municipio": 34134, "nr_zona": 170, "nr_secao": 262, "motivo": "seção redesenhada? comparecimento 1T 107 > aptos 2T 68"}, {"uf": "MG", "cd_municipio": 46531, "nr_zona": 136, "nr_secao": 216, "motivo": "seção redesenhada? comparecimento 1T 26 > aptos 2T 21"}, {"uf": "RS", "cd_municipio": 87491, "nr_zona": 31, "nr_secao": 247, "motivo": "seção redesenhada? comparecimento 1T 35 > aptos 2T 34"}, {"uf": "MG", "cd_municipio": 41416, "nr_zona": 43, "nr_secao": 132, "motivo": "seção redesenhada? comparecimento 1T 27 > aptos 2T 21"}, {"uf": "PE", "cd_municipio": 25313, "nr_zona": 5, "nr_secao": 21, "motivo": "seção redesenhada? comparecimento 1T 323 > aptos 2T 312"}, {"uf": "MA", "cd_municipio": 9210, "nr_zona": 2, "nr_secao": 512, "motivo": "seção redesenhada? comparecimento 1T 171 > aptos 2T 142"}, {"uf": "MA", "cd_municipio": 9210, "nr_zona": 89, "nr_secao": 532, "motivo": "seção redesenhada? comparecimento 1T 285 > aptos 2T 276"}, {"uf": "PE", "cd_municipio": 24910, "nr_zona": 117, "nr_secao": 417, "motivo": "seção redesenhada? comparecimento 1T 201 > aptos 2T 139"}, {"uf": "MA", "cd_municipio": 9210, "nr_zona": 2, "nr_secao": 511, "motivo": "seção redesenhada? comparecimento 1T 223 > aptos 2T 193"}, {"uf": "CE", "cd_municipio": 13188, "nr_zona": 78, "nr_secao": 418, "motivo": "seção redesenhada? comparecimento 1T 29 > aptos 2T 26"}, {"uf": "PE", "cd_municipio": 25313, "nr_zona": 5, "nr_secao": 517, "motivo": "seção redesenhada? comparecimento 1T 329 > aptos 2T 310"}]}}
```

## Checagem de afirmações de mensagem viral (dados agregados) (checagem_dados.json)
```json
{"presidente_2026": {"1": {"validos": 119306034, "aptos": 158745502, "comparecimento": 125275835, "abstencoes": 33469244, "brancos": 2300798, "nulos": 3669003, "candidatos": [{"nr": 22, "nome": "FLAVIO BOLSONARO", "partido": "PL", "ideologia": "direita/extrema-direita", "votos": 56104503, "pct_validos": 47.026}, {"nr": 13, "nome": "LULA", "partido": "PT", "ideologia": "extrema-esquerda/esquerda", "votos": 53879538, "pct_validos": 45.161}, {"nr": 70, "nome": "ESCRITOR AUGUSTO CURY", "partido": "AVANTE", "ideologia": "centro", "votos": 3448569, "pct_validos": 2.891}, {"nr": 14, "nome": "RENAN SANTOS", "partido": "MISSÃO", "ideologia": "direita/extrema-direita", "votos": 2675887, "pct_validos": 2.243}, {"nr": 55, "nome": "RONALDO CAIADO", "partido": "PSD", "ideologia": "centro-direita", "votos": 2605148, "pct_validos": 2.184}, {"nr": 30, "nome": "ZEMA", "partido": "NOVO", "ideologia": "direita/extrema-direita", "votos": 326488, "pct_validos": 0.274}, {"nr": 80, "nome": "SAMARA", "partido": "UP", "ideologia": "extrema-esquerda/esquerda", "votos": 122911, "pct_validos": 0.103}, {"nr": 16, "nome": "HERTZ DIAS", "partido": "PSTU", "ideologia": "extrema-esquerda/esquerda", "votos": 43103, "pct_validos": 0.036}, {"nr": 27, "nome": "CLARIANA BARAO", "partido": "DC", "ideologia": "direita/extrema-direita", "votos": 40043, "pct_validos": 0.034}, {"nr": 21, "nome": "EDMILSON COSTA", "partido": "PCB", "ideologia": "extrema-esquerda/esquerda", "votos": 22693, "pct_validos": 0.019}, {"nr": 35, "nome": "VETERINÁRIO WILSON GRASSI", "partido": "DEMOCRATA", "ideologia": "centro", "votos": 16881, "pct_validos": 0.014}, {"nr": 29, "nome": "RUI COSTA PIMENTA", "partido": "PCO", "ideologia": "extrema-esquerda/esquerda", "votos": 15024, "pct_validos": 0.013}, {"nr": 28, "nome": "LEONARDO AVALANCHE", "partido": "PRTB", "ideologia": "direita/extrema-direita", "votos": 5246, "pct_validos": 0.004}]}, "2": {"validos": 124082273, "aptos": 158745502, "comparecimento": 128236074, "abstencoes": 30509005, "brancos": 1430496, "nulos": 2723305, "candidatos": [{"nr": 13, "nome": "LULA", "partido": "PT", "ideologia": "extrema-esquerda/esquerda", "votos": 64256232, "pct_validos": 51.785}, {"nr": 22, "nome": "FLAVIO BOLSONARO", "partido": "PL", "ideologia": "direita/extrema-direita", "votos": 59826041, "pct_validos": 48.215}]}}, "presidente_2022": {"1": {"validos": 118229719, "aptos": 156454011, "comparecimento": 123682372, "abstencoes": 32770982, "brancos": 1964779, "nulos": 3487874, "candidatos": [{"nr": 13, "nome": "LULA", "partido": "PT", "ideologia": "extrema-esquerda/esquerda", "votos": 57259504, "pct_validos": 48.431}, {"nr": 22, "nome": "JAIR BOLSONARO", "partido": "PL", "ideologia": "direita/extrema-direita", "votos": 51072345, "pct_validos": 43.198}, {"nr": 15, "nome": "SIMONE TEBET", "partido": "MDB", "ideologia": "centro", "votos": 4915423, "pct_validos": 4.158}, {"nr": 12, "nome": "CIRO GOMES", "partido": "PDT", "ideologia": "centro-esquerda", "votos": 3599287, "pct_validos": 3.044}, {"nr": 44, "nome": "SORAYA THRONICKE", "partido": "UNIÃO", "ideologia": "direita/extrema-direita", "votos": 600955, "pct_validos": 0.508}, {"nr": 30, "nome": "FELIPE D AVILA", "partido": "NOVO", "ideologia": "direita/extrema-direita", "votos": 559708, "pct_validos": 0.473}, {"nr": 14, "nome": "ROBERTO JEFFERSON", "partido": "PTB", "ideologia": "direita/extrema-direita", "votos": 81129, "pct_validos": 0.069}, {"nr": 80, "nome": "LÉO PÉRICLES", "partido": "UP", "ideologia": "extrema-esquerda/esquerda", "votos": 53519, "pct_validos": 0.045}, {"nr": 21, "nome": "SOFIA MANZANO", "partido": "PCB", "ideologia": "extrema-esquerda/esquerda", "votos": 45620, "pct_validos": 0.039}, {"nr": 16, "nome": "VERA", "partido": "PSTU", "ideologia": "extrema-esquerda/esquerda", "votos": 25625, "pct_validos": 0.022}, {"nr": 27, "nome": "CONSTITUINTE EYMAEL", "partido": "DC", "ideologia": "direita/extrema-direita", "votos": 16604, "pct_validos": 0.014}]}, "2": {"validos": 118552353, "aptos": 156454011, "comparecimento": 124252796, "abstencoes": 32200558, "brancos": 1769678, "nulos": 3930765, "candidatos": [{"nr": 13, "nome": "LULA", "partido": "PT", "ideologia": "extrema-esquerda/esquerda", "votos": 60345999, "pct_validos": 50.902}, {"nr": 22, "nome": "JAIR BOLSONARO", "partido": "PL", "ideologia": "direita/extrema-direita", "votos": 58206354, "pct_validos": 49.098}]}}, "congresso_governadores": {"DEPUTADO FEDERAL_2026": {"total": 513, "por_partido": {"PL": 121, "PT": 70, "UNIÃO": 46, "PSD": 43, "REPUBLICANOS": 41, "PP": 41, "MDB": 36, "PODE": 27, "PSB": 15, "PSOL": 14, "PSDB": 11, "PCDOB": 11, "NOVO": 10, "PV": 7, "PDT": 6, "PRD": 5, "AVANTE": 5, "SOLIDARIEDADE": 2, "MISSÃO": 1, "REDE": 1}, "por_campo": {"direita": 335, "esquerda": 124, "centro": 54}, "lista": null}, "GOVERNADOR_2026": {"total": 27, "por_partido": {"PL": 6, "PSD": 5, "REPUBLICANOS": 4, "PP": 4, "PT": 4, "PSDB": 2, "PODE": 1, "MDB": 1}, "por_campo": {"direita": 20, "esquerda": 4, "centro": 3}, "lista": [["AC", "MAILZA ASSIS", "PP"], ["AL", "JHC", "PSDB"], ["AM", "OMAR AZIZ", "PSD"], ["AP", "DR. FURLAN", "PSD"], ["BA", "JERÔNIMO RODRIGUES", "PT"], ["CE", "ELMANO DE FREITAS", "PT"], ["DF", "CELINA LEÃO", "PP"], ["ES", "LORENZO PAZOLINI", "REPUBLICANOS"], ["GO", "DANIEL VILELA", "MDB"], ["MA", "EDUARDO BRAIDE", "PSD"], ["MG", "CLEITINHO AZEVEDO", "REPUBLICANOS"], ["MS", "EDUARDO RIEDEL", "PP"], ["MT", "OTAVIANO PIVETTA", "REPUBLICANOS"], ["PA", "DR. DANIEL", "PODE"], ["PB", "LUCAS RIBEIRO", "PP"], ["PE", "RAQUEL LYRA", "PSD"], ["PI", "RAFAEL FONTELES", "PT"], ["PR", "SERGIO MORO", "PL"], ["RJ", "DOUGLAS RUAS", "PL"], ["RN", "CADU DE LULA", "PT"], ["RO", "MARCOS ROGÉRIO", "PL"], ["RR", "ARTHUR HENRIQUE", "PL"], ["RS", "ZUCCO", "PL"], ["SC", "JORGINHO MELLO", "PL"], ["SE", "FÁBIO", "PSD"], ["SP", "TARCÍSIO", "REPUBLICANOS"], ["TO", "VICENTINHO JÚNIOR", "PSDB"]]}, "SENADOR_2026": {"total": 54, "por_partido": {"PL": 19, "MDB": 7, "PT": 6, "PSB": 3, "NOVO": 3, "PP": 3, "UNIÃO": 3, "REPUBLICANOS": 2, "PODE": 2, "PSDB": 2, "PSD": 2, "PDT": 1, "REDE": 1}, "por_campo": {"direita": 34, "centro": 9, "esquerda": 11}, "lista": null}, "DEPUTADO FEDERAL_2022": {"total": 513, "por_partido": {"PL": 98, "PT": 69, "UNIÃO": 57, "PP": 47, "PSD": 42, "MDB": 41, "REPUBLICANOS": 40, "PDT": 16, "PSB": 15, "PODE": 14, "PSDB": 13, "PSOL": 13, "PC do B": 7, "AVANTE": 7, "PV": 6, "PSC": 6, "CIDADANIA": 5, "SOLIDARIEDADE": 4, "PATRIOTA": 4, "NOVO": 3, "PROS": 3, "REDE": 2, "PTB": 1}, "por_campo": {"direita": 315, "esquerda": 128, "centro": 70}, "lista": null}, "GOVERNADOR_2022": {"total": 27, "por_partido": {"PT": 4, "UNIÃO": 4, "PSB": 3, "MDB": 3, "PSDB": 3, "PSD": 2, "PP": 2, "REPUBLICANOS": 2, "PL": 2, "NOVO": 1, "SOLIDARIEDADE": 1}, "por_campo": {"esquerda": 7, "direita": 13, "centro": 7}, "lista": [["AC", "GLADSON CAMELI", "PP"], ["AL", "PAULO DANTAS", "MDB"], ["AM", "WILSON LIMA", "UNIÃO"], ["AP", "CLÉCIO", "SOLIDARIEDADE"], ["BA", "JERÔNIMO", "PT"], ["CE", "ELMANO DE FREITAS", "PT"], ["DF", "IBANEIS ROCHA", "MDB"], ["ES", "RENATO CASAGRANDE", "PSB"], ["GO", "RONALDO CAIADO", "UNIÃO"], ["MA", "CARLOS BRANDÃO", "PSB"], ["MG", "ZEMA", "NOVO"], ["MS", "EDUARDO RIEDEL", "PSDB"], ["MT", "MAURO MENDES", "UNIÃO"], ["PA", "HELDER", "MDB"], ["PB", "JOÃO", "PSB"], ["PE", "RAQUEL LYRA", "PSDB"], ["PI", "RAFAEL FONTELES", "PT"], ["PR", "CARLOS MASSA RATINHO JUNIOR", "PSD"], ["RJ", "CLÁUDIO CASTRO", "PL"], ["RN", "FATIMA BEZERRA", "PT"], ["RO", "CORONEL MARCOS ROCHA", "UNIÃO"], ["RR", "ANTONIO DENARIUM", "PP"], ["RS", "EDUARDO LEITE", "PSDB"], ["SC", "JORGINHO MELLO", "PL"], ["SE", "FÁBIO", "PSD"], ["SP", "TARCÍSIO", "REPUBLICANOS"], ["TO", "WANDERLEI BARBOSA", "REPUBLICANOS"]]}, "SENADOR_2022": {"total": 27, "por_partido": {"PL": 8, "UNIÃO": 5, "PT": 4, "PP": 3, "REPUBLICANOS": 2, "PSD": 2, "MDB": 1, "PSC": 1, "PSB": 1}, "por_campo": {"direita": 21, "esquerda": 5, "centro": 1}, "lista": null}, "SENADO_2027_composicao": {"total": 81, "por_partido": {"PL": 27, "PT": 10, "MDB": 8, "UNIÃO": 8, "PP": 6, "PSB": 4, "REPUBLICANOS": 4, "PSD": 4, "NOVO": 3, "PODE": 2, "PSDB": 2, "PDT": 1, "REDE": 1, "PSC": 1}, "por_campo": {"esquerda": 16, "centro": 10, "direita": 55, "?": 0}}}, "crescimento_municipal": {"municipios_brasil": 5571, "cidades_exterior": 186, "votos absolutos": {"lula_cresceu": 5621, "flavio_cresceu": 4747, "lula_cresceu_so_brasil": 5491, "flavio_cresceu_so_brasil": 4624}, "% dos válidos": {"lula_cresceu": 5698, "flavio_cresceu": 3954, "lula_cresceu_so_brasil": 5567, "flavio_cresceu_so_brasil": 3830}, "ganho absoluto maior que o do adversário": {"lula_cresceu": 5323, "flavio_cresceu": 384, "lula_cresceu_so_brasil": 5228, "flavio_cresceu_so_brasil": 339}, "ganho em pontos % maior que o do adversário": {"lula_cresceu": 5490, "flavio_cresceu": 225, "lula_cresceu_so_brasil": 5389, "flavio_cresceu_so_brasil": 182}, "lider_1t_municipios": {"22": 2906, "13": 2665}, "lider_1t_aptos": {"22": 89830667, "13": 67998301}, "lider_2t_municipios": {"13": 2876, "22": 2695}, "viradas_municipais": {"22->22": 2694, "13->13": 2664, "22->13": 212, "13->22": 1}, "ref_2022_votos_absolutos": {"lula_cresceu": 4676, "bolsonaro_cresceu": 5590, "total": 5751}}, "transferencias_2026": {"v55": {"votos_1t": 2605148, "para_13": 36.8, "para_22": 55.5, "nao_valido": 7.6}, "v14": {"votos_1t": 2675887, "para_13": 36.9, "para_22": 37.1, "nao_valido": 26.0}, "v13": {"votos_1t": 53879537, "para_13": 98.7, "para_22": 0.0, "nao_valido": 1.3}, "v70": {"votos_1t": 3448568, "para_13": 67.5, "para_22": 27.6, "nao_valido": 4.9}, "v22": {"votos_1t": 56104503, "para_13": 0.2, "para_22": 97.9, "nao_valido": 1.8}, "outros": {"votos_1t": 592389, "para_13": 16.2, "para_22": 58.0, "nao_valido": 25.8}, "nao_valido": {"votos_1t": 39439045, "para_13": 12.9, "para_22": 1.3, "nao_valido": 85.8}}, "transferencias_2022": {"v13": {"votos_1t": 57259503, "para_13": 96.5, "para_22": 0.2, "nao_valido": 3.3}, "v12": {"votos_1t": 3599287, "para_13": 42.8, "para_22": 39.0, "nao_valido": 18.2}, "v22": {"votos_1t": 51072345, "para_13": 0.0, "para_22": 99.8, "nao_valido": 0.2}, "v15": {"votos_1t": 4915422, "para_13": 43.8, "para_22": 42.2, "nao_valido": 14.0}, "outros": {"votos_1t": 1383160, "para_13": 30.7, "para_22": 53.8, "nao_valido": 15.4}, "nao_valido": {"votos_1t": 38223635, "para_13": 2.9, "para_22": 4.1, "nao_valido": 92.9}}, "estados": {"2026": {"GO": {"p13_1t": 31.06, "p13_2t": 40.34, "p22_1t": 53.6, "p22_2t": 59.66, "lider_1t": 22, "lider_2t": 22}, "MT": {"p13_1t": 29.18, "p13_2t": 33.94, "p22_1t": 65.14, "p22_2t": 66.06, "lider_1t": 22, "lider_2t": 22}, "PR": {"p13_1t": 31.2, "p13_2t": 37.42, "p22_1t": 59.91, "p22_2t": 62.58, "lider_1t": 22, "lider_2t": 22}, "RS": {"p13_1t": 35.73, "p13_2t": 42.16, "p22_1t": 55.64, "p22_2t": 57.84, "lider_1t": 22, "lider_2t": 22}, "SC": {"p13_1t": 25.04, "p13_2t": 30.58, "p22_1t": 66.65, "p22_2t": 69.42, "lider_1t": 22, "lider_2t": 22}}, "2026_todas_ufs": {"AC": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 28.73, "p13_2t": 33.43, "p22_1t": 64.55, "p22_2t": 66.57}, "AL": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 54.73, "p13_2t": 60.77, "p22_1t": 40.45, "p22_2t": 39.23}, "AM": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 48.23, "p13_2t": 54.02, "p22_1t": 44.99, "p22_2t": 45.98}, "AP": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 45.71, "p13_2t": 52.88, "p22_1t": 45.66, "p22_2t": 47.12}, "BA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 66.17, "p13_2t": 71.31, "p22_1t": 28.53, "p22_2t": 28.69}, "CE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 63.28, "p13_2t": 68.93, "p22_1t": 31.27, "p22_2t": 31.07}, "DF": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 38.11, "p13_2t": 45.72, "p22_1t": 51.31, "p22_2t": 54.28}, "ES": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 37.76, "p13_2t": 43.63, "p22_1t": 54.78, "p22_2t": 56.37}, "GO": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 31.06, "p13_2t": 40.34, "p22_1t": 53.6, "p22_2t": 59.66}, "MA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 63.99, "p13_2t": 69.54, "p22_1t": 30.89, "p22_2t": 30.46}, "MG": {"lider_1t": 22, "lider_2t": 13, "p13_1t": 43.32, "p13_2t": 50.43, "p22_1t": 48.24, "p22_2t": 49.57}, "MS": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 34.68, "p13_2t": 40.4, "p22_1t": 58.6, "p22_2t": 59.6}, "MT": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 29.18, "p13_2t": 33.94, "p22_1t": 65.14, "p22_2t": 66.06}, "PA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 49.91, "p13_2t": 55.02, "p22_1t": 44.5, "p22_2t": 44.98}, "PB": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 61.31, "p13_2t": 67.46, "p22_1t": 33.07, "p22_2t": 32.54}, "PE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 63.45, "p13_2t": 69.2, "p22_1t": 31.03, "p22_2t": 30.8}, "PI": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 70.99, "p13_2t": 75.88, "p22_1t": 24.09, "p22_2t": 24.12}, "PR": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 31.2, "p13_2t": 37.42, "p22_1t": 59.91, "p22_2t": 62.58}, "RJ": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 39.41, "p13_2t": 46.9, "p22_1t": 53.01, "p22_2t": 53.1}, "RN": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 59.75, "p13_2t": 65.72, "p22_1t": 34.77, "p22_2t": 34.28}, "RO": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 25.89, "p13_2t": 30.39, "p22_1t": 67.45, "p22_2t": 69.61}, "RR": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 22.86, "p13_2t": 27.54, "p22_1t": 71.05, "p22_2t": 72.46}, "RS": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 35.73, "p13_2t": 42.16, "p22_1t": 55.64, "p22_2t": 57.84}, "SC": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 25.04, "p13_2t": 30.58, "p22_1t": 66.65, "p22_2t": 69.42}, "SE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 62.75, "p13_2t": 69.53, "p22_1t": 30.63, "p22_2t": 30.47}, "SP": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 38.2, "p13_2t": 46.15, "p22_1t": 51.93, "p22_2t": 53.85}, "TO": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 43.42, "p13_2t": 48.63, "p22_1t": 50.44, "p22_2t": 51.37}, "ZZ": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 47.55, "p13_2t": 53.86, "p22_1t": 43.47, "p22_2t": 46.14}}, "2022": {"GO": {"p13_1t": 39.51, "p13_2t": 41.29, "p22_1t": 52.16, "p22_2t": 58.71, "lider_1t": 22, "lider_2t": 22}, "MT": {"p13_1t": 34.39, "p13_2t": 34.92, "p22_1t": 59.84, "p22_2t": 65.08, "lider_1t": 22, "lider_2t": 22}, "PR": {"p13_1t": 35.99, "p13_2t": 37.6, "p22_1t": 55.26, "p22_2t": 62.4, "lider_1t": 22, "lider_2t": 22}, "RS": {"p13_1t": 42.28, "p13_2t": 43.65, "p22_1t": 48.89, "p22_2t": 56.35, "lider_1t": 22, "lider_2t": 22}, "SC": {"p13_1t": 29.54, "p13_2t": 30.73, "p22_1t": 62.21, "p22_2t": 69.27, "lider_1t": 22, "lider_2t": 22}}, "2022_todas_ufs": {"AC": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 29.26, "p13_2t": 29.7, "p22_1t": 62.5, "p22_2t": 70.3}, "AL": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 56.5, "p13_2t": 58.68, "p22_1t": 36.05, "p22_2t": 41.32}, "AM": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 49.58, "p13_2t": 51.1, "p22_1t": 42.8, "p22_2t": 48.9}, "AP": {"lider_1t": 13, "lider_2t": 22, "p13_1t": 45.67, "p13_2t": 48.64, "p22_1t": 43.41, "p22_2t": 51.36}, "BA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 69.73, "p13_2t": 72.12, "p22_1t": 24.31, "p22_2t": 27.88}, "CE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 65.91, "p13_2t": 69.97, "p22_1t": 25.38, "p22_2t": 30.03}, "DF": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 36.85, "p13_2t": 41.19, "p22_1t": 51.65, "p22_2t": 58.81}, "ES": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 40.4, "p13_2t": 41.96, "p22_1t": 52.23, "p22_2t": 58.04}, "GO": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 39.51, "p13_2t": 41.29, "p22_1t": 52.16, "p22_2t": 58.71}, "MA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 68.84, "p13_2t": 71.14, "p22_1t": 26.02, "p22_2t": 28.86}, "MG": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 48.29, "p13_2t": 50.2, "p22_1t": 43.6, "p22_2t": 49.8}, "MS": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 39.04, "p13_2t": 40.51, "p22_1t": 52.7, "p22_2t": 59.49}, "MT": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 34.39, "p13_2t": 34.92, "p22_1t": 59.84, "p22_2t": 65.08}, "PA": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 52.22, "p13_2t": 54.75, "p22_1t": 40.27, "p22_2t": 45.25}, "PB": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 64.21, "p13_2t": 66.62, "p22_1t": 29.62, "p22_2t": 33.38}, "PE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 65.27, "p13_2t": 66.93, "p22_1t": 29.91, "p22_2t": 33.07}, "PI": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 74.25, "p13_2t": 76.86, "p22_1t": 19.9, "p22_2t": 23.14}, "PR": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 35.99, "p13_2t": 37.6, "p22_1t": 55.26, "p22_2t": 62.4}, "RJ": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 40.68, "p13_2t": 43.47, "p22_1t": 51.09, "p22_2t": 56.53}, "RN": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 62.98, "p13_2t": 65.1, "p22_1t": 31.02, "p22_2t": 34.9}, "RO": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 28.98, "p13_2t": 29.34, "p22_1t": 64.36, "p22_2t": 70.66}, "RR": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 23.05, "p13_2t": 23.92, "p22_1t": 69.57, "p22_2t": 76.08}, "RS": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 42.28, "p13_2t": 43.65, "p22_1t": 48.89, "p22_2t": 56.35}, "SC": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 29.54, "p13_2t": 30.73, "p22_1t": 62.21, "p22_2t": 69.27}, "SE": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 63.82, "p13_2t": 67.21, "p22_1t": 29.16, "p22_2t": 32.79}, "SP": {"lider_1t": 22, "lider_2t": 22, "p13_1t": 40.89, "p13_2t": 44.76, "p22_1t": 47.71, "p22_2t": 55.24}, "TO": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 50.4, "p13_2t": 51.36, "p22_1t": 44.0, "p22_2t": 48.64}, "ZZ": {"lider_1t": 13, "lider_2t": 13, "p13_1t": 47.17, "p13_2t": 51.28, "p22_1t": 41.61, "p22_2t": 48.72}}}, "apuracao": {"2026_2t": {"secoes": 499248, "sem_horario_recebimento": 0, "sem_horario_totalizacao": 0, "rec": {"primeira": "2026-10-25 17:03:25", "p50": "2026-10-25 20:26:25", "p90": "2026-10-25 21:01:27", "p99": "2026-10-25 21:09:39", "ultima": "2026-10-25 23:21:40", "maior_pausa_min_ate_99pct": 34.3, "maior_pausa_inicio": "2026-10-25 17:59:08", "maior_pausa_fim": "2026-10-25 18:33:25", "pausas_maiores_que_5min": 5}, "tot": {"primeira": "2026-10-25 17:05:21", "p50": "2026-10-25 20:26:48", "p90": "2026-10-25 21:01:47", "p99": "2026-10-25 21:10:05", "ultima": "2026-10-25 23:21:51", "maior_pausa_min_ate_99pct": 115.3, "maior_pausa_inicio": "2026-10-25 17:07:37", "maior_pausa_fim": "2026-10-25 19:02:54", "pausas_maiores_que_5min": 1}, "evolucao_pct_lula_por_secoes_totalizadas": {"10%": {"hora": "2026-10-25 19:38:14", "pct_lula": 50.5}, "25%": {"hora": "2026-10-25 20:03:01", "pct_lula": 49.49}, "50%": {"hora": "2026-10-25 20:26:48", "pct_lula": 50.12}, "75%": {"hora": "2026-10-25 20:48:15", "pct_lula": 51.08}, "90%": {"hora": "2026-10-25 21:01:47", "pct_lula": 51.57}, "99%": {"hora": "2026-10-25 21:10:05", "pct_lula": 51.76}, "100%": {"hora": "2026-10-25 23:21:51", "pct_lula": 51.79}}, "trocas_de_lider_apos_1pct": 45}, "2026_1t": {"secoes": 499248, "sem_horario_recebimento": 0, "sem_horario_totalizacao": 0, "rec": {"primeira": "2026-10-04 17:08:44", "p50": "2026-10-04 18:44:51", "p90": "2026-10-04 20:13:00", "p99": "2026-10-04 21:13:46", "ultima": "2026-10-05 02:58:30", "maior_pausa_min_ate_99pct": 27.5, "maior_pausa_inicio": "2026-10-04 19:31:50", "maior_pausa_fim": "2026-10-04 19:59:22", "pausas_maiores_que_5min": 2}, "tot": {"primeira": "2026-10-04 17:08:57", "p50": "2026-10-04 18:46:51", "p90": "2026-10-04 20:16:26", "p99": "2026-10-04 21:13:52", "ultima": "2026-10-05 02:58:39", "maior_pausa_min_ate_99pct": 18.4, "maior_pausa_inicio": "2026-10-04 19:45:15", "maior_pausa_fim": "2026-10-04 20:03:42", "pausas_maiores_que_5min": 4}, "evolucao_pct_lula_por_secoes_totalizadas": {"10%": {"hora": "2026-10-04 17:53:18", "pct_lula": 44.46}, "25%": {"hora": "2026-10-04 18:20:29", "pct_lula": 44.56}, "50%": {"hora": "2026-10-04 18:46:51", "pct_lula": 45.4}, "75%": {"hora": "2026-10-04 19:17:14", "pct_lula": 46.6}, "90%": {"hora": "2026-10-04 20:16:26", "pct_lula": 47.76}, "99%": {"hora": "2026-10-04 21:13:52", "pct_lula": 48.77}, "100%": {"hora": "2026-10-05 02:58:39", "pct_lula": 48.99}}, "trocas_de_lider_apos_1pct": 0}, "2022_2t": {"secoes": 472075, "sem_horario_recebimento": 0, "sem_horario_totalizacao": 0, "rec": {"primeira": "2022-10-30 01:20:48", "p50": "2022-10-30 18:26:12", "p90": "2022-10-30 19:09:01", "p99": "2022-10-30 20:00:28", "ultima": "2022-10-31 00:17:31", "maior_pausa_min_ate_99pct": 114.5, "maior_pausa_inicio": "2022-10-30 01:20:48", "maior_pausa_fim": "2022-10-30 03:15:20", "pausas_maiores_que_5min": 34}, "tot": {"primeira": "2022-10-30 17:00:51", "p50": "2022-10-30 18:26:53", "p90": "2022-10-30 19:09:26", "p99": "2022-10-30 20:00:46", "ultima": "2022-10-31 00:18:04", "maior_pausa_min_ate_99pct": 1.0, "maior_pausa_inicio": "2022-10-30 17:01:51", "maior_pausa_fim": "2022-10-30 17:02:52", "pausas_maiores_que_5min": 0}, "evolucao_pct_lula_por_secoes_totalizadas": {"10%": {"hora": "2022-10-30 17:33:41", "pct_lula": 47.98}, "25%": {"hora": "2022-10-30 17:55:43", "pct_lula": 48.74}, "50%": {"hora": "2022-10-30 18:26:53", "pct_lula": 49.7}, "75%": {"hora": "2022-10-30 18:51:36", "pct_lula": 50.17}, "90%": {"hora": "2022-10-30 19:09:26", "pct_lula": 50.53}, "99%": {"hora": "2022-10-30 20:00:46", "pct_lula": 50.84}, "100%": {"hora": "2022-10-31 00:18:04", "pct_lula": 50.9}}, "trocas_de_lider_apos_1pct": 4}}}
```