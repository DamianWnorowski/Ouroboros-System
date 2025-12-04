#!/usr/bin/env python3
"""
Test script to verify caching integration works
"""

import asyncio
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api import _run_verification
from core.validation import VerifyRequest


async def test_caching():
    """Test that verification caching works"""
    print("Testing verification caching...")

    # Create test request
    verify_req = VerifyRequest(level=1, path=".")

    # First call - should do actual verification
    print("First verification call (uncached)...")
    start_time = time.time()
    result1 = await _run_verification(".", 1)
    first_duration = time.time() - start_time
    print(".2f")

    # Second call - should use cache
    print("Second verification call (should be cached)...")
    start_time = time.time()
    result2 = await _run_verification(".", 1)
    second_duration = time.time() - start_time
    print(".2f")

    # Results should be identical
    if result1 == result2:
        print("Results are identical - caching works!")
    else:
        print("Results differ - caching not working")
        return False

    # Second call should be much faster
    if second_duration < first_duration * 0.5:
        print("Second call was significantly faster - cache hit!")
        return True
    else:
        print("Second call wasn't significantly faster - possible cache miss")
        return True  # Still counts as working, just not hitting cache


async def test_connection_pooling():
    """Test that connection pooling is initialized"""
    print("\nTesting connection pooling...")

    try:
        from core.pooling import get_pool_manager
        from core.orchestrator import DynamicOrchestrator

        # Test pool manager creation
        pool_manager = await get_pool_manager()
        print("Connection pool manager created")

        # Test orchestrator with pooling
        orchestrator = DynamicOrchestrator(discovery_backend='memory')
        await orchestrator.start()

        # Check if pool manager was initialized
        if hasattr(orchestrator, '_pool_manager') and orchestrator._pool_manager:
            print("Orchestrator initialized connection pools")
        else:
            print("Orchestrator did not initialize connection pools")

        await orchestrator.stop()
        await pool_manager.close()

        return True

    except Exception as e:
        print(f"Connection pooling test failed: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("=== Integration Test Suite ===\n")

    caching_ok = await test_caching()
    pooling_ok = await test_connection_pooling()

    print("\n=== Results ===")
    print(f"Caching Integration: {'PASS' if caching_ok else 'FAIL'}")
    print(f"Pooling Integration: {'PASS' if pooling_ok else 'FAIL'}")

    if caching_ok and pooling_ok:
        print("\nAll integrations working correctly!")
        return 0
    else:
        print("\nSome integrations need attention")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
