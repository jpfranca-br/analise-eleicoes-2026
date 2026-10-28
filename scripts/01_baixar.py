"""Baixa os arquivos do TSE necessários para a análise.

Uso:
    python -I scripts/01_baixar.py [--anos 2026 2022] [--so-resultados] [--ufs AC SP ...] [--paralelo 4]

- Resultados por seção (votacao_secao, detalhe_votacao_secao): pequenos, sempre baixados.
- Arquivos de urna (BU + log + RDV) por UF e turno: grandes (~130 GB em 2026).
Downloads são retomáveis (HTTP Range) e conferidos pelo tamanho (Content-Length).
"""
import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS = RAIZ / "dados" / "brutos"
CDN = "https://cdn.tse.jus.br/estatistica/sead"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO", "ZZ"]


def lista_arquivos(anos, ufs, so_resultados):
    itens = []
    for ano in anos:
        itens.append((f"{CDN}/odsele/votacao_secao/votacao_secao_{ano}_BR.zip",
                      BRUTOS / "odsele" / f"votacao_secao_{ano}_BR.zip"))
        itens.append((f"{CDN}/odsele/detalhe_votacao_secao/detalhe_votacao_secao_{ano}.zip",
                      BRUTOS / "odsele" / f"detalhe_votacao_secao_{ano}.zip"))
    if so_resultados:
        return itens
    # 2026 primeiro (prioridade), turnos intercalados por UF, menores primeiro não importa
    for ano in anos:
        for uf in ufs:
            for t in ("1t", "2t"):
                nome = f"bu_imgbu_logjez_rdv_vscmr_{ano}_{t}_{uf}.zip"
                itens.append((f"{CDN}/eleicoes/eleicoes{ano}/arqurnatot/{nome}",
                              BRUTOS / "arqurna" / f"{ano}_{t}_{uf}.zip"))
    return itens


def baixa(url, destino, tentativas=8):
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(destino.suffix + ".part")
    for tentativa in range(1, tentativas + 1):
        try:
            h = requests.head(url, allow_redirects=True, timeout=60)
            if h.status_code == 404:
                return f"404 {url}"
            h.raise_for_status()
            total = int(h.headers["Content-Length"])
            if destino.exists() and destino.stat().st_size == total:
                return f"ok (já existia) {destino.name}"
            ja = parcial.stat().st_size if parcial.exists() else 0
            if ja > total:
                parcial.unlink()
                ja = 0
            cab = {"Range": f"bytes={ja}-"} if ja else {}
            with requests.get(url, headers=cab, stream=True, timeout=120) as r:
                r.raise_for_status()
                modo = "ab" if ja and r.status_code == 206 else "wb"
                with open(parcial, modo) as f:
                    for bloco in r.iter_content(chunk_size=8 << 20):
                        f.write(bloco)
            if parcial.stat().st_size == total:
                parcial.replace(destino)
                return f"ok {destino.name} ({total / 1e9:.2f} GB)"
        except Exception as e:  # rede instável: tenta de novo continuando de onde parou
            print(f"  tentativa {tentativa} falhou em {destino.name}: {e}", flush=True)
            time.sleep(min(60, 5 * tentativa))
    return f"FALHOU {destino.name}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anos", nargs="+", default=["2026", "2022"])
    ap.add_argument("--ufs", nargs="+", default=UFS)
    ap.add_argument("--so-resultados", action="store_true")
    ap.add_argument("--paralelo", type=int, default=4)
    a = ap.parse_args()

    itens = lista_arquivos(a.anos, a.ufs, a.so_resultados)
    print(f"{len(itens)} arquivos na fila", flush=True)
    falhas = []
    with ThreadPoolExecutor(a.paralelo) as ex:
        futs = {ex.submit(baixa, u, d): d for u, d in itens}
        for f in as_completed(futs):
            msg = f.result()
            print(time.strftime("%H:%M:%S"), msg, flush=True)
            if not msg.startswith("ok"):
                falhas.append(msg)
    print(f"\nConcluído. Falhas: {len(falhas)}")
    for m in falhas:
        print("  ", m)
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
