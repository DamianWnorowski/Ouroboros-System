"""
Base Generator Class
All generators inherit from this
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path


@dataclass
class GeneratedFile:
    """Represents a generated file"""
    path: str
    content: str
    description: Optional[str] = None
    hash: Optional[str] = None


@dataclass
class GeneratorContext:
    """Context for generator execution"""
    providers: List[Dict[str, Any]] = field(default_factory=list)
    namespace: str = "ouroboros"
    version: str = "0.1.0"
    environment: str = "development"
    output_dir: str = "./generated"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    config: Dict[str, Any] = field(default_factory=dict)


class BaseGenerator(ABC):
    """Base class for all generators"""
    
    def __init__(self, generator_id: str, name: str, description: str = ""):
        self.generator_id = generator_id
        self.name = name
        self.description = description
        self.generated_files: List[GeneratedFile] = []
    
    @abstractmethod
    async def generate(self, context: GeneratorContext) -> List[GeneratedFile]:
        """Generate files based on context"""
        pass
    
    def resolve_path(self, template: str, **kwargs) -> str:
        """Resolve path template with placeholders"""
        path = template
        for key, value in kwargs.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    path = path.replace(f"{{{key}.{sub_key}}}", str(sub_value))
            else:
                path = path.replace(f"{{{key}}}", str(value))
        return path
    
    def to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase"""
        return ''.join(word.capitalize() for word in text.replace('-', '_').split('_'))
    
    def to_camel_case(self, text: str) -> str:
        """Convert text to camelCase"""
        pascal = self.to_pascal_case(text)
        return pascal[0].lower() + pascal[1:] if pascal else ""
    
    def to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

