"""Monta a tabela de resultados por seção (cargo Presidente), 1º e 2º turno.

Uso:  python -I scripts/02_resultados.py [--anos 2026 2022]

Fontes (dados/brutos/odsele):
  detalhe_votacao_secao_{ano}.zip  -> aptos, comparecimento, abstenções, brancos, nulos, urna
  votacao_secao_{ano}_BR.zip       -> votos por candidato
Saída: dados/processados/resultados_{ano}.parquet (1 linha por seção e turno)
       dados/processados/candidatos_{ano}.parquet (número -> nome)
"""
import argparse
import zipfile
from pathlib import Path

import polars as pl

RAIZ = Path(__file__).resolve().parent.parent
ODS = RAIZ / "dados" / "brutos" / "odsele"
PROC = RAIZ / "dados" / "processados"
CHAVE = ["turno", "uf", "cd_municipio", "nr_zona", "nr_secao"]


def le_csv(zip_path, membro, colunas):
    with zipfile.ZipFile(zip_path) as z:
        dados = z.read(membro)
    return pl.read_csv(dados, separator=";", encoding="latin1", columns=colunas,
                       infer_schema_length=0)


def detalhe(ano):
    cols = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO",
            "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS_NOMINAIS",
            "QT_VOTOS_BRANCOS", "QT_VOTOS_NULOS", "NR_LOCAL_VOTACAO", "NM_LOCAL_VOTACAO",
            "DT_RECEBIMENTO_BU_HOR_TSE", "DS_ORIGEM_VOTO", "ST_SECAO_INSTALADA",
            "ST_SECAO_ANULADA", "DS_MODELO_URNA"]
    with zipfile.ZipFile(ODS / f"detalhe_votacao_secao_{ano}.zip") as z:
        membro = f"detalhe_votacao_secao_{ano}_BR.csv"
        cab = z.open(membro).readline().decode("latin1")
    cols = [c for c in cols if f'"{c}"' in cab]  # alguns campos não existem em 2022
    d = le_csv(ODS / f"detalhe_votacao_secao_{ano}.zip", membro, cols)
    d = d.filter(pl.col("CD_CARGO") == "1")
    ints = {"NR_TURNO": "turno", "CD_MUNICIPIO": "cd_municipio", "NR_ZONA": "nr_zona",
            "NR_SECAO": "nr_secao", "QT_APTOS": "aptos", "QT_COMPARECIMENTO": "comparecimento",
            "QT_ABSTENCOES": "abstencoes", "QT_VOTOS_NOMINAIS": "nominais",
            "QT_VOTOS_BRANCOS": "brancos", "QT_VOTOS_NULOS": "nulos",
            "NR_LOCAL_VOTACAO": "nr_local"}
    outros = {"SG_UF": "uf", "NM_MUNICIPIO": "nm_municipio", "NM_LOCAL_VOTACAO": "nm_local",
              "DT_RECEBIMENTO_BU_HOR_TSE": "dt_recebimento_bu", "DS_ORIGEM_VOTO": "origem_voto",
              "ST_SECAO_INSTALADA": "instalada", "ST_SECAO_ANULADA": "anulada",
              "DS_MODELO_URNA": "modelo_urna"}
    return d.select([pl.col(k).cast(pl.Int64).alias(v) for k, v in ints.items() if k in cols]
                    + [pl.col(k).alias(v) for k, v in outros.items() if k in cols])


def votos(ano):
    cols = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "CD_CARGO",
            "NR_VOTAVEL", "NM_VOTAVEL", "QT_VOTOS"]
    v = le_csv(ODS / f"votacao_secao_{ano}_BR.zip", f"votacao_secao_{ano}_BR.csv", cols)
    v = v.filter(pl.col("CD_CARGO") == "1").select(
        pl.col("NR_TURNO").cast(pl.Int64).alias("turno"), pl.col("SG_UF").alias("uf"),
        pl.col("CD_MUNICIPIO").cast(pl.Int64).alias("cd_municipio"),
        pl.col("NR_ZONA").cast(pl.Int64).alias("nr_zona"),
        pl.col("NR_SECAO").cast(pl.Int64).alias("nr_secao"),
        pl.col("NR_VOTAVEL").cast(pl.Int64).alias("nr"), pl.col("NM_VOTAVEL").alias("nome"),
        pl.col("QT_VOTOS").cast(pl.Int64).alias("qt"))
    cand = v.group_by("nr", "nome").agg(pl.col("qt").sum()).sort("qt", descending=True)
    larga = (v.filter(~pl.col("nr").is_in([95, 96]))
              .with_columns(("v" + pl.col("nr").cast(pl.Utf8)).alias("col"))
              .pivot(on="col", index=CHAVE, values="qt", aggregate_function="sum")
              .fill_null(0))
    return larga, cand


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs="+", default=["2026", "2022"])
    a = ap.parse_args()
    PROC.mkdir(parents=True, exist_ok=True)
    for ano in a.anos:
        d = detalhe(ano)
        larga, cand = votos(ano)
        r = d.join(larga, on=CHAVE, how="left").with_columns(pl.lit(int(ano)).alias("ano"))
        vcols = [c for c in r.columns if c.startswith("v") and c[1:].isdigit()]
        r = r.with_columns([pl.col(c).fill_null(0) for c in vcols])
        # checagem: soma dos candidatos = votos nominais
        dif = r.filter(pl.sum_horizontal(vcols) != pl.col("nominais")).height
        r.write_parquet(PROC / f"resultados_{ano}.parquet")
        cand.write_parquet(PROC / f"candidatos_{ano}.parquet")
        print(f"{ano}: {r.height} seção-turno | por turno: "
              f"{dict(r.group_by('turno').len().sort('turno').iter_rows())} | "
              f"divergência nominais: {dif}")
        print(cand.head(6))


if __name__ == "__main__":
    main()
