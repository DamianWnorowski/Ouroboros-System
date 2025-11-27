# Worktree Quick Start Guide

## ✅ Setup Complete!

Your worktree configuration is now ready. Here's what was set up:

### Configuration Applied
- ✅ Git worktree settings configured
- ✅ `worktrees/` directory created
- ✅ Git aliases added (wt-list, wt-add, wt-remove, wt-prune)
- ✅ PowerShell functions available

### Current Worktrees
```
Main:     C:/Users/Ouroboros/Ouroboros-System (main)
Worktrees:
  - eqgEX:  analyze-eqgEX
  - FtRNp:  analyze-FtRNp (current)
  - lWDYE:  analyze-lWDYE
  - VQcHh:  analyze-data-VQcHh
```

---

## Quick Commands

### Load Functions
```powershell
# From main repository
. .\worktree-functions.ps1
```

### Create New Worktree
```powershell
New-Worktree -BranchName "feature-name" -BaseBranch "main"
```

### List All Worktrees
```powershell
Show-Worktrees
# or
git wt-list
```

### Remove Worktree
```powershell
Remove-Worktree -BranchName "feature-name"
```

### Cleanup Merged Worktrees
```powershell
Cleanup-Worktrees
```

---

## Git Aliases Available

```powershell
git wt-list      # List all worktrees
git wt-add       # Add new worktree
git wt-remove    # Remove worktree
git wt-prune     # Prune worktrees
```

---

## Example Workflow

### 1. Create Feature Branch Worktree
```powershell
cd C:\Users\Ouroboros\Ouroboros-System
. .\worktree-functions.ps1
New-Worktree -BranchName "feature-orchestrator" -BaseBranch "main"
cd worktrees\feature-orchestrator
# ... make changes ...
git add .
git commit -m "Add orchestrator feature"
git push -u origin feature-orchestrator
```

### 2. Switch Between Worktrees
```powershell
# Work on main
cd C:\Users\Ouroboros\Ouroboros-System

# Work on feature
cd C:\Users\Ouroboros\Ouroboros-System\worktrees\feature-orchestrator
```

### 3. Clean Up When Done
```powershell
cd C:\Users\Ouroboros\Ouroboros-System
Remove-Worktree -BranchName "feature-orchestrator"
```

---

## Directory Structure

```
Ouroboros-System/
├── worktrees/              # All worktrees go here
│   ├── feature-*/         # Feature branches
│   ├── analyze-*/          # Analysis/documentation
│   └── hotfix-*/           # Hotfix branches
├── worktree-functions.ps1   # PowerShell functions
├── setup-worktree.ps1      # Setup script
└── WORKTREE_SETUP.md       # Full documentation
```

---

## Tips

1. **Always create worktrees in `worktrees/` directory** for organization
2. **Use descriptive branch names** that match the worktree folder
3. **Clean up merged branches** regularly with `Cleanup-Worktrees`
4. **Each worktree is independent** - you can work on multiple features simultaneously

---

## Need Help?

- Full documentation: `WORKTREE_SETUP.md`
- Git worktree docs: `git help worktree`
- Current status: `Show-Worktrees`

---

*Setup completed successfully!*

