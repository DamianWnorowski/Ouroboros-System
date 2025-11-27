#!/usr/bin/env python3
"""
API Key Validator - Validate and categorize found API keys
Helps identify real API keys vs false positives
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional

# Known API key patterns with validation
VALIDATORS = {
    'OpenAI API Key': {
        'pattern': r'^sk-[a-zA-Z0-9]{32,}$',
        'description': 'OpenAI API key starting with sk-',
        'priority': 'HIGH'
    },
    'AWS Access Key ID': {
        'pattern': r'^AKIA[0-9A-Z]{16}$',
        'description': 'AWS access key ID',
        'priority': 'CRITICAL'
    },
    'AWS Secret Key': {
        'pattern': r'^[a-zA-Z0-9+/]{40}$',
        'description': 'AWS secret access key (40 chars base64)',
        'priority': 'CRITICAL'
    },
    'GitHub Personal Access Token': {
        'pattern': r'^ghp_[a-zA-Z0-9]{36}$',
        'description': 'GitHub personal access token',
        'priority': 'HIGH'
    },
    'Stripe Live Secret Key': {
        'pattern': r'^sk_live_[a-zA-Z0-9]{24,}$',
        'description': 'Stripe live secret key',
        'priority': 'CRITICAL'
    },
    'Stripe Test Secret Key': {
        'pattern': r'^sk_test_[a-zA-Z0-9]{24,}$',
        'description': 'Stripe test secret key',
        'priority': 'MEDIUM'
    },
    'Google API Key': {
        'pattern': r'^AIza[0-9A-Za-z\-_]{35}$',
        'description': 'Google Cloud API key',
        'priority': 'HIGH'
    },
}


def validate_key(key: str, key_type: str) -> Dict:
    """Validate if a key matches known patterns"""
    result = {
        'key': key,
        'type': key_type,
        'valid': False,
        'priority': 'LOW',
        'description': '',
        'needs_rotation': False
    }
    
    # Check against validators
    for validator_type, validator_info in VALIDATORS.items():
        if re.match(validator_info['pattern'], key):
            result['valid'] = True
            result['type'] = validator_type
            result['priority'] = validator_info['priority']
            result['description'] = validator_info['description']
            result['needs_rotation'] = validator_info['priority'] in ['CRITICAL', 'HIGH']
            break
    
    # Additional heuristics
    if not result['valid']:
        # Check if it looks like a real key (not just random text)
        if len(key) >= 32 and len(key) <= 100:
            # Has mix of alphanumeric
            if re.match(r'^[a-zA-Z0-9\-_]+$', key):
                # Not all same character
                if len(set(key)) > 5:
                    result['valid'] = True
                    result['priority'] = 'MEDIUM'
                    result['description'] = 'Potential API key (needs manual verification)'
    
    return result


def analyze_report(report_file: Path) -> List[Dict]:
    """Analyze API key report and validate keys"""
    if not report_file.exists():
        print(f"Report file not found: {report_file}")
        return []
    
    content = report_file.read_text(encoding='utf-8')
    
    # Extract keys from report
    keys = []
    current_key = None
    
    for line in content.split('\n'):
        if line.startswith('**Key**:'):
            # Extract key value
            match = re.search(r'\*\*Key\*\*: `([^`]+)`', line)
            if match:
                key_value = match.group(1)
                if '...' in key_value:
                    # Try to find full key
                    continue
                current_key = {'key': key_value}
        elif line.startswith('**Type**:') and current_key:
            match = re.search(r'\*\*Type\*\*: `([^`]+)`', line)
            if match:
                current_key['reported_type'] = match.group(1)
        elif line.startswith('**File**:') and current_key:
            match = re.search(r'\*\*File\*\*: `([^`]+)`', line)
            if match:
                current_key['file'] = match.group(1)
                keys.append(current_key)
                current_key = None
    
    # Validate keys
    validated = []
    for key_info in keys:
        validation = validate_key(key_info['key'], key_info.get('reported_type', 'Unknown'))
        key_info.update(validation)
        validated.append(key_info)
    
    return validated


def generate_priority_report(validated_keys: List[Dict], output_file: Path):
    """Generate prioritized report"""
    # Group by priority
    by_priority = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for key_info in validated_keys:
        if key_info.get('valid'):
            priority = key_info.get('priority', 'LOW')
            by_priority[priority].append(key_info)
    
    report = f"""# API Key Validation Report

