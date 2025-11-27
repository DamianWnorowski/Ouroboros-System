"""
Template Engine - Handlebars-like templating for code generation
"""

import re
from typing import Dict, Any, Callable, Optional
from jinja2 import Environment, BaseLoader, Template


class TemplateEngine:
    """Template engine for code generation"""
    
    def __init__(self):
        self.env = Environment(
            loader=BaseLoader(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.templates: Dict[str, Template] = {}
        self.helpers: Dict[str, Callable] = {}
        self._register_default_helpers()
    
    def _register_default_helpers(self):
        """Register default template helpers"""
        self.register_helper('upper', str.upper)
        self.register_helper('lower', str.lower)
        self.register_helper('camel', self._to_camel_case)
        self.register_helper('pascal', self._to_pascal_case)
        self.register_helper('kebab', self._to_kebab_case)
        self.register_helper('snake', self._to_snake_case)
    
    def _to_camel_case(self, text: str) -> str:
        """Convert to camelCase"""
        components = text.replace('-', '_').split('_')
        return components[0].lower() + ''.join(x.capitalize() for x in components[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert to PascalCase"""
        components = text.replace('-', '_').split('_')
        return ''.join(x.capitalize() for x in components)
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert to kebab-case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    
    def _to_snake_case(self, text: str) -> str:
        """Convert to snake_case"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def compile(self, template_id: str, content: str):
        """Compile a template"""
        self.templates[template_id] = self.env.from_string(content)
    
    def register_helper(self, name: str, func: Callable):
        """Register a custom helper function"""
        self.helpers[name] = func
        self.env.globals[name] = func
    
    def render(self, template_id: str, context: Dict[str, Any]) -> str:
        """Render a template with context"""
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found")
        
        template = self.templates[template_id]
        return template.render(**context)
    
    def render_string(self, content: str, context: Dict[str, Any]) -> str:
        """Render a template string directly"""
        template = self.env.from_string(content)
        return template.render(**context)

