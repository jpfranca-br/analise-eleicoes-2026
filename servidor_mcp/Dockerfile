FROM python:3.13-slim
WORKDIR /app
COPY servidor_mcp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY servidor_mcp/servidor.py /app/servidor_mcp/servidor.py
# dados entram por volume (somente leitura): /dados/dados/processados, /dados/saida e, opcionalmente, /dados/dados/brutos/arqurna
ENV ELEICOES_RAIZ=/dados MCP_HOST=0.0.0.0 MCP_PORTA=8000
RUN useradd -m mcp
USER mcp
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saude')"
CMD ["python", "-I", "-X", "utf8", "/app/servidor_mcp/servidor.py", "--http"]
