# Ouroboros System - Worktree Setup Script
# Configures optimal Git worktree setup for the Ouroboros System repository

param(
    [switch]$SetupConfig,
    [switch]$CreateAliases,
    [switch]$CreateFunctions,
    [switch]$Cleanup,
    [switch]$All
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Get repository root
$repoRoot = git rev-parse --show-toplevel
if (-not $repoRoot) {
    Write-Error "Not in a Git repository!"
    exit 1
}

Write-Info "Repository root: $repoRoot"
Set-Location $repoRoot

# Setup Git configuration
function Setup-GitConfig {
    Write-Info "`n=== Setting up Git worktree configuration ==="
    
    # Worktree settings
    git config worktree.pruneExpire "never"
    git config fetch.prune true
    git config fetch.pruneTags true
    
    Write-Success "✓ Git worktree configuration updated"
}

# Create worktrees directory
function Setup-WorktreeDirectory {
    Write-Info "`n=== Creating worktrees directory ==="
    
    $worktreeDir = Join-Path $repoRoot "worktrees"
    if (-not (Test-Path $worktreeDir)) {
        New-Item -ItemType Directory -Path $worktreeDir | Out-Null
        Write-Success "✓ Created worktrees directory: $worktreeDir"
    } else {
        Write-Info "✓ Worktrees directory already exists"
    }
}

# Create Git aliases
function Setup-GitAliases {
    Write-Info "`n=== Setting up Git aliases ==="
    
    $aliases = @{
        "wt-list" = "worktree list"
        "wt-add" = "worktree add"
        "wt-remove" = "worktree remove"
        "wt-prune" = "worktree prune"
        "wt-move" = "worktree move"
        "wt-lock" = "worktree lock"
        "wt-unlock" = "worktree unlock"
    }
    
    foreach ($alias in $aliases.GetEnumerator()) {
        git config --global "alias.$($alias.Key)" $alias.Value
        Write-Success "✓ Created alias: git $($alias.Key)"
    }
}

# Create PowerShell functions
function Setup-PowerShellFunctions {
    Write-Info "`n=== Creating PowerShell functions ==="
    
    $functionsFile = Join-Path $repoRoot "worktree-functions.ps1"
    
    # Write functions file directly
    $functionsContent = @'
# Git Worktree PowerShell Functions
# Source this file: . .\worktree-functions.ps1

function New-Worktree {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BranchName,
        
        [Parameter(Mandatory=$false)]
        [string]$BaseBranch = "main",
        
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $repoRoot = git rev-parse --show-toplevel
    $worktreePath = Join-Path $repoRoot $WorktreeDir $BranchName
    
    # Check if branch exists
    $branchExists = git branch --list $BranchName
    if (-not $branchExists) {
        Write-Host "Creating new branch: $BranchName from $BaseBranch" -ForegroundColor Cyan
        git checkout -b $BranchName $BaseBranch
        git checkout main
    }
    
    # Create worktree
    Write-Host "Creating worktree: $worktreePath" -ForegroundColor Cyan
    git worktree add $worktreePath $BranchName
    
    Write-Host "Worktree created successfully!" -ForegroundColor Green
    Write-Host "To switch to worktree: cd `"$worktreePath`"" -ForegroundColor Yellow
}

function Remove-Worktree {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BranchName,
        
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $repoRoot = git rev-parse --show-toplevel
    $worktreePath = Join-Path $repoRoot $WorktreeDir $BranchName
    
    if (-not (Test-Path $worktreePath)) {
        Write-Host "Worktree not found: $worktreePath" -ForegroundColor Red
        return
    }
    
    Write-Host "Removing worktree: $worktreePath" -ForegroundColor Yellow
    git worktree remove $worktreePath --force
    
    Write-Host "Worktree removed successfully!" -ForegroundColor Green
}

function Show-Worktrees {
    Write-Host "`n=== Current Worktrees ===" -ForegroundColor Cyan
    git worktree list
    Write-Host "`nCurrent worktree:" -ForegroundColor Cyan
    git rev-parse --show-toplevel
}

function Cleanup-Worktrees {
    param(
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $repoRoot = git rev-parse --show-toplevel
    $worktreeBase = Join-Path $repoRoot $WorktreeDir
    
    if (-not (Test-Path $worktreeBase)) {
        Write-Host "Worktrees directory not found: $worktreeBase" -ForegroundColor Red
        return
    }
    
    Write-Host "`n=== Cleaning up merged worktrees ===" -ForegroundColor Cyan
    
    $worktrees = Get-ChildItem $worktreeBase -Directory
    foreach ($wt in $worktrees) {
        $branch = git -C $wt.FullName rev-parse --abbrev-ref HEAD 2>$null
        if ($branch) {
            $merged = git branch --merged main | Select-String $branch
            if ($merged -and $branch -ne "main") {
                Write-Host "Removing merged worktree: $($wt.Name) ($branch)" -ForegroundColor Yellow
                git worktree remove $wt.FullName --force
                git branch -d $branch 2>$null
            }
        }
    }
    
    Write-Host "Cleanup complete!" -ForegroundColor Green
}
'@
    
    Set-Content -Path $functionsFile -Value $functionsContent
    Write-Success "✓ Created PowerShell functions file: $functionsFile"
    Write-Info "  Source with: . .\worktree-functions.ps1"
}

# Show current worktree status
function Show-Status {
    Write-Info "`n=== Current Worktree Status ==="
    git worktree list
    Write-Info "`nCurrent location: $(Get-Location)"
    Write-Info "Current branch: $(git rev-parse --abbrev-ref HEAD)"
}

# Cleanup old worktrees
function Cleanup-OldWorktrees {
    Write-Info "`n=== Cleaning up old worktrees ==="
    
    $worktrees = git worktree list --porcelain | Select-String "worktree" | ForEach-Object {
        $_.Line -replace "worktree ", ""
    }
    
    Write-Warning "Found $($worktrees.Count) worktrees"
    Write-Info "Review and remove manually if needed:"
    foreach ($wt in $worktrees) {
        Write-Info "  - $wt"
    }
}

# Main execution
if ($All -or $SetupConfig) {
    Setup-GitConfig
    Setup-WorktreeDirectory
}

if ($All -or $CreateAliases) {
    Setup-GitAliases
}

if ($All -or $CreateFunctions) {
    Setup-PowerShellFunctions
}

if ($Cleanup) {
    Cleanup-OldWorktrees
}

Show-Status

Write-Success "`n=== Setup Complete ==="
Write-Info "Next steps:"
Write-Info "  1. Source functions: . .\worktree-functions.ps1"
Write-Info "  2. Create new worktree: New-Worktree -BranchName 'feature-name'"
Write-Info "  3. List worktrees: Show-Worktrees"
Write-Info "  4. See WORKTREE_SETUP.md for detailed guide"

