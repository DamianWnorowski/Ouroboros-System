"""
Unit tests for Oracle Verification Engine
"""

import pytest
import tempfile
import os
from pathlib import Path
from core.verification.oracle import OracleVerificationEngine, VerificationLevel


@pytest.mark.asyncio
async def test_oracle_initialization():
    """Test Oracle engine can be initialized"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = OracleVerificationEngine(tmpdir)
        assert engine is not None
        assert engine.base_path == Path(tmpdir)


@pytest.mark.asyncio
async def test_verify_existence():
    """Test L0 existence verification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / 'test.py'
        test_file.write_text('# test file')
        
        engine = OracleVerificationEngine(tmpdir)
        await engine._verify_existence()
        
        assert len(engine.results) > 0
        # Should have at least one result
        assert any(r.level == VerificationLevel.EXISTENCE for r in engine.results)


@pytest.mark.asyncio
async def test_verify_syntax():
    """Test L1 syntax verification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create valid Python file
        valid_file = Path(tmpdir) / 'valid.py'
        valid_file.write_text('def test(): pass\n')
        
        # Create invalid Python file
        invalid_file = Path(tmpdir) / 'invalid.py'
        invalid_file.write_text('def test(:\n')  # Syntax error
        
        engine = OracleVerificationEngine(tmpdir)
        await engine._verify_syntax()
        
        results = engine.results
        assert len(results) > 0
        # Should have both pass and fail results
        assert any(r.status == 'pass' for r in results)
        assert any(r.status == 'fail' for r in results)


@pytest.mark.asyncio
async def test_generate_report():
    """Test report generation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = OracleVerificationEngine(tmpdir)
        await engine.verify_all(max_level=2)
        
        report = engine.generate_report()
        assert 'ORACLE VERIFICATION REPORT' in report
        assert 'Total:' in report


@pytest.mark.asyncio
async def test_export_json():
    """Test JSON export"""
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = OracleVerificationEngine(tmpdir)
        await engine.verify_all(max_level=1)
        
        json_output = engine.export_json()
        assert 'results' in json_output
        assert 'statistics' in json_output
        
        # Test file export
        json_file = Path(tmpdir) / 'results.json'
        engine.export_json(str(json_file))
        assert json_file.exists()

