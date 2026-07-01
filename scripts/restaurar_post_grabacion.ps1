# ===========================================================================
# restaurar_post_grabacion.ps1
#
# Deshace TODO lo que hizo preparar_grabacion.ps1:
#   1. Restaura ~/.apify/auth.json desde el backup
#   2. Restaura el comando /carruseles desde el backup
#   3. Confirma que tu proyecto real sigue intacto
#
# Si los .GRABACION_BAK ya no existen, no hace nada (ya estabas restaurado).
# ===========================================================================

Write-Host "=== RESTAURANDO ESTADO POST-GRABACION ===" -ForegroundColor Cyan
Write-Host ""

# -- 1. Restaurar token de Apify --------------------------------------------
$apifyAuth = "$env:USERPROFILE\.apify\auth.json"
$apifyBak  = "$env:USERPROFILE\.apify\auth.json.GRABACION_BAK"
if (Test-Path $apifyBak) {
    Copy-Item $apifyBak $apifyAuth -Force
    Remove-Item $apifyBak -Force
    Write-Host "[OK] Apify re-logueado (auth.json restaurado)" -ForegroundColor Green
} else {
    if (Test-Path $apifyAuth) {
        Write-Host "[i] Apify ya estaba logueado (no habia backup)" -ForegroundColor Yellow
    } else {
        Write-Host "[!] No hay backup de Apify NI auth.json activo" -ForegroundColor Red
        Write-Host "    Vas a tener que correr 'apify login' manualmente"
    }
}
Write-Host ""

# -- 2. Restaurar comando /carruseles ---------------------------------------
$cmdFile = "$env:USERPROFILE\.claude\commands\carruseles.md"
$cmdBak  = "$env:USERPROFILE\.claude\commands\carruseles.md.GRABACION_BAK"
if (Test-Path $cmdBak) {
    Move-Item $cmdBak $cmdFile -Force
    Write-Host "[OK] Comando /carruseles restaurado" -ForegroundColor Green
    Write-Host "     (cierra y reabre Claude Code para que lo detecte de nuevo)"
} else {
    if (Test-Path $cmdFile) {
        Write-Host "[i] Comando /carruseles ya estaba activo" -ForegroundColor Yellow
    } else {
        Write-Host "[!] No hay backup NI archivo activo de /carruseles" -ForegroundColor Red
        Write-Host "    Revisa ~/.claude/commands/ manualmente"
    }
}
Write-Host ""

# -- 3. Verificar que el proyecto real sigue intacto ------------------------
$projDir = "$env:USERPROFILE\Documents\Claude practicas\carruseles-ig"
$envFile = "$projDir\.env"
$configFile = "$projDir\config.json"
$catalogoFile = "$projDir\catalogo_detallado.json"

Write-Host "Verificando proyecto real:"
if (Test-Path $envFile) {
    Write-Host "  [OK] .env existe" -ForegroundColor Green
} else {
    Write-Host "  [!] .env NO existe en $projDir" -ForegroundColor Red
}
if (Test-Path $configFile) {
    Write-Host "  [OK] config.json existe" -ForegroundColor Green
} else {
    Write-Host "  [!] config.json NO existe" -ForegroundColor Red
}
if (Test-Path $catalogoFile) {
    Write-Host "  [OK] catalogo_detallado.json existe" -ForegroundColor Green
} else {
    Write-Host "  [!] catalogo_detallado.json NO existe" -ForegroundColor Red
}
Write-Host ""

# -- 4. Verificar carpeta DEMO (si existe, recordar que se puede borrar) ----
$demoDir = "$env:USERPROFILE\Documents\Claude practicas\carruseles-ig-DEMO"
if (Test-Path $demoDir) {
    Write-Host "[i] Carpeta DEMO detectada en:" -ForegroundColor Yellow
    Write-Host "    $demoDir"
    Write-Host "    Si terminaste de grabar y no la necesitas, podes borrarla:"
    Write-Host "    Remove-Item -Recurse -Force `"$demoDir`""
    Write-Host ""
}

# -- 5. Resumen final -------------------------------------------------------
Write-Host "=== RESTAURACION COMPLETA ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Estado actual:"
Write-Host "  - Apify: LOGUEADO de nuevo"
Write-Host "  - /carruseles: DISPONIBLE de nuevo (reinicia Claude Code)"
Write-Host "  - Proyecto real: verificado arriba"
Write-Host ""
Write-Host "Si algo quedo raro, los backups originales tenian sufijo .GRABACION_BAK"
Write-Host "y este script los borro al restaurar. Si necesitas auditoria:"
Write-Host "  - Tu Apify token tambien esta en el dashboard de apify.com"
Write-Host "  - El comando /carruseles esta versionado en este repo"
