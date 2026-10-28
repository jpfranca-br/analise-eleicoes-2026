# Inicia o servidor MCP em segundo plano (desacoplado do terminal), ouvindo só em 127.0.0.1 (para túnel/proxy local).
# Uso:   powershell -ExecutionPolicy Bypass -File servidor_mcp\iniciar.ps1 [-Porta 8000]
# Parar: powershell -ExecutionPolicy Bypass -File servidor_mcp\parar.ps1
# O token fica em servidor_mcp\.mcp_token (gerado na 1ª execução). Não versionar esse arquivo.
param([int]$Porta = 8000)
$raiz = Split-Path -Parent $PSScriptRoot
$arqToken = Join-Path $PSScriptRoot ".mcp_token"
if (-not (Test-Path $arqToken)) {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()   # compatível com Windows PowerShell 5
    $rng.GetBytes($bytes)
    $rng.Dispose()
    if (($bytes | Measure-Object -Sum).Sum -eq 0) { throw "falha ao gerar token aleatório" }
    ([System.BitConverter]::ToString($bytes) -replace "-", "").ToLower() | Set-Content -NoNewline -Encoding ascii $arqToken
}
$env:MCP_TOKEN = (Get-Content -Raw $arqToken).Trim()
$env:ELEICOES_RAIZ = $raiz
$logs = Join-Path $raiz "logs"
New-Item -ItemType Directory -Force $logs | Out-Null
$py = Join-Path $raiz ".venv\Scripts\python.exe"
$p = Start-Process -FilePath $py -ArgumentList @("-I", "-X", "utf8", "`"$raiz\servidor_mcp\servidor.py`"", "--http", "--host", "127.0.0.1", "--porta", "$Porta") `
    -WorkingDirectory $raiz -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $logs "mcp_servidor.out.log") -RedirectStandardError (Join-Path $logs "mcp_servidor.err.log")
$p.Id | Set-Content -Encoding ascii (Join-Path $PSScriptRoot ".mcp_pid")
Write-Output "Servidor MCP iniciado (PID $($p.Id)) em http://127.0.0.1:$Porta/mcp"
