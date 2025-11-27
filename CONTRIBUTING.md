# Contributing to Ouroboros System

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/Ouroboros-System.git
   cd Ouroboros-System
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 📝 Development Workflow

### Using Worktrees (Recommended)

```powershell
# Load functions
. .\worktree-functions.ps1

# Create feature branch worktree
New-Worktree -BranchName "feature-my-feature"

# Work in worktree
cd worktrees\feature-my-feature
# ... make changes ...
git add .
git commit -m "Add my feature"
git push -u origin feature-my-feature
```

### Direct Branching

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "Add my feature"

# Push
git push -u origin feature/my-feature
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_orchestrator.py

# With coverage
pytest --cov=core --cov=agents
```

### Run Verification
```bash
# Full verification
python -m core.verification.cli

# Specific level
python -m core.verification.cli --level 3
```

## 📋 Code Standards

### Python Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused

### Pre-commit Hooks
The project uses pre-commit hooks for:
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Type checking (mypy)

### Commit Messages
Use clear, descriptive commit messages:
```
Add: New feature description
Fix: Bug description
Update: Change description
Refactor: Refactoring description
```

## 🏗️ Project Structure

```
Ouroboros-System/
├── core/              # Core systems
├── agents/            # Agent implementations
├── tests/             # Test suite
├── deployment/        # Deployment configs
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Integration tests
- [ ] Additional agents
- [ ] CI/CD improvements
- [ ] Documentation improvements

### Medium Priority
- [ ] Performance optimizations
- [ ] Additional generators
- [ ] Monitoring enhancements
- [ ] Example implementations

### Low Priority
- [ ] UI improvements
- [ ] Additional documentation
- [ ] Tutorial content

## 📚 Documentation

- Update relevant `.md` files
- Add docstrings to code
- Update examples if needed
- Keep `INDEX.md` updated

## 🔍 Before Submitting

1. **Run tests**
   ```bash
   pytest
   ```

2. **Run verification**
   ```bash
   python -m core.verification.cli
   ```

3. **Check formatting**
   ```bash
   black --check core agents tests
   isort --check-only core agents tests
   ```

4. **Update documentation** if needed

## 🐛 Reporting Issues

When reporting issues, please include:
- Description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

## 💡 Feature Requests

For feature requests:
- Describe the feature
- Explain the use case
- Provide examples if possible

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

*Thank you for contributing to Ouroboros System!*

