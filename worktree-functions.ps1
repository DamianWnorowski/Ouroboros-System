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
    if (-not $repoRoot) {
        Write-Host "Not in a Git repository!" -ForegroundColor Red
        return
    }
    
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
    if (-not $repoRoot) {
        Write-Host "Not in a Git repository!" -ForegroundColor Red
        return
    }
    
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
    if (-not $repoRoot) {
        Write-Host "Not in a Git repository!" -ForegroundColor Red
        return
    }
    
    $worktreeBase = Join-Path $repoRoot $WorktreeDir
    
    if (-not (Test-Path $worktreeBase)) {
        Write-Host "Worktrees directory not found: $worktreeBase" -ForegroundColor Red
        return
    }
    
    Write-Host "`n=== Cleaning up merged worktrees ===" -ForegroundColor Cyan
    
    $worktrees = Get-ChildItem $worktreeBase -Directory -ErrorAction SilentlyContinue
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

# Functions are available after sourcing this file
# Usage: . .\worktree-functions.ps1

