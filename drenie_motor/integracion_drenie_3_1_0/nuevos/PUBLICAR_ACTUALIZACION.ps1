# DrenIE · Publica una versión nueva para que las copias instaladas se actualicen solas.
#
#   powershell -ExecutionPolicy Bypass -File PUBLICAR_ACTUALIZACION.ps1 -Repositorio usuario/drenie-actualizaciones -Notas "Qué cambió"
#
# Toma el instalador del cliente de la última compilación (SALIDA\<versión-fecha>\CLIENTE, con su firma .sig, que sale cuando
# PROBAR_Y_COMPILAR.ps1 encuentra la clave de GENERAR_CLAVE_ACTUALIZACIONES.ps1), arma latest.json y crea la versión en GitHub
# con el programa gh (https://cli.github.com, sesión iniciada con «gh auth login»). DrenIE solo instala el instalador si la firma
# corresponde a la clave pública que lleva dentro: un archivo cambiado o firmado con otra clave se rechaza.
[CmdletBinding()]
param([Parameter(Mandatory = $true)][string]$Repositorio, [string]$Notas = '', [string]$Carpeta = '')

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (!(Get-Command gh -ErrorAction SilentlyContinue)) { throw 'Falta el programa gh (GitHub CLI): instálelo e inicie sesión con «gh auth login».' }
$conf = Get-Content -LiteralPath (Join-Path $root 'client\src-tauri\tauri.conf.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$version = $conf.version
if (!$conf.plugins.updater.pubkey) { throw 'Primero ejecute GENERAR_CLAVE_ACTUALIZACIONES.ps1 y vuelva a compilar.' }
if (!$Carpeta) {
  $ultima = Get-ChildItem -LiteralPath (Join-Path $root 'SALIDA') -Directory | Where-Object { $_.Name -like "$version-*" } | Sort-Object LastWriteTime | Select-Object -Last 1
  if (!$ultima) { throw "No hay una compilación de la versión $version en SALIDA." }
  $Carpeta = Join-Path $ultima.FullName 'CLIENTE'
}
$nombre = "DrenIE_${version}_x64-setup.exe"
$instalador = Join-Path $Carpeta $nombre
$firma = $instalador + '.sig'
if (!(Test-Path -LiteralPath $instalador)) { throw "No se encontró $instalador." }
if (!(Test-Path -LiteralPath $firma)) { throw "Falta la firma ${firma}: compile con PROBAR_Y_COMPILAR.ps1 teniendo la clave de actualizaciones." }
$etiqueta = "v$version"
$latest = [ordered]@{
  version   = $version
  notes     = $Notas
  pub_date  = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
  platforms = [ordered]@{
    'windows-x86_64' = [ordered]@{
      signature = (Get-Content -LiteralPath $firma -Raw).Trim()
      url       = "https://github.com/$Repositorio/releases/download/$etiqueta/$nombre"
    }
  }
}
$json = Join-Path $Carpeta 'latest.json'
[IO.File]::WriteAllText($json, ($latest | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding $false))
& gh release create $etiqueta $instalador $json --repo $Repositorio --title "DrenIE $version" --notes ($(if ($Notas) { $Notas } else { "DrenIE $version" }))
if ($LASTEXITCODE -ne 0) { throw 'GitHub no aceptó la publicación (revise la sesión de gh y que la etiqueta no exista).' }
Write-Host "Publicada DrenIE $version. Las copias instaladas la ofrecerán al abrir el programa (una vez al día) o con «Buscar actualización»." -ForegroundColor Green
