# Git Worktree Best Practices Setup Guide

## Current Worktree Status

Your repository has the following worktrees configured:

```
Main Repository:  C:/Users/Ouroboros/Ouroboros-System (main)
Worktrees:
  - eqgEX:  analyze-eqgEX
  - FtRNp:  analyze-FtRNp (current)
  - lWDYE:  analyze-lWDYE
  - VQcHh:  analyze-data-VQcHh
```

---

## Optimal Worktree Structure

### Recommended Worktree Organization

```
Ouroboros-System/                    # Main repo (main branch)
├── worktrees/
│   ├── develop/                     # Development branch
│   ├── feature-*/                   # Feature branches
│   ├── hotfix-*/                    # Hotfix branches
│   ├── release-*/                   # Release branches
│   └── analyze-*/                   # Analysis/documentation branches
```

---

## Best Practices Configuration

### 1. **Worktree Directory Structure**

Create a dedicated directory for all worktrees:

```powershell
# From main repository
cd C:\Users\Ouroboros\Ouroboros-System
mkdir worktrees -ErrorAction SilentlyContinue
```

### 2. **Git Configuration for Worktrees**

Add these configurations to optimize worktree usage:

```powershell
# Enable worktree pruning (auto-cleanup)
git config worktree.pruneExpire "never"

# Set default worktree directory
git config worktree.defaultDirectory "worktrees"

# Enable worktree auto-prune on fetch
git config fetch.prune true
git config fetch.pruneTags true
```

### 3. **Aliases for Common Worktree Operations**

Add these Git aliases for easier worktree management:

```powershell
# Add to .gitconfig or run these commands:
git config --global alias.wt-list "worktree list"
git config --global alias.wt-add "worktree add"
git config --global alias.wt-remove "worktree remove"
git config --global alias.wt-prune "worktree prune"
git config --global alias.wt-move "worktree move"
```

---

## Worktree Management Scripts

### Create New Worktree

```powershell
# Function to create a new worktree with best practices
function New-Worktree {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BranchName,
        
        [Parameter(Mandatory=$false)]
        [string]$BaseBranch = "main",
        
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $worktreePath = Join-Path $WorktreeDir $BranchName
    
    # Check if branch exists
    $branchExists = git branch --list $BranchName
    if (-not $branchExists) {
        Write-Host "Creating new branch: $BranchName from $BaseBranch"
        git checkout -b $BranchName $BaseBranch
        git checkout main
    }
    
    # Create worktree
    Write-Host "Creating worktree: $worktreePath"
    git worktree add $worktreePath $BranchName
    
    Write-Host "Worktree created successfully!"
    Write-Host "To switch to worktree: cd $worktreePath"
}

# Usage:
# New-Worktree -BranchName "feature-new-component" -BaseBranch "main"
```

### Remove Worktree

```powershell
function Remove-Worktree {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BranchName,
        
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $worktreePath = Join-Path $WorktreeDir $BranchName
    
    Write-Host "Removing worktree: $worktreePath"
    git worktree remove $worktreePath --force
    
    Write-Host "Worktree removed successfully!"
}
```

### List All Worktrees

```powershell
function Show-Worktrees {
    git worktree list
    Write-Host "`nCurrent worktree:"
    git rev-parse --show-toplevel
}
```

---

## Recommended Worktree Workflow

### For Feature Development

```powershell
# 1. Create feature branch worktree
New-Worktree -BranchName "feature-orchestrator-enhancement" -BaseBranch "main"

# 2. Switch to worktree
cd worktrees\feature-orchestrator-enhancement

# 3. Make changes and commit
git add .
git commit -m "Add orchestrator enhancement"

# 4. Push to remote
git push -u origin feature-orchestrator-enhancement

# 5. When done, remove worktree
cd ..\..
Remove-Worktree -BranchName "feature-orchestrator-enhancement"
```

### For Analysis/Documentation

```powershell
# 1. Create analysis branch
New-Worktree -BranchName "analyze-deployment-script" -BaseBranch "main"

# 2. Work on analysis
cd worktrees\analyze-deployment-script
# ... make changes ...

# 3. Commit and push
git add .
git commit -m "Add deployment script analysis"
git push -u origin analyze-deployment-script

