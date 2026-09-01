# Sincroniza assets desde el monorepo padre hacia applications/backend.
# Ejecutar desde applications/ mientras conviva dentro del repo principal.

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
$backend = Join-Path $PSScriptRoot ".." "backend"

Write-Host "Sincronizando desde $repoRoot hacia $backend"

$modelSrc = Join-Path $repoRoot "models\mbert-sv"
$modelDst = Join-Path $backend "models\mbert-sv"
if (-not (Test-Path $modelSrc)) {
    Write-Error "No se encontró $modelSrc. Descomprima artifacts/mbert-sv-audit.zip primero."
}
New-Item -ItemType Directory -Force -Path (Join-Path $backend "models") | Out-Null
if (Test-Path $modelDst) { Remove-Item $modelDst -Recurse -Force }
Copy-Item $modelSrc $modelDst -Recurse

New-Item -ItemType Directory -Force -Path (Join-Path $backend "config") | Out-Null
Copy-Item (Join-Path $repoRoot "config\settings.yaml") (Join-Path $backend "config\") -Force

New-Item -ItemType Directory -Force -Path (Join-Path $backend "metrics") | Out-Null
Copy-Item (Join-Path $repoRoot "reports\metrics\mbert_official_run.json") (Join-Path $backend "metrics\") -Force
Copy-Item (Join-Path $repoRoot "reports\metrics\slice_metrics.json") (Join-Path $backend "metrics\") -Force

Write-Host "Listo: modelo, config y métricas copiados al backend."
