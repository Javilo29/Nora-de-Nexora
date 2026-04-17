# Limpieza de emergencia en C: — Bloatware IA (TensorFlow / DeepFace / pesos)
# Ejecutar en PowerShell del usuario Javier (no requiere admin salvo permisos en su perfil).

$ErrorActionPreference = "Continue"

function Get-CFreeGB {
    $b = (Get-PSDrive -Name C -ErrorAction SilentlyContinue).Free
    if ($null -eq $b) { return $null }
    return [math]::Round($b / 1GB, 2)
}

$antes = Get-CFreeGB
Write-Host "Espacio libre en C: antes: $antes GB (aprox.)"

Write-Host "`n--- pip uninstall (tensorflow / keras / deepface / opencv pesado) ---"
pip uninstall -y tensorflow keras deepface opencv-python-headless opencv-python tf-keras keras-nightly tensorflow-cpu tensorflow-intel 2>$null

Write-Host "`n--- pip cache purge ---"
pip cache purge

Write-Host "`n--- Eliminar %USERPROFILE%\.deepface (modelos .h5 / pesos) ---"
$df = Join-Path $env:USERPROFILE ".deepface"
if (Test-Path $df) {
    $sz = (Get-ChildItem $df -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
    Remove-Item -Recurse -Force $df
    Write-Host "Eliminado: $df (~ $([math]::Round($sz/1GB,2)) GB)"
} else {
    Write-Host "No existe: $df"
}

Write-Host "`n--- Caché pip en AppData (opcional): borrar subcarpeta http ---"
$pipCache = Join-Path $env:LOCALAPPDATA "pip\cache"
if (Test-Path $pipCache) {
    Remove-Item -Recurse -Force (Join-Path $pipCache "*") -ErrorAction SilentlyContinue
    Write-Host "Vaciado: $pipCache"
}

$despues = Get-CFreeGB
Write-Host "`nEspacio libre en C: después: $despues GB (aprox.)"
if ($null -ne $antes -and $null -ne $despues) {
    $delta = [math]::Round($despues - $antes, 2)
    Write-Host "Cambio aproximado: $delta GB (positivo = más libre)"
}
