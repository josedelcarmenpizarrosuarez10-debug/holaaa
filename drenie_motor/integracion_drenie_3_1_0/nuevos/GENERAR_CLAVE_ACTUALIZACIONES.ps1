# DrenIE 3.1.0 · Clave de las actualizaciones automáticas (se ejecuta UNA sola vez, en la PC del propietario).
#
#   powershell -ExecutionPolicy Bypass -File GENERAR_CLAVE_ACTUALIZACIONES.ps1 -Repositorio usuario/drenie-actualizaciones
#
# Genera el par de claves de firma de Tauri:
#   - la clave PRIVADA queda en %USERPROFILE%\DrenIE_Actualizaciones_PRIVADO\drenie-actualizaciones.key (protegida con la
#     contraseña que usted escriba). Nadie más debe tenerla: con ella se firman las versiones nuevas. Guarde una copia en una
#     memoria USB. Si la pierde, las copias instaladas ya no aceptarán actualizaciones y habrá que reinstalar a mano.
#   - la clave PÚBLICA se escribe en client\src-tauri\tauri.conf.json (plugins.updater.pubkey), junto con la dirección donde
#     DrenIE busca las versiones nuevas: https://github.com/<Repositorio>/releases/latest/download/latest.json
# El repositorio de GitHub debe ser público y llevar solo los instaladores (nunca el código ni las claves).
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$Repositorio)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if ($Repositorio -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'El repositorio va como usuario/nombre, por ejemplo hidroconsult/drenie-actualizaciones.' }
$carpeta = Join-Path $env:USERPROFILE 'DrenIE_Actualizaciones_PRIVADO'
$clave = Join-Path $carpeta 'drenie-actualizaciones.key'
if (Test-Path -LiteralPath $clave) {
  throw "Ya existe una clave en $clave. No la reemplace: las copias instaladas solo aceptan versiones firmadas con ella."
}
New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
Push-Location (Join-Path $root 'client')
try {
  Write-Host 'Escriba una contraseña para la clave (la pedirá cada vez que compile una versión para publicar).' -ForegroundColor Cyan
  & pnpm tauri signer generate --write-keys $clave
  if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar la clave.' }
} finally { Pop-Location }
$publica = (Get-Content -LiteralPath ($clave + '.pub') -Raw).Trim()
if (!$publica) { throw 'No se encontró la clave pública generada.' }
$conf = Join-Path $root 'client\src-tauri\tauri.conf.json'
$texto = [IO.File]::ReadAllText($conf)
$texto = $texto -replace '"pubkey":\s*"[^"]*"', ('"pubkey": "' + $publica + '"')
$texto = $texto -replace '"endpoints":\s*\[[^\]]*\]', ('"endpoints": [ "https://github.com/' + $Repositorio + '/releases/latest/download/latest.json" ]')
[IO.File]::WriteAllText($conf, $texto, (New-Object Text.UTF8Encoding $false))
Write-Host "Listo. Clave privada: $clave (guarde una copia fuera de la PC)." -ForegroundColor Green
Write-Host 'La clave pública y la dirección de las actualizaciones quedaron en tauri.conf.json. Compile con PROBAR_Y_COMPILAR.ps1 y publique con PUBLICAR_ACTUALIZACION.ps1.' -ForegroundColor Green
