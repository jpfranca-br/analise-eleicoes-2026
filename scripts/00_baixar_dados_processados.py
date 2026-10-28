"""Baixa da Release do GitHub os votos individuais extraídos dos logs (dados/processados/logs, ~1,9 GB),
para usar a análise e o servidor MCP sem baixar os ~363 GB brutos do TSE nem rodar o pipeline.

Uso:  python -I scripts/00_baixar_dados_processados.py --repo <dono>/<repositorio> [--tag dados-v1]
"""
import argparse
import zipfile
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "dados" / "processados"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="ex.: jpfranca-br/analise-eleicoes-2026")
    ap.add_argument("--tag", default="dados-v1")
    a = ap.parse_args()
    rel = requests.get(f"https://api.github.com/repos/{a.repo}/releases/tags/{a.tag}", timeout=60)
    rel.raise_for_status()
    pasta = RAIZ / "release"
    pasta.mkdir(exist_ok=True)
    for asset in rel.json()["assets"]:
        if not asset["name"].endswith(".zip"):
            continue
        alvo = pasta / asset["name"]
        if not (alvo.exists() and alvo.stat().st_size == asset["size"]):
            print(f"baixando {asset['name']} ({asset['size'] / 1e9:.2f} GB)")
            with requests.get(asset["browser_download_url"], stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(alvo, "wb") as f:
                    for bloco in r.iter_content(8 << 20):
                        f.write(bloco)
        with zipfile.ZipFile(alvo) as z:
            for nome in z.namelist():  # só parquets dentro de logs/, sem caminhos absolutos
                if nome.startswith("logs/") and nome.endswith(".parquet") and ".." not in nome:
                    z.extract(nome, DESTINO)
        print(f"extraído: {asset['name']}")
    print("pronto:", DESTINO / "logs")


if __name__ == "__main__":
    main()
