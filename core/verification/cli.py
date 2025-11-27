"""
CLI interface for Oracle Verification Engine
"""

import asyncio
import argparse
import sys
from pathlib import Path
from .oracle import OracleVerificationEngine, VerificationLevel


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Oracle Verification Engine - Recursive Verification System'
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Base path to verify (default: current directory)'
    )
    parser.add_argument(
        '--level',
        type=int,
        default=6,
        choices=[0, 1, 2, 3, 4, 5, 6],
        help='Maximum verification level (0-6, default: 6)'
    )
    parser.add_argument(
        '--json',
        type=str,
        help='Export results to JSON file'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output (only show report)'
    )
    
    args = parser.parse_args()
    
    base_path = Path(args.path).resolve()
    
    if not base_path.exists():
        print(f"Error: Path does not exist: {base_path}")
        sys.exit(1)
    
    engine = OracleVerificationEngine(str(base_path))
    results = await engine.verify_all(max_level=args.level)
    
    if not args.quiet:
        print(engine.generate_report())
    
    if args.json:
        await engine.export_json(args.json)
        print(f"\nResults exported to: {args.json}")
    
    # Exit with error code if any failures
    failed = len([r for r in results if r.status == 'fail'])
    if failed > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())

