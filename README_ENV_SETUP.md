# Environment Setup Guide

## Creating .env File

Since `.env.example` cannot be committed (security), here's how to create your `.env` file:

### Option 1: Manual Creation
```bash
# Create .env file
cat > .env << 'EOF'
# Copy the template below and fill in your values
EOF
```

### Option 2: From Documentation
See `README.md` or `QUICK_START_GUIDE.md` for environment variable references.

### Required Variables

```bash
# Minimum required
CONSUL_HOST=localhost
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password
REDIS_HOST=localhost
NEO4J_HOST=localhost
NEO4J_PASSWORD=your_password
JWT_SECRET=your_jwt_secret_min_32_chars
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Optional Variables

```bash
# External APIs
VIRUSTOTAL_API_KEY=
OTX_API_KEY=
SHODAN_API_KEY=

# GCP (if using)
GCP_PROJECT_ID=
GCP_REGION=us-central1
```

### Security Note

**Never commit `.env` files!** They are in `.gitignore` for security.

---

*Environment Setup - Secure configuration management*

