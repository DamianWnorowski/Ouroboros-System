"""
Example: Using Oracle Verification Engine

This example demonstrates how to use the Oracle verification system.
"""

import asyncio
from core.verification import OracleVerificationEngine


async def main():
    """Example verification usage"""
    
    # Initialize verification engine
    engine = OracleVerificationEngine(".")
    
    # Run full verification (all levels)
    print("Running full verification...")
    results = await engine.verify_all(max_level=6)
    
    # Generate and print report
    report = engine.generate_report()
    print(report)
    
    # Export to JSON
    json_output = engine.export_json("verification-results.json")
    print("\nResults exported to verification-results.json")
    
    # Check specific levels
    print("\n=== Level Breakdown ===")
    for level in range(7):
        level_results = [r for r in results if r.level == level]
        if level_results:
            passed = len([r for r in level_results if r.status == 'pass'])
            total = len(level_results)
            print(f"L{level}: {passed}/{total} passed")


if __name__ == "__main__":
    asyncio.run(main())

