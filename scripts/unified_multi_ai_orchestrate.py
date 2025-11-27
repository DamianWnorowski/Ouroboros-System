#!/usr/bin/env python3
"""
Unified Multi-AI Orchestration Tool
Intelligently orchestrates multiple AIs using the best available method

AUTO MODE (default):
  - If OpenAI API configured: Runs TRUE API-integrated orchestration (fully automated)
  - If NO API: Generates prompt templates for manual copy-paste

Usage:
    python unified_multi_ai_orchestrate.py [--mode auto|api|prompts] [--cycles N] [--check] [--setup]
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Check for OpenAI API
HAS_OPENAI = False
try:
    import openai
    if os.getenv("OPENAI_API_KEY"):
        HAS_OPENAI = True
        openai.api_key = os.getenv("OPENAI_API_KEY")
except ImportError:
    pass

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
AUDIT_DIR = PROJECT_ROOT


class UnifiedMultiAIOrchestrator:
    """Unified orchestrator that adapts to available capabilities"""
    
    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.has_api = HAS_OPENAI and mode != "prompts"
        self.project_root = PROJECT_ROOT
        self.results: List[Dict[str, Any]] = []
        
    def check_capabilities(self) -> Dict[str, bool]:
        """Check what capabilities are available"""
        return {
            "openai_api": HAS_OPENAI,
            "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
            "project_root_exists": self.project_root.exists(),
            "docs_dir_exists": DOCS_DIR.exists(),
        }
    
    def generate_analysis_prompt(self) -> str:
        """Generate comprehensive analysis prompt for manual use"""
        prompt = f"""# OUROBOROS SYSTEM - MULTI-AI ANALYSIS REQUEST

## Context
You are analyzing the Ouroboros System, an autonomous self-healing multi-agent AI system.

## Project Location
{self.project_root}

## Current Status
- Overall Score: 85/100
- Security: 75/100
- Performance: 80/100
- Reliability: 90/100
- Status: Production Ready

## Recent Improvements
- Phase 1: Critical Security Fixes (100% Complete)
- Phase 2: Performance & Reliability (100% Complete)
- All critical issues fixed (8/8)
- All high priority issues fixed (4/4)

## Your Task

Please analyze the Ouroboros System from your specialized perspective and provide:

1. **Deep Analysis**: Identify any remaining issues, optimizations, or improvements
2. **Specific Recommendations**: Actionable items with priority levels
3. **Code Examples**: If applicable, provide code snippets for fixes
4. **Risk Assessment**: Identify any potential risks or concerns
5. **Next Steps**: Prioritized roadmap for further improvements

## Analysis Areas

### Security Specialist
- Authentication mechanisms
- Authorization and access control
- Input validation and sanitization
- Secret management
- Security headers and CORS
- Vulnerability assessment

### Performance Engineer
- Algorithm complexity
- Database query optimization
- Caching strategies
- Connection pooling usage
- Async/await patterns
- Resource utilization

### Reliability Expert
- Error handling patterns
- Retry mechanisms
- Circuit breakers
- Health checks
- Monitoring and alerting
- Disaster recovery

### Scalability Architect
- Horizontal scaling readiness
- Database sharding strategies
- Load balancing
- Microservices architecture
- Distributed systems patterns

### Code Quality Expert
- Code organization
- Type hints and documentation
- Test coverage
- Linting and formatting
- Dependency management

## Output Format

Please provide your analysis in the following format:

```markdown
# [Your Role] Analysis - Ouroboros System

## Executive Summary
[Brief overview of findings]

## Critical Issues (P0)
1. [Issue] - [Description] - [Impact] - [Recommendation]

## High Priority (P1)
1. [Issue] - [Description] - [Impact] - [Recommendation]

## Medium Priority (P2)
1. [Issue] - [Description] - [Impact] - [Recommendation]

## Code Examples
[If applicable]

## Risk Assessment
[Potential risks and mitigation strategies]

## Next Steps
[Prioritized action items]
```

## Files to Review

Key files to examine:
- `core/orchestrator.py` - Main orchestrator
- `core/api.py` - REST API
- `core/auth.py` - Authentication
- `core/verification/oracle.py` - Verification engine
- `core/generators/alpha.py` - Meta-generator
- `core/pooling.py` - Connection pooling
- `core/cache.py` - Caching layer
- `requirements.txt` - Dependencies
- `AUDIT_REPORT.md` - Previous audit
- `ULTRA_CRITIC_REPORT.md` - Previous critic report

## Notes
- System is production-ready (85/100)
- All critical security issues have been addressed
- Performance optimizations have been implemented
- Focus on identifying remaining opportunities for improvement

