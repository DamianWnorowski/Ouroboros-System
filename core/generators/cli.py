"""
CLI interface for Alpha Generator
"""

import asyncio
import argparse
import sys
from pathlib import Path
from .alpha import AlphaGenerator, GeneratorDNA
from .base import GeneratorContext


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Alpha Generator - The meta-generator that creates generators'
    )
    parser.add_argument(
        '--dna',
        type=str,
        required=True,
        help='Path to Generator DNA file (YAML or JSON)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./generated',
        help='Output directory (default: ./generated)'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        default='ouroboros',
        help='Namespace for generated code (default: ouroboros)'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='0.1.0',
        help='Generator version (default: 0.1.0)'
    )
    
    args = parser.parse_args()
    
    # Initialize Alpha Generator
    alpha = AlphaGenerator()
    
    # Load DNA (async)
    try:
        dna_data = await alpha.load_dna_from_file(args.dna)
        # Convert to GeneratorDNA if needed
        from .alpha import GeneratorDNA
        if isinstance(dna_data, dict):
            dna = GeneratorDNA(**dna_data)
            alpha.load_generator_dna(dna)
        elif isinstance(dna_data, list):
            alpha.load_generator_dna([GeneratorDNA(**d) for d in dna_data])
        else:
            alpha.load_generator_dna(dna_data)
    except Exception as e:
        print(f"Error loading DNA file: {e}")
        sys.exit(1)
    
    # Create context
    context = GeneratorContext(
        namespace=args.namespace,
        version=args.version,
        output_dir=args.output,
    )
    
    # Generate
    try:
        files = await alpha.generate(context)
        
        # Write files
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            file_path = output_path / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file.content, encoding='utf-8')
            print(f"Generated: {file_path}")
        
        print(f"\n✅ Generated {len(files)} files")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