## Summary

**Total Keys Validated**: {len(validated_keys)}
**Valid API Keys Found**: {sum(1 for k in validated_keys if k.get('valid'))}

### By Priority

- **CRITICAL**: {len(by_priority['CRITICAL'])} keys (rotate immediately!)
- **HIGH**: {len(by_priority['HIGH'])} keys (review and rotate)
- **MEDIUM**: {len(by_priority['MEDIUM'])} keys (verify manually)
- **LOW**: {len(by_priority['LOW'])} keys (likely false positives)

---

## CRITICAL Priority Keys

**These need immediate rotation!**

"""
    
    for key_info in by_priority['CRITICAL']:
        report += f"""
### {key_info.get('type', 'Unknown')}

- **File**: `{key_info.get('file', 'Unknown')}`
- **Key**: `{key_info.get('key', '')[:20]}...` (truncated for security)
- **Description**: {key_info.get('description', '')}
- **Action**: **ROTATE IMMEDIATELY**

"""
    
    report += "\n---\n\n## HIGH Priority Keys\n\n"
    
    for key_info in by_priority['HIGH']:
        report += f"""
### {key_info.get('type', 'Unknown')}

- **File**: `{key_info.get('file', 'Unknown')}`
- **Key**: `{key_info.get('key', '')[:20]}...` (truncated)
- **Description**: {key_info.get('description', '')}
- **Action**: Review and rotate if exposed

"""
    
    report += "\n---\n\n## Recommendations\n\n"
    report += "1. **CRITICAL keys**: Rotate immediately and remove from codebase\n"
    report += "2. **HIGH keys**: Review usage and rotate if in public repos\n"
    report += "3. **MEDIUM keys**: Verify manually - may be false positives\n"
    report += "4. **Use environment variables**: Never hardcode keys in code\n"
    report += "5. **Use secret managers**: Consider using AWS Secrets Manager, HashiCorp Vault, etc.\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"Priority report saved to: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate API keys from search report")
    parser.add_argument(
        '--report',
        type=str,
        default='api_keys_report.md',
        help='Path to API keys report file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='api_keys_validated.md',
        help='Output file for validated report'
    )
    
    args = parser.parse_args()
    
    report_file = Path(args.report)
    output_file = Path(args.output)
    
    print("Validating API keys from report...")
    validated_keys = analyze_report(report_file)
    
    if not validated_keys:
        print("No keys found in report or report format not recognized.")
        print("Try running the finder again: python scripts/find_api_keys.py --common")
        return
    
    print(f"Validated {len(validated_keys)} keys")
    
    # Count valid keys
    valid_count = sum(1 for k in validated_keys if k.get('valid'))
    critical_count = sum(1 for k in validated_keys if k.get('priority') == 'CRITICAL')
    high_count = sum(1 for k in validated_keys if k.get('priority') == 'HIGH')
    
    print(f"\nResults:")
    print(f"  Valid API keys: {valid_count}")
    print(f"  CRITICAL: {critical_count}")
    print(f"  HIGH: {high_count}")
    
    if valid_count > 0:
        generate_priority_report(validated_keys, output_file)
        print(f"\nReview the validated report: {output_file}")
        if critical_count > 0:
            print(f"\nWARNING: {critical_count} CRITICAL keys found - rotate immediately!")
    else:
        print("\nNo valid API keys found - likely all false positives.")


if __name__ == "__main__":
    main()