Thank you for your analysis!
"""
        return prompt
    
    def run_api_orchestration(self, cycles: int = 1) -> List[Dict[str, Any]]:
        """Run true API-integrated orchestration"""
        if not self.has_api:
            raise RuntimeError("OpenAI API not configured. Use --mode prompts for prompt generation.")
        
        results = []
        
        # Define AI roles
        roles = [
            {
                "name": "Security Specialist",
                "focus": "Security vulnerabilities, authentication, authorization, input validation",
                "model": "gpt-4"
            },
            {
                "name": "Performance Engineer",
                "focus": "Performance bottlenecks, algorithm optimization, caching, async patterns",
                "model": "gpt-4"
            },
            {
                "name": "Reliability Expert",
                "focus": "Error handling, resilience, monitoring, disaster recovery",
                "model": "gpt-4"
            },
            {
                "name": "Scalability Architect",
                "focus": "Horizontal scaling, load balancing, distributed systems",
                "model": "gpt-4"
            },
            {
                "name": "Code Quality Expert",
                "focus": "Code organization, type hints, test coverage, best practices",
                "model": "gpt-4"
            }
        ]
        
        # Read key files for context
        context_files = [
            "core/orchestrator.py",
            "core/api.py",
            "core/auth.py",
            "AUDIT_REPORT.md",
            "FINAL_IMPROVEMENTS_SUMMARY.md"
        ]
        
        context = self._load_context(context_files)
        
        for cycle in range(cycles):
            print(f"\n🔄 Cycle {cycle + 1}/{cycles}")
            
            for role in roles:
                print(f"  🤖 Consulting {role['name']}...")
                
                try:
                    response = openai.ChatCompletion.create(
                        model=role["model"],
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are a {role['name']} analyzing the Ouroboros System. Focus on: {role['focus']}"
                            },
                            {
                                "role": "user",
                                "content": self.generate_analysis_prompt() + f"\n\nContext:\n{context}"
                            }
                        ],
                        temperature=0.7,
                        max_tokens=2000
                    )
                    
                    analysis = response.choices[0].message.content
                    
                    result = {
                        "cycle": cycle + 1,
                        "role": role["name"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "analysis": analysis
                    }
                    
                    results.append(result)
                    
                    # Save individual result
                    output_file = AUDIT_DIR / f"ai_analysis_{role['name'].lower().replace(' ', '_')}_cycle{cycle+1}.md"
                    output_file.write_text(analysis, encoding="utf-8")
                    print(f"    ✅ Saved to {output_file.name}")
                    
                except Exception as e:
                    print(f"    ❌ Error: {e}")
                    results.append({
                        "cycle": cycle + 1,
                        "role": role["name"],
                        "error": str(e)
                    })
        
        # Generate unified report
        self._generate_unified_report(results)
        
        return results
    
    def generate_prompts(self) -> Dict[str, str]:
        """Generate prompt templates for manual use"""
        prompts = {}
        
        roles = [
            "Security Specialist",
            "Performance Engineer",
            "Reliability Expert",
            "Scalability Architect",
            "Code Quality Expert"
        ]
        
        base_prompt = self.generate_analysis_prompt()
        
        for role in roles:
            role_prompt = f"""# {role} Analysis Request

{base_prompt}

## Your Specific Focus
As a {role}, please pay special attention to:
"""
            
            if "Security" in role:
                role_prompt += """
- Authentication and authorization mechanisms
- Input validation and sanitization
- Secret management practices
- Security headers and CORS configuration
- Vulnerability assessment
"""
            elif "Performance" in role:
                role_prompt += """
- Algorithm complexity and optimization opportunities
- Database query performance
- Caching strategy effectiveness
- Connection pooling usage
- Async/await patterns
"""
            elif "Reliability" in role:
                role_prompt += """
- Error handling patterns
- Retry mechanisms and circuit breakers
- Health check implementations
- Monitoring and alerting coverage
- Disaster recovery procedures
"""
            elif "Scalability" in role:
                role_prompt += """
- Horizontal scaling readiness
- Load balancing strategies
- Database sharding approaches
- Microservices architecture patterns
- Distributed systems design
"""
            elif "Code Quality" in role:
                role_prompt += """
- Code organization and structure
- Type hints and documentation
- Test coverage and quality
- Linting and formatting compliance
- Dependency management
"""
            
            prompts[role] = role_prompt
        
        return prompts
    
    def _load_context(self, files: List[str]) -> str:
        """Load context from key files"""
        context_parts = []
        
        for file_path in files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")[:5000]  # Limit size
                    context_parts.append(f"=== {file_path} ===\n{content}\n")
                except Exception as e:
                    context_parts.append(f"=== {file_path} ===\n[Error reading: {e}]\n")
        
        return "\n".join(context_parts)
    
    def _generate_unified_report(self, results: List[Dict[str, Any]]):
        """Generate unified report from all analyses"""
        report = f"""# Unified Multi-AI Analysis Report - Ouroboros System

