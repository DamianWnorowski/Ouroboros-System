"""
Example: Using Alpha Generator

This example shows how to use the Alpha meta-generator to create new generators.
"""

import asyncio
from pathlib import Path
from core.generators import AlphaGenerator, GeneratorContext
from core.generators.alpha import GeneratorDNA, GeneratorOutputSpec, GeneratorTemplateSpec


async def main():
    """Example generator usage"""
    
    # Initialize Alpha Generator
    alpha = AlphaGenerator()
    
    # Option 1: Load from YAML file
    print("Loading DNA from file...")
    alpha.load_dna_from_file("examples/generator-dna-example.yaml")
    
    # Option 2: Create DNA programmatically
    dna = GeneratorDNA(
        id="my-custom-generator",
        name="My Custom Generator",
        system="CustomForge",
        codename="Spark",
        description="A custom generator example",
        version="1.0.0",
        category="infrastructure",
        outputs=[
            GeneratorOutputSpec(
                path="output/{provider.id}.py",
                template="main_template",
                description="Main output file",
            ),
        ],
        templates=[
            GeneratorTemplateSpec(
                id="main_template",
                content="# Generated: {{ provider.name }}\ndef main():\n    pass",
                description="Main template",
            ),
        ],
    )
    
    # Load DNA
    alpha.load_generator_dna(dna)
    
    # Create context
    context = GeneratorContext(
        providers=[
            {
                "id": "example-provider",
                "name": "Example Provider",
                "version": "1.0.0",
            }
        ],
        namespace="example",
        version="0.1.0",
    )
    
    # Generate
    print("Generating code...")
    files = await alpha.generate(context)
    
    # Write files
    output_dir = Path("generated")
    output_dir.mkdir(exist_ok=True)
    
    for file in files:
        file_path = output_dir / file.path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(file.content, encoding="utf-8")
        print(f"Generated: {file_path}")
    
    print(f"\n✅ Generated {len(files)} files")


if __name__ == "__main__":
    asyncio.run(main())

