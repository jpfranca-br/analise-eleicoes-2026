"""Teste de ponta a ponta do servidor MCP (stdio): python -I servidor_mcp/testar.py"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDOR = Path(__file__).resolve().parent / "servidor.py"
CHAMADAS = [
    ("visao_geral", {}),
    ("listar_tabelas", {}),
    ("descrever_tabela", {"tabela": "escores_2026", "amostra": 2}),
    ("consultar_sql", {"sql": "SELECT uf, sum(v13_2)-sum(v22_2) AS margem FROM indicadores_2026 GROUP BY uf ORDER BY margem LIMIT 5"}),
    ("consultar_sql", {"sql": "SELECT bio, count(*) n FROM eleitores WHERE ano=2026 AND turno=2 AND uf='AC' GROUP BY bio ORDER BY bio"}),
    ("consultar_sql", {"sql": "COPY (SELECT 1) TO 'x.csv'"}),
    ("consultar_sql", {"sql": "SELECT 1; DROP VIEW eleitores"}),
    ("consultar_sql", {"sql": "SELECT * FROM read_csv('C:/Windows/win.ini')"}),
    ("buscar_municipio", {"nome": "ipixuna"}),
    ("secao", {"uf": "AM", "cd_municipio": 2550, "nr_zona": 45, "nr_secao": 63}),
    ("linha_do_tempo_secao", {"uf": "AC", "cd_municipio": 1015, "nr_zona": 2, "nr_secao": 88, "a_partir_de": "16:50"}),
    ("log_urna", {"uf": "AC", "cd_municipio": 1015, "nr_zona": 2, "nr_secao": 88, "contem": "encerr", "max_linhas": 5}),
    ("log_urna", {"uf": "AC", "cd_municipio": 1015, "nr_zona": 2, "nr_secao": 88, "ano": 2022, "turno": 1, "contem": "pronta", "max_linhas": 3}),
    ("listar_relatorios", {}),
    ("ler_relatorio", {"nome": "checagem", "tamanho": 600}),
]


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-I", "-X", "utf8", str(SERVIDOR)])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("ferramentas:", [t.name for t in tools.tools])
            for nome, args in CHAMADAS:
                res = await s.call_tool(nome, args)
                txt = "".join(getattr(c, "text", "") for c in res.content)
                print(f"\n=== {nome} {args}\n{txt[:700]}")


asyncio.run(main())
