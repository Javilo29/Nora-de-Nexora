# Nora v5.9.5 — Libera espacio en C: (modelos DeepFace en perfil + caché pip)
# Ejecutar: PowerShell → .\limpieza_discos_nora.ps1

$ErrorActionPreference = "Continue"
$df = Join-Path $env:USERPROFILE ".deepface"
if (Test-Path $df) {
    Remove-Item -LiteralPath $df -Recurse -Force
    Write-Host "OK: eliminado $df"
} else {
    Write-Host "Info: no existe $df (nada que borrar)"
}

try {
    & pip cache purge 2>&1 | Write-Host
    Write-Host "OK: pip cache purge ejecutado"
} catch {
    Write-Host "Aviso: pip cache purge: $_"
}

Write-Host "Limpieza terminada."
