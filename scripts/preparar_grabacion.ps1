# ===========================================================================
# preparar_grabacion.ps1
#
# Pone tu maquina en estado "grabar video tutorial desde cero":
#   1. Hace backup de cosas globales (~/.apify/auth.json y comando /carruseles)
#   2. Cierra sesion de Apify CLI
#   3. Renombra el comando /carruseles para que NO funcione en el video
#   4. Sugiere crear un proyecto DEMO paralelo (no toca el real)
#
# NO toca:
#   - Tu proyecto real carruseles-ig/
#   - Tu repo en GitHub
#   - Tus carruseles publicados
#   - Tu .env real (queda intacto en tu proyecto)
#
# Para restaurar TODO despues de grabar: restaurar_post_grabacion.ps1
# ===========================================================================

Write-Host "=== PREPARANDO MAQUINA PARA GRABACION ===" -ForegroundColor Cyan
Write-Host ""

# -- 1. Backup del token de Apify -------------------------------------------
$apifyAuth = "$env:USERPROFILE\.apify\auth.json"
$apifyBak  = "$env:USERPROFILE\.apify\auth.json.GRABACION_BAK"
if (Test-Path $apifyAuth) {
    Copy-Item $apifyAuth $apifyBak -Force
    Write-Host "[OK] Backup Apify token: $apifyBak" -ForegroundColor Green
    Remove-Item $apifyAuth -Force
    Write-Host "[OK] apify logout (auth.json eliminado)" -ForegroundColor Green
} else {
    Write-Host "[i] Apify ya estaba deslogueado" -ForegroundColor Yellow
}
Write-Host ""

# -- 2. Backup del comando /carruseles --------------------------------------
$cmdFile = "$env:USERPROFILE\.claude\commands\carruseles.md"
$cmdBak  = "$env:USERPROFILE\.claude\commands\carruseles.md.GRABACION_BAK"
if (Test-Path $cmdFile) {
    Move-Item $cmdFile $cmdBak -Force
    Write-Host "[OK] Comando /carruseles oculto temporalmente" -ForegroundColor Green
    Write-Host "     (renombrado a .GRABACION_BAK - Claude Code no lo vera)"
} else {
    Write-Host "[i] Comando /carruseles no existia" -ForegroundColor Yellow
}
Write-Host ""

# -- 3. Listar el estado de tu .env real (informativo) ----------------------
$envFile = "$env:USERPROFILE\Documents\Claude practicas\carruseles-ig\.env"
if (Test-Path $envFile) {
    Write-Host "[i] Tu .env REAL en carruseles-ig/ NO se toca:" -ForegroundColor Yellow
    Write-Host "    $envFile"
    Write-Host "    (sigue teniendo tus keys de Kie/Telegram intactas)"
    Write-Host ""
    Write-Host "[!] Para el DEMO no uses ese proyecto. Crea uno nuevo:" -ForegroundColor Yellow
    Write-Host "    ej: C:\Users\LAPTOP\Documents\Claude practicas\carruseles-ig-DEMO\"
}
Write-Host ""

# -- 4. Resumen final -------------------------------------------------------
Write-Host "=== LISTO PARA GRABAR ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Estado actual:"
Write-Host "  - Apify: DESLOGUEADO (token en backup)"
Write-Host "  - /carruseles: NO disponible (en backup)"
Write-Host "  - Tu proyecto real: INTACTO"
Write-Host ""
Write-Host "ANTES de grabar:"
Write-Host "  1. Cerrar y reabrir Claude Code (para que detecte que /carruseles ya no existe)"
Write-Host "  2. Crear carpeta nueva carruseles-ig-DEMO para grabar ahi"
Write-Host "  3. Tener los tokens REALES en un Notepad aparte (Apify, Kie, Telegram)"
Write-Host "     para pegarlos cuando el video lo muestre - NO mostrarlos en pantalla"
Write-Host ""
Write-Host "DESPUES de grabar:"
Write-Host "  Corre restaurar_post_grabacion.ps1"
