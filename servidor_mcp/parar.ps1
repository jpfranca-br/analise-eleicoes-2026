# Para o servidor MCP iniciado por iniciar.ps1
$arqPid = Join-Path $PSScriptRoot ".mcp_pid"
if (Test-Path $arqPid) {
    $id = [int](Get-Content $arqPid)
    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
    Remove-Item $arqPid
    Write-Output "Servidor MCP (PID $id) parado."
} else {
    Write-Output "Nenhum PID registrado."
}
