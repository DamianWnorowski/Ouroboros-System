# API Key Security Guide

## Overview

This guide covers best practices for finding, managing, and securing API keys in the Ouroboros System.

---

## 🔍 Finding Lost API Keys

### Quick Search (Common Locations)

```bash
python scripts/find_api_keys.py --common
```

Searches:
- `~/.ssh/`
- `~/.config/`
- `~/.secrets/`
- `~/Documents/`
- `~/Desktop/`
- `~/Downloads/`
- `.env` files

### Full System Search

```bash
python scripts/find_api_keys.py --all-drives
```

**Warning**: This can take a long time and may scan system files. Use with caution.

### Project-Only Search

```bash
python scripts/find_api_keys.py --project
```

### Validate Results

After running the finder, validate the results:

```bash
python scripts/validate_api_keys.py --report api_keys_report.md
```

This will:
- Filter out false positives
- Categorize keys by priority (CRITICAL, HIGH, MEDIUM, LOW)
- Generate a prioritized report

---

## 🔒 Security Best Practices

### 1. Never Commit Keys to Git

**DO:**
- Use `.env` files (in `.gitignore`)
- Use environment variables
- Use secret managers (AWS Secrets Manager, HashiCorp Vault, etc.)

**DON'T:**
- Hardcode keys in source code
- Commit `.env` files
- Share keys in chat/email
- Store keys in documentation

### 2. Use Environment Variables

```python
import os

# Good
api_key = os.getenv("OPENAI_API_KEY")

# Bad
api_key = "sk-1234567890abcdef..."
```

### 3. Use Secret Managers

**AWS Secrets Manager:**
```python
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='my-api-key')
api_key = response['SecretString']
```

**HashiCorp Vault:**
```python
import hvac

client = hvac.Client(url='https://vault.example.com')
secret = client.secrets.kv.v2.read_secret_version(path='api-keys')
api_key = secret['data']['data']['openai_key']
```

### 4. Rotate Keys Regularly

- Rotate keys every 90 days (or per your security policy)
- Rotate immediately if exposed
- Use key versioning when possible

### 5. Use Different Keys for Different Environments

- Development: `OPENAI_API_KEY_DEV`
- Staging: `OPENAI_API_KEY_STAGING`
- Production: `OPENAI_API_KEY_PROD`

---

## 🚨 If You Find Exposed Keys

### Immediate Actions

1. **Rotate the key immediately**
   - Generate a new key
   - Update all systems using the old key
   - Revoke the old key

2. **Check for unauthorized access**
   - Review API usage logs
   - Check for unusual activity
   - Monitor for suspicious requests

3. **Remove from codebase**
   - Search for all occurrences
   - Remove from all files
   - Clean Git history if needed:
     ```bash
     git filter-branch --force --index-filter \
       "git rm --cached --ignore-unmatch path/to/file" \
       --prune-empty --tag-name-filter cat -- --all
     ```

4. **Notify your team**
   - Inform security team
   - Update incident log
   - Review access controls

---

## 📋 Key Types and Priorities

### CRITICAL Priority (Rotate Immediately)

- **AWS Access Keys**: Full cloud access
- **Stripe Live Keys**: Payment processing
- **Database Credentials**: Data access
- **SSH Private Keys**: Server access

### HIGH Priority (Review and Rotate)

- **OpenAI API Keys**: AI service access
- **GitHub Tokens**: Code repository access
- **Google API Keys**: Cloud service access
- **OAuth Tokens**: Authentication

### MEDIUM Priority (Verify Manually)

- **Test Keys**: Limited scope
- **Development Keys**: Non-production
- **Public Keys**: Read-only access

### LOW Priority (Likely Safe)

- **Hashes**: SHA256, MD5 (not keys)
- **UUIDs**: Identifiers (not keys)
- **Placeholders**: Example values

---

## 🛠️ Tools

### API Key Finder

```bash
# Quick search
python scripts/find_api_keys.py --common

# Full search
python scripts/find_api_keys.py --all-drives

# Project only
python scripts/find_api_keys.py --project
```

### API Key Validator

```bash
# Validate results
python scripts/validate_api_keys.py --report api_keys_report.md
```

### Git Secrets Scanner

```bash
# Install git-secrets
git secrets --install

# Scan repository
git secrets --scan
```

---

## 📝 Checklist

Before committing code:

- [ ] No API keys in source code
- [ ] `.env` files in `.gitignore`
- [ ] Environment variables used
- [ ] Secrets in secret manager
- [ ] Keys rotated regularly
- [ ] Different keys per environment
- [ ] Access logs monitored

---

## 🔗 Resources

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [HashiCorp Vault](https://www.vaultproject.io/)

---

*Last Updated: December 2024*

