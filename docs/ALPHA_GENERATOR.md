# Alpha Generator - The Meta-Generator

## PHANTOM GENESIS: Alpha Generator
**System**: OmegaForge | **Codename**: Alpha

> "The generator that generates generators"

---

## Overview

The Alpha Generator is the apex predator of the generator ecosystem - a recursive self-bootstrapping system that can create new generators from Generator DNA specifications.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ALPHA GENERATOR                                │
├─────────────────────────────────────────────────────────────────────┤
│  Generator DNA  →  Template Synthesis  →  Code Generation          │
│       ↓                    ↓                    ↓                   │
│  [Spec YAML]  →  [Jinja2 Templates]  →  [.generator.py]            │
│       ↓                    ↓                    ↓                   │
│  Validation   →   Type Inference      →   Self-Registration        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Generator DNA Specification

### Structure

```yaml
id: my-generator              # kebab-case identifier
name: My Generator            # Human-readable name
system: MyForge               # System name (XxxForge pattern)
codename: Phoenix             # Single-word codename
description: Generates X      # Description
version: 1.0.0                # Semver version
category: infrastructure      # Category

outputs:                      # Output file specifications
  - path: "output/{provider.id}.py"
    template: main_template
    description: "Main output file"
    perTechnique: false

templates:                    # Template definitions
  - id: main_template
    content: |
      # Generated code for {{ provider.name }}
      def generate():
          pass
    description: "Main template"

configSchema:                 # Optional configuration schema
  type: object
  properties:
    outputDir:
      type: string
      default: "./generated"

dependencies: []              # Optional dependencies
helpers: []                   # Optional custom helpers
hooks: []                     # Optional hooks
```

---

## Usage

### Command Line

```bash
# Generate from DNA file
python -m core.generators.cli --dna generator-dna.yaml --output ./generated

# With custom namespace
python -m core.generators.cli --dna generator-dna.yaml --namespace myproject
```

### Python API

```python
from core.generators import AlphaGenerator, GeneratorContext

# Initialize Alpha Generator
alpha = AlphaGenerator()

# Load DNA
alpha.load_dna_from_file('generator-dna.yaml')

# Or load directly
from core.generators.alpha import GeneratorDNA, GeneratorOutputSpec, GeneratorTemplateSpec

dna = GeneratorDNA(
    id='my-generator',
    name='My Generator',
    system='MyForge',
    codename='Phoenix',
    description='Generates X',
    version='1.0.0',
    category='infrastructure',
    outputs=[
        GeneratorOutputSpec(
            path='output/{provider.id}.py',
            template='main_template',
        ),
    ],
    templates=[
        GeneratorTemplateSpec(
            id='main_template',
            content='# Generated: {{ provider.name }}',
        ),
    ],
)
alpha.load_generator_dna(dna)

# Generate
context = GeneratorContext(
    namespace='ouroboros',
    version='0.1.0',
)
files = await alpha.generate(context)

# Write files
for file in files:
    Path(file.path).parent.mkdir(parents=True, exist_ok=True)
    Path(file.path).write_text(file.content)
```

---

## Generated Output

The Alpha Generator produces:

1. **Generator Class** (`{id}_generator.py`)
   - Full Python generator implementation
   - Template registration
   - Helper registration
   - Generation logic

2. **Type Definitions** (`{id}_types.py`)
   - Type hints for generated code
   - Configuration types
   - Output types

3. **Test File** (`test_{id}_generator.py`)
   - Unit tests for the generator
   - Mock data
   - Test fixtures

4. **Documentation** (`docs/generators/{id}.md`)
   - README for the generator
   - Usage examples
   - Configuration guide

---

## Template Engine

Uses Jinja2 for templating with custom helpers:

- `{{ upper(text) }}` - Uppercase
- `{{ lower(text) }}` - Lowercase
- `{{ camel(text) }}` - camelCase
- `{{ pascal(text) }}` - PascalCase
- `{{ kebab(text) }}` - kebab-case
- `{{ snake(text) }}` - snake_case

### Custom Helpers

Define custom helpers in DNA:

```yaml
helpers:
  - name: format_code
    implementation: |
      def format_code(text):
          return text.strip().replace('\n', ' ')
    description: "Format code block"
```

---

## Example DNA File

```yaml
id: kubernetes-generator
name: Kubernetes Generator
system: K8sForge
codename: Helm
description: Generates Kubernetes manifests from provider specifications
version: 1.0.0
category: infrastructure

outputs:
  - path: "k8s/{provider.id}/deployment.yaml"
    template: deployment_template
    description: "Kubernetes deployment manifest"
  - path: "k8s/{provider.id}/service.yaml"
    template: service_template
    description: "Kubernetes service manifest"

templates:
  - id: deployment_template
    content: |
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: {{ provider.id }}
        namespace: {{ namespace }}
      spec:
        replicas: 1
        selector:
          matchLabels:
            app: {{ provider.id }}
        template:
          metadata:
            labels:
              app: {{ provider.id }}
          spec:
            containers:
            - name: {{ provider.id }}
              image: {{ provider.id }}:latest
  - id: service_template
    content: |
      apiVersion: v1
      kind: Service
      metadata:
        name: {{ provider.id }}
        namespace: {{ namespace }}
      spec:
        selector:
          app: {{ provider.id }}
        ports:
        - port: 80
          targetPort: 8080
```

---

## Integration

### With Ouroboros Orchestrator

```python
from core.orchestrator import DynamicOrchestrator
from core.generators import AlphaGenerator

async def setup_generators():
    alpha = AlphaGenerator()
    alpha.load_dna_from_file('generators/kubernetes-dna.yaml')
    
    context = GeneratorContext(
        providers=get_providers(),
        namespace='ouroboros',
    )
    
    files = await alpha.generate(context)
    # Process generated files
```

---

## Best Practices

1. **Start Simple**: Begin with basic DNA, then add complexity
2. **Reusable Templates**: Create templates that can be reused
3. **Type Safety**: Define proper config schemas
4. **Test Generated Code**: Always test generated generators
5. **Documentation**: Include descriptions in DNA

---

*Alpha Generator - Creating generators recursively, infinitely, maximally*