# 4. Keep worktree for reference or remove when done
```

### For Hotfixes

```powershell
# 1. Create hotfix from main
New-Worktree -BranchName "hotfix-security-patch" -BaseBranch "main"

# 2. Fix issue
cd worktrees\hotfix-security-patch
# ... apply fix ...

# 3. Merge to main and remove
git checkout main
git merge hotfix-security-patch
git push origin main
Remove-Worktree -BranchName "hotfix-security-patch"
```

---

## Worktree Cleanup Script

```powershell
# Cleanup merged worktrees
function Cleanup-Worktrees {
    param(
        [Parameter(Mandatory=$false)]
        [string]$WorktreeDir = "worktrees"
    )
    
    $worktrees = git worktree list --porcelain | Select-String "worktree" | ForEach-Object {
        $_.Line -replace "worktree ", ""
    }
    
    foreach ($wt in $worktrees) {
        if ($wt -like "*$WorktreeDir*") {
            $branchName = Split-Path $wt -Leaf
            $branch = git -C $wt rev-parse --abbrev-ref HEAD
            
            # Check if branch is merged
            $merged = git branch --merged main | Select-String $branch
            if ($merged) {
                Write-Host "Removing merged worktree: $branchName"
                git worktree remove $wt --force
                
                # Delete branch if it's not main
                if ($branch -ne "main") {
                    git branch -d $branch
                }
            }
        }
    }
}
```

---

## Integration with Cursor IDE

### Cursor Worktree Configuration

Cursor automatically detects worktrees. To optimize:

1. **Open Worktree in New Window**
   - File → Open Folder → Select worktree directory
   - Cursor will recognize it as part of the same repo

2. **Worktree-Specific Settings**
   - Each worktree can have its own `.vscode/settings.json`
   - Useful for branch-specific configurations

3. **Recommended Cursor Settings**

Create `.cursor/settings.json` in each worktree:

```json
{
  "git.autoRepositoryDetection": true,
  "git.detectSubmodules": true,
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "files.exclude": {
    "**/.git": false
  }
}
```

---

## Performance Optimization

### 1. **Sparse Checkout** (for large repos)

```powershell
# Enable sparse checkout in worktree
cd worktrees\feature-name
git sparse-checkout init --cone
git sparse-checkout set core/ agents/  # Only checkout specific directories
```

### 2. **Shallow Clones** (if needed)

```powershell
# Create worktree with limited history
git worktree add --detach worktrees\shallow-work ../main
git -C worktrees\shallow-work fetch --depth=1
```

---

## Troubleshooting

### Common Issues

#### 1. **Worktree locked**
```powershell
# Remove lock file
Remove-Item .git\worktrees\<worktree-name>\locked
```

#### 2. **Worktree path changed**
```powershell
# Move worktree to new location
git worktree move <old-path> <new-path>
```

#### 3. **Cleanup orphaned worktrees**
```powershell
# Prune worktrees
git worktree prune
```

---

## Quick Reference Commands

```powershell
# List all worktrees
git worktree list

# Add new worktree
git worktree add <path> <branch>

# Remove worktree
git worktree remove <path>

# Move worktree
git worktree move <old-path> <new-path>

# Prune worktrees
git worktree prune

# Lock worktree (prevent deletion)
git worktree lock <path>

# Unlock worktree
git worktree unlock <path>
```

---

## Current Worktree Recommendations

Based on your current setup:

1. **Keep analysis worktrees** until analysis is complete
2. **Create feature worktrees** for new development
3. **Use main repo** for quick fixes and merges
4. **Clean up merged branches** regularly

### Suggested Cleanup

```powershell
# Review current worktrees
git worktree list

# Remove completed analysis worktrees (if done)
# git worktree remove worktrees/analyze-eqgEX
# git worktree remove worktrees/analyze-lWDYE
```

---

## Next Steps

1. ✅ Review current worktree setup
2. ✅ Create `worktrees/` directory structure
3. ✅ Add Git aliases for worktree management
4. ✅ Set up PowerShell functions for worktree operations
5. ✅ Configure Cursor IDE settings
6. ✅ Clean up old/merged worktrees

---

*Last Updated: $(Get-Date)*

