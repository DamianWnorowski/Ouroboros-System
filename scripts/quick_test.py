#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import DynamicOrchestrator

async def quick_test():
    print('QUICK ELITE SYSTEM TEST')
    print('=' * 30)

    try:
        orchestrator = DynamicOrchestrator()
        await orchestrator.start()
        print('[OK] Orchestrator started')

        fitness = await orchestrator.assess_system_fitness()
        print('.3f')
        print(f'DEFCON: {fitness["defcon_level"]}')

        await orchestrator.stop()
        print('[OK] System test completed successfully')
        return True

    except Exception as e:
        print(f'[ERROR] Test failed: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    sys.exit(0 if result else 1)
