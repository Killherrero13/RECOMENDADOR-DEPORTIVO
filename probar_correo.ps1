# Envía un único correo de demostración por Gmail. No consulta fuentes deportivas.
$ErrorActionPreference = 'Stop'
$pythonPrueba = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPrueba)) {
    throw 'Primero crea el entorno .venv como indica README.md.'
}
$variablesCorreo = @('SMTP_USERNAME', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_TO')
$valoresPrevios = @{}
foreach ($nombreCorreo in $variablesCorreo) {
    $valoresPrevios[$nombreCorreo] = [Environment]::GetEnvironmentVariable($nombreCorreo, 'Process')
}
$codigoPrueba = 1
try {
    $env:SMTP_USERNAME = (Read-Host 'Tu cuenta Gmail remitente').Trim()
    $destinoPrueba = (Read-Host 'Email de destino (Enter para enviártelo a ti mismo)').Trim()
    $env:EMAIL_TO = if ($destinoPrueba) { $destinoPrueba } else { $env:SMTP_USERNAME }
    $env:EMAIL_FROM = $env:SMTP_USERNAME
    $claveCorreoTemporal = Read-Host 'Contraseña de aplicación de Google (no tu contraseña habitual)' -AsSecureString
    $env:SMTP_PASSWORD = [System.Net.NetworkCredential]::new('', $claveCorreoTemporal).Password
    Push-Location -LiteralPath $PSScriptRoot
    try {
        & $pythonPrueba -X utf8 -m resumen --sin-conexion --enviar
        $codigoPrueba = $LASTEXITCODE
    } finally {
        Pop-Location
    }
} finally {
    foreach ($nombreCorreo in $variablesCorreo) {
        [Environment]::SetEnvironmentVariable($nombreCorreo, $valoresPrevios[$nombreCorreo], 'Process')
    }
    if ($null -ne $claveCorreoTemporal) { $claveCorreoTemporal.Dispose() }
    Remove-Variable claveCorreoTemporal -ErrorAction SilentlyContinue
}
exit $codigoPrueba
