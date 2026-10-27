param(
    [Parameter(Mandatory=$false)]
    [string]$RepoUrl
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ATGS - Push to GitHub Helper Script                     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not $RepoUrl) {
    $RepoUrl = Read-Host "Please enter your GitHub repository URL (e.g. https://github.com/YourUsername/ATGS.git)"
}

if (-not $RepoUrl) {
    Write-Host "Error: Repository URL cannot be empty." -ForegroundColor Red
    exit 1
}

cd $PSScriptRoot

$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    git remote set-url origin $RepoUrl
    Write-Host "Updated existing remote 'origin' to: $RepoUrl" -ForegroundColor Yellow
} else {
    git remote add origin $RepoUrl
    Write-Host "Added remote 'origin': $RepoUrl" -ForegroundColor Green
}

git branch -M main
Write-Host "Pushing main branch to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSuccessfully published ATGS to GitHub!" -ForegroundColor Green
} else {
    Write-Host "`nPush encountered an issue. Please verify your credentials or permissions." -ForegroundColor Yellow
}