**Generated**: {datetime.utcnow().isoformat()}
**Mode**: API-Integrated Orchestration
**Cycles**: {max(r.get('cycle', 1) for r in results)}

---

## Summary

This report aggregates analyses from multiple AI specialists analyzing the Ouroboros System.

## Analyses

"""
        
        for result in results:
            if "error" not in result:
                report += f"### {result['role']} (Cycle {result['cycle']})\n\n"
                report += f"{result['analysis']}\n\n"
                report += "---\n\n"
        
        # Save unified report
        output_file = AUDIT_DIR / f"UNIFIED_AI_ANALYSIS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        output_file.write_text(report, encoding="utf-8")
        print(f"\n✅ Unified report saved to {output_file.name}")
    
    def run(self, cycles: int = 1) -> List[Dict[str, Any]]:
        """Run orchestration in the configured mode"""
        if self.mode == "prompts" or not self.has_api:
            # Generate prompts for manual use
            print("📝 Generating prompt templates for manual analysis...")
            prompts = self.generate_prompts()
            
            # Save prompts
            output_dir = Path("D:/codex") if Path("D:/codex").exists() else self.project_root / "prompts"
            output_dir.mkdir(exist_ok=True)
            
            for role, prompt in prompts.items():
                filename = f"{role.lower().replace(' ', '_')}_filled.md"
                output_file = output_dir / filename
                output_file.write_text(prompt, encoding="utf-8")
                print(f"  ✅ {filename}")
            
            print(f"\n✅ Prompts saved to {output_dir}")
            print("📋 Copy-paste these prompts into ChatGPT for analysis")
            
            return []
        else:
            # Run API orchestration
            print("🤖 Running API-integrated orchestration...")
            return self.run_api_orchestration(cycles)


def main():
    parser = argparse.ArgumentParser(
        description="Unified Multi-AI Orchestration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect mode
  python unified_multi_ai_orchestrate.py
  
  # Check capabilities
  python unified_multi_ai_orchestrate.py --check
  
  # Force API mode
  python unified_multi_ai_orchestrate.py --mode api --cycles 3
  
  # Generate prompts only
  python unified_multi_ai_orchestrate.py --mode prompts
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["auto", "api", "prompts"],
        default="auto",
        help="Orchestration mode (default: auto)"
    )
    
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of evolution cycles (API mode only, default: 1)"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check capabilities and exit"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show setup instructions"
    )
    
    args = parser.parse_args()
    
    orchestrator = UnifiedMultiAIOrchestrator(mode=args.mode)
    
    if args.setup:
        print("""
╔═══════════════════════════════════════════════════════════════╗
║           UNIFIED MULTI-AI ORCHESTRATION SETUP               ║
╚═══════════════════════════════════════════════════════════════╝

API MODE (Automated):
  1. Get OpenAI API key from https://platform.openai.com/api-keys
  2. Set environment variable:
     Windows: set OPENAI_API_KEY=your_key_here
     Linux/Mac: export OPENAI_API_KEY=your_key_here
  3. Install openai package:
     pip install openai
  4. Run: python unified_multi_ai_orchestrate.py --mode api

PROMPT MODE (Free, Manual):
  1. Run: python unified_multi_ai_orchestrate.py --mode prompts
  2. Prompts will be saved to D:/codex/*_filled.md
  3. Copy-paste prompts into ChatGPT
  4. Implement suggestions manually

AUTO MODE (Default):
  - Automatically detects if API is configured
  - Falls back to prompt generation if not
  - Run: python unified_multi_ai_orchestrate.py

COST ESTIMATE (API Mode):
  - ~$0.50-$5.00 per run (5 AIs × cycles)
  - Depends on model and response length
        """)
        return
    
    if args.check:
        caps = orchestrator.check_capabilities()
        print("\n╔═══════════════════════════════════════════════════════════════╗")
        print("║              CAPABILITY CHECK                                  ║")
        print("╠═══════════════════════════════════════════════════════════════╣")
        for key, value in caps.items():
            status = "✅" if value else "❌"
            print(f"║  {status} {key.replace('_', ' ').title():<45} ║")
        print("╚═══════════════════════════════════════════════════════════════╝\n")
        
        if caps["openai_api"] and caps["api_key_configured"]:
            print("✅ API mode available - Full automation enabled")
        else:
            print("⚠️  API mode not available - Will generate prompts")
        return
    
    # Run orchestration
    results = orchestrator.run(cycles=args.cycles)
    
    if results:
        print(f"\n✅ Orchestration complete! {len(results)} analyses generated.")


if __name__ == "__main__":
    main()

