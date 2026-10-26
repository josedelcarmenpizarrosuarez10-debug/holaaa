# DrenIE · Mueve las carpetas privadas de claves al disco D: (sobreviven a un formateo de C:).
#
#   Mover (la primera vez):          clic derecho > Ejecutar con PowerShell
#                                    o: powershell -ExecutionPolicy Bypass -File .\MOVER_CLAVES_A_D.ps1
#   Después de formatear la PC:      powershell -ExecutionPolicy Bypass -File .\MOVER_CLAVES_A_D.ps1 -Restaurar
#
# Qué hace (solo con su usuario de Windows; no muestra ni envía el contenido de ninguna clave):
#   1. Copia %USERPROFILE%\DrenIE_Propietario_PRIVADO y %USERPROFILE%\DrenIE_Actualizaciones_PRIVADO a D:\DrenIE_PRIVADO.
#   2. Comprueba que cada archivo copiado sea idéntico al original (SHA256).
#   3. Deja permisos solo para su usuario (y SYSTEM) en D:\DrenIE_PRIVADO.
#   4. Renombra los originales a <carpeta>_ANTIGUO_BORRAR (no los borra) y crea en su lugar un enlace de carpeta (junction)
#      con el mismo nombre que apunta a D:. El Administrador de licencias y PROBAR_Y_COMPILAR.ps1 siguen encontrando las
#      claves en la ruta de siempre: no hay que cambiar nada del programa.
# Con -Restaurar (PC recién formateada) solo vuelve a crear los enlaces hacia D:\DrenIE_PRIVADO.
[CmdletBinding()]
param([switch]$Restaurar, [string]$Destino = 'D:\DrenIE_PRIVADO')

$ErrorActionPreference = 'Stop'
$carpetas = @('DrenIE_Propietario_PRIVADO', 'DrenIE_Actualizaciones_PRIVADO')

function Es-Enlace([string]$ruta) {
  $i = Get-Item -LiteralPath $ruta -Force -ErrorAction SilentlyContinue
  return [bool]($i -and ($i.Attributes -band [IO.FileAttributes]::ReparsePoint))
}
function Huellas([string]$raiz) {
  $h = @{}
  Get-ChildItem -LiteralPath $raiz -Recurse -File -Force | ForEach-Object {
    $h[$_.FullName.Substring($raiz.Length).TrimStart('\')] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
  }
  return $h
}
function Salir([int]$codigo) {
  Read-Host 'Pulse Enter para cerrar' | Out-Null   # con «Ejecutar con PowerShell» la ventana se cerraría sin dejar leer
  exit $codigo
}
function Enlazar([string]$enlace, [string]$objetivo) {
  New-Item -ItemType Junction -Path $enlace -Target $objetivo | Out-Null
  Write-Host "  Enlace creado: $enlace -> $objetivo" -ForegroundColor Green
}

try {
  $unidad = Split-Path -Qualifier $Destino
  if (!(Test-Path -LiteralPath ($unidad + '\'))) { throw "No existe la unidad $unidad en esta PC." }
  foreach ($nube in @($env:OneDrive, $env:OneDriveConsumer, $env:OneDriveCommercial) | Where-Object { $_ }) {
    if ($Destino.StartsWith($nube, [StringComparison]::OrdinalIgnoreCase)) { throw 'El destino está dentro de OneDrive: las claves no deben sincronizarse con la nube.' }
  }
  foreach ($palabra in @('OneDrive', 'Dropbox', 'Google Drive', 'iCloud', 'Codex', 'chatgpt')) {
    if ($Destino.IndexOf($palabra, [StringComparison]::OrdinalIgnoreCase) -ge 0) { throw "El destino ($Destino) parece una carpeta sincronizada ($palabra). Use una carpeta local, por ejemplo D:\DrenIE_PRIVADO." }
  }

  if ($Restaurar) {
    Write-Host "Restaurando los enlaces hacia $Destino" -ForegroundColor Cyan
    foreach ($c in $carpetas) {
      $origen = Join-Path $env:USERPROFILE $c; $nuevo = Join-Path $Destino $c
      if (!(Test-Path -LiteralPath $nuevo)) { Write-Host "  No está $nuevo (se omite)." -ForegroundColor Yellow; continue }
      if (Es-Enlace $origen) { Write-Host "  Ya existe el enlace $origen." -ForegroundColor Green; continue }
      if (Test-Path -LiteralPath $origen) { throw "Ya existe una carpeta real $origen. Revísela antes: este script no la reemplaza." }
      Enlazar $origen $nuevo
    }
    Write-Host "`nListo. Abra el Administrador de licencias: si pide restaurar, use su respaldo .drenbackup." -ForegroundColor Green
    Salir 0
  }

  Write-Host "Moviendo las carpetas privadas a $Destino" -ForegroundColor Cyan
  New-Item -ItemType Directory -Force -Path $Destino | Out-Null
  # Permisos: solo el usuario actual y SYSTEM (sin herencia de la unidad D:)
  & icacls $Destino /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "No se pudieron fijar los permisos de $Destino (icacls $LASTEXITCODE)." }
  $movidas = 0
  foreach ($c in $carpetas) {
    $origen = Join-Path $env:USERPROFILE $c; $nuevo = Join-Path $Destino $c
    if (Es-Enlace $origen) { Write-Host "  $c ya apunta a otra ubicación (enlace): no se toca." -ForegroundColor Green; continue }
    if (!(Test-Path -LiteralPath $origen)) { Write-Host "  No existe $origen (se omite)." -ForegroundColor Yellow; continue }
    if (Test-Path -LiteralPath $nuevo) { throw "Ya existe $nuevo. Para no pisar una clave, revise esa carpeta y vuelva a ejecutar." }
    Write-Host "  Copiando $c ..."
    & robocopy $origen $nuevo /E /COPY:DAT /DCOPY:DAT /R:2 /W:2 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy no pudo copiar $c (código $LASTEXITCODE)." }
    $a = Huellas $origen; $b = Huellas $nuevo
    $distintos = @($a.Keys | Where-Object { $b[$_] -ne $a[$_] })
    if ($a.Count -eq 0 -or $a.Count -ne $b.Count -or $distintos.Count) { throw "La copia de $c no es idéntica: no se cambió nada en C:. Revise $nuevo." }
    Write-Host "  Copia verificada: $($a.Count) archivo(s) idénticos (SHA256)." -ForegroundColor Green
    $antiguo = $origen + '_ANTIGUO_BORRAR'
    if (Test-Path -LiteralPath $antiguo) { throw "Ya existe $antiguo: bórrelo o renómbrelo y vuelva a ejecutar." }
    Rename-Item -LiteralPath $origen -NewName (Split-Path -Leaf $antiguo)
    Enlazar $origen $nuevo
    $movidas++
  }
  Write-Host ''
  Write-Host "LISTO: $movidas carpeta(s) en $Destino." -ForegroundColor Green
  Write-Host '1. Abra el Administrador de licencias y genere una licencia de prueba: debe funcionar igual.'
  Write-Host '2. Cuando lo compruebe, borre las carpetas *_ANTIGUO_BORRAR de su carpeta de usuario.'
  Write-Host "3. Guarde además una copia de $Destino en una USB que guarde en otro lugar (D: es el mismo disco físico)."
  Write-Host '4. Al formatear: los datos del Administrador (licencias emitidas) se recuperan con su respaldo .drenbackup;'
  Write-Host '   luego ejecute este script con -Restaurar.'
  Salir 0
} catch {
  Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
  Write-Host 'No se borró ninguna clave.' -ForegroundColor Red
  Salir 1
}
