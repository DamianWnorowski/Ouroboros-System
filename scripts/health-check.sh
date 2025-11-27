#!/bin/bash
# Quick health check script

python -m core.verification.cli --level 2 --quiet && \
python -c "from core.orchestrator import DynamicOrchestrator; print('✅ Orchestrator OK')" && \
python -c "from core.verification import OracleVerificationEngine; print('✅ Verification OK')" && \
python -c "from core.generators import AlphaGenerator; print('✅ Generator OK')" && \
python -c "from core.api import app; print('✅ API OK')" && \
echo "✅ All systems healthy"

