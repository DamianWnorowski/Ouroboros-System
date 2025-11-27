#!/usr/bin/env python3
"""
API Key Finder - Search entire system for lost API keys
Searches all drives and common locations for API key patterns
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime
import argparse

# Common API key patterns
API_KEY_PATTERNS = [
    # OpenAI
    (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API Key'),
    (r'OPENAI_API_KEY["\s:=]+([a-zA-Z0-9\-_]{32,})', 'OpenAI API Key (env)'),
    
    # Generic API keys
    (r'api[_-]?key["\s:=]+([a-zA-Z0-9\-_]{20,})', 'Generic API Key'),
    (r'apikey["\s:=]+([a-zA-Z0-9\-_]{20,})', 'API Key (no separator)'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'aws[_-]?secret[_-]?access[_-]?key["\s:=]+([a-zA-Z0-9+/]{40})', 'AWS Secret Key'),
    
    # Google Cloud
    (r'AIza[0-9A-Za-z\-_]{35}', 'Google API Key'),
    (r'ya29\.[a-zA-Z0-9\-_]+', 'Google OAuth Token'),
    
    # GitHub
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
    (r'github[_-]?token["\s:=]+([a-zA-Z0-9]{36,})', 'GitHub Token'),
    
    # Azure
    (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'Azure/GUID (potential)'),
    
    # Stripe
    (r'sk_live_[a-zA-Z0-9]{24,}', 'Stripe Live Secret Key'),
    (r'sk_test_[a-zA-Z0-9]{24,}', 'Stripe Test Secret Key'),
    (r'pk_live_[a-zA-Z0-9]{24,}', 'Stripe Live Publishable Key'),
    
    # Generic tokens (more specific to reduce false positives)
    (r'[a-zA-Z0-9\-_]{40,}', 'Potential Token/Key (40+ chars)'),
]

# Common file extensions to search
SEARCH_EXTENSIONS = {
    '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.txt', '.md',
    '.sh', '.ps1', '.bat', '.cmd', '.config', '.conf', '.ini', '.properties',
    '.xml', '.toml', '.cfg', '.log'
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
    'Library', 'System', 'Windows', 'Program Files', 'Program Files (x86)',
    '$Recycle.Bin', 'System Volume Information', 'AppData\\Local\\Temp',
    'AppData\\Roaming\\npm', 'AppData\\Local\\pip'
}

# Common locations to check first
COMMON_LOCATIONS = [
    Path.home() / '.ssh',
    Path.home() / '.config',
    Path.home() / '.secrets',
    Path.home() / 'Documents',
    Path.home() / 'Desktop',
    Path.home() / 'Downloads',
    Path.home() / '.env',
    Path.home() / '.bashrc',
    Path.home() / '.bash_profile',
    Path.home() / '.zshrc',
    Path.home() / '.profile',
]


class APIKeyFinder:
    """Find API keys across the system"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.found_keys: List[Dict] = []
        self.scanned_files = 0
        self.scanned_dirs = 0
        self.errors = []
        
    def get_all_drives(self) -> List[Path]:
        """Get all available drives"""
        drives = []
        
        # Windows
        if os.name == 'nt':
            import string
            for letter in string.ascii_uppercase:
                drive = Path(f"{letter}:\\")
                if drive.exists():
                    drives.append(drive)
        else:
            # Linux/Mac
            drives.append(Path('/'))
            
        return drives
    
    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        path_str = str(path).lower()
        
        # Skip system directories
        for skip_dir in SKIP_DIRS:
            if skip_dir.lower() in path_str:
                return True
        
        # Skip hidden directories (except .ssh, .config, .secrets)
        if path.name.startswith('.') and path.name not in ['.ssh', '.config', '.secrets', '.env']:
            if path.is_dir():
                return True
        
        return False
    
    def extract_api_key(self, content: str, file_path: Path) -> List[Dict]:
        """Extract API keys from content"""
        found = []
        lines = content.split('\n')
        
        for pattern, key_type in API_KEY_PATTERNS:
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    key_value = match.group(1) if match.groups() else match.group(0)
                    
                    # Skip if it's a comment or documentation
                    stripped_line = line.strip()
                    if stripped_line.startswith('#') or stripped_line.startswith('//'):
                        continue
                    
                    # Skip if it's a placeholder
                    if any(word in key_value.lower() for word in ['example', 'placeholder', 'your_', 'replace', 'xxx', 'test_key']):
                        continue
                    
                    # Skip if it's clearly a hash (all hex, very long)
                    if len(key_value) > 50 and re.match(r'^[0-9a-f]{40,}$', key_value, re.IGNORECASE):
                        continue
                    
                    # Skip if it's a UUID (has dashes in UUID format)
                    if re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', key_value, re.IGNORECASE):
                        if key_type == 'Azure/GUID (potential)':
                            continue  # Skip generic GUID matches
                    
                    found.append({
                        'type': key_type,
                        'key': key_value[:50] + '...' if len(key_value) > 50 else key_value,
                        'full_key': key_value,  # Store full key for user
                        'file': str(file_path),
                        'line': line_num,
                        'context': line.strip()[:100]
                    })
        
        return found
    
    def search_file(self, file_path: Path) -> List[Dict]:
        """Search a single file for API keys"""
        try:
            # Check extension
            if file_path.suffix.lower() not in SEARCH_EXTENSIONS:
                return []
            
            # Read file
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except (UnicodeDecodeError, PermissionError):
                return []
            
            # Extract keys
            found = self.extract_api_key(content, file_path)
            return found
            
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return []
    
    def search_directory(self, directory: Path, max_depth: int = 10, current_depth: int = 0) -> List[Dict]:
        """Recursively search directory"""
        if current_depth > max_depth:
            return []
        
        if self.should_skip_path(directory):
            return []
        
        found = []
        
        try:
            if not directory.exists() or not directory.is_dir():
                return []
            
            self.scanned_dirs += 1
            
            # Search files in directory
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        self.scanned_files += 1
                        file_keys = self.search_file(item)
                        found.extend(file_keys)
                    elif item.is_dir() and not self.should_skip_path(item):
                        # Recursively search subdirectory
                        sub_keys = self.search_directory(item, max_depth, current_depth + 1)
                        found.extend(sub_keys)
                except PermissionError:
                    continue
                except Exception as e:
                    self.errors.append(f"Error processing {item}: {e}")
                    
        except PermissionError:
            pass
        except Exception as e:
            self.errors.append(f"Error accessing {directory}: {e}")
        
        return found
    
    def search_common_locations(self) -> List[Dict]:
        """Search common locations first"""
        print("Searching common locations...")
        found = []
        
        for location in COMMON_LOCATIONS:
            if location.exists():
                if location.is_file():
                    found.extend(self.search_file(location))
                elif location.is_dir():
                    found.extend(self.search_directory(location, max_depth=3))
        
        return found
    
    def search_all_drives(self, max_depth: int = 5) -> List[Dict]:
        """Search all drives (with limited depth for performance)"""
        print("Searching all drives (this may take a while)...")
        drives = self.get_all_drives()
        all_found = []
        
        for drive in drives:
            print(f"  Searching {drive}...")
            try:
                found = self.search_directory(drive, max_depth=max_depth)
                all_found.extend(found)
                print(f"    Found {len(found)} potential keys")
            except Exception as e:
                print(f"    Error searching {drive}: {e}")
        
        return all_found
    
    def deduplicate_keys(self, keys: List[Dict]) -> List[Dict]:
        """Remove duplicate keys"""
        seen = set()
        unique = []
        
        for key_info in keys:
            key_id = (key_info['full_key'], key_info['file'])
            if key_id not in seen:
                seen.add(key_id)
                unique.append(key_info)
        
        return unique
    
    def generate_report(self, keys: List[Dict], output_file: Optional[Path] = None) -> str:
        """Generate a report of found keys"""
        report = f"""# API Key Search Report

**Generated**: {datetime.now().isoformat()}
**Total Keys Found**: {len(keys)}
**Files Scanned**: {self.scanned_files:,}
**Directories Scanned**: {self.scanned_dirs:,}
**Errors**: {len(self.errors)}

---

## ⚠️ SECURITY WARNING

**DO NOT COMMIT THIS FILE TO GIT!**
**DO NOT SHARE THESE KEYS!**
**REVIEW AND ROTATE ANY EXPOSED KEYS IMMEDIATELY!**

---

## Found API Keys

"""
        
        # Group by type
        by_type = {}
        for key_info in keys:
            key_type = key_info['type']
            if key_type not in by_type:
                by_type[key_type] = []
            by_type[key_type].append(key_info)
        
        for key_type, key_list in sorted(by_type.items()):
            report += f"\n### {key_type} ({len(key_list)} found)\n\n"
            
            for key_info in key_list:
                report += f"**File**: `{key_info['file']}`\n"
                report += f"**Line**: {key_info['line']}\n"
                report += f"**Key**: `{key_info['key']}`\n"
                report += f"**Context**: `{key_info['context']}`\n"
                report += "\n---\n\n"
        
        if self.errors:
            report += "\n## Errors\n\n"
            for error in self.errors[:20]:  # Limit errors
                report += f"- {error}\n"
        
        # Save to file
        if output_file:
            output_file.write_text(report, encoding='utf-8')
            print(f"\nReport saved to: {output_file}")
        
        return report
    
    def save_keys_json(self, keys: List[Dict], output_file: Path):
        """Save keys to JSON (for programmatic use)"""
        # Redact full keys in JSON for safety
        safe_keys = []
        for key_info in keys:
            safe_info = key_info.copy()
            # Only show first 8 and last 4 chars
            full_key = safe_info['full_key']
            if len(full_key) > 12:
                safe_info['full_key'] = full_key[:8] + '...' + full_key[-4:]
            safe_keys.append(safe_info)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'total_found': len(keys),
            'keys': safe_keys
        }
        
        output_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f"Keys summary saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Find API keys across the system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search common locations only (fast)
  python find_api_keys.py --common
  
  # Search entire system (slow, but thorough)
  python find_api_keys.py --all-drives
  
  # Search project directory only
  python find_api_keys.py --project
  
  # Search specific directory
  python find_api_keys.py --dir "C:\\Users\\YourName\\Documents"
        """
    )
    
    parser.add_argument(
        '--common',
        action='store_true',
        help='Search common locations only (fast)'
    )
    
    parser.add_argument(
        '--all-drives',
        action='store_true',
        help='Search all drives (slow, but thorough)'
    )
    
    parser.add_argument(
        '--project',
        action='store_true',
        help='Search project directory only'
    )
    
    parser.add_argument(
        '--dir',
        type=str,
        help='Search specific directory'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='api_keys_report.md',
        help='Output file for report (default: api_keys_report.md)'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Also save JSON summary to this file'
    )
    
    args = parser.parse_args()
    
    finder = APIKeyFinder()
    
    print("=" * 63)
    print("API KEY FINDER - SYSTEM SCAN")
    print("=" * 63)
    print("WARNING: This will search for API keys on your system")
    print("Review results carefully and rotate any exposed keys!")
    print("=" * 63)
    print()
    
    found_keys = []
    
    if args.dir:
        # Search specific directory
        target_dir = Path(args.dir)
        if target_dir.exists():
            print(f"Searching directory: {target_dir}")
            found_keys = finder.search_directory(target_dir, max_depth=10)
        else:
            print(f"Directory not found: {target_dir}")
            return
    elif args.project:
        # Search project directory
        print("Searching project directory...")
        found_keys = finder.search_directory(finder.project_root, max_depth=10)
    elif args.all_drives:
        # Search all drives
        found_keys = finder.search_all_drives(max_depth=3)
    else:
        # Default: search common locations
        found_keys = finder.search_common_locations()
    
    # Deduplicate
    found_keys = finder.deduplicate_keys(found_keys)
    
    # Generate report
    output_path = Path(args.output)
    report = finder.generate_report(found_keys, output_path)
    
    # Save JSON if requested
    if args.json:
        finder.save_keys_json(found_keys, Path(args.json))
    
    # Print summary
    print("\n" + "=" * 63)
    print("SEARCH COMPLETE")
    print("=" * 63)
    print(f"Keys Found:        {len(found_keys)}")
    print(f"Files Scanned:     {finder.scanned_files:,}")
    print(f"Directories:       {finder.scanned_dirs:,}")
    print(f"Report Saved:      {output_path}")
    print("=" * 63)
    print("IMPORTANT: Review the report and rotate any exposed")
    print("keys immediately! Do NOT commit keys to Git!")
    print("=" * 63)
    print()
    
    if found_keys:
        print("Key Types Found:")
        by_type = {}
        for key_info in found_keys:
            key_type = key_info['type']
            by_type[key_type] = by_type.get(key_type, 0) + 1
        
        for key_type, count in sorted(by_type.items()):
            print(f"  • {key_type}: {count}")


if __name__ == "__main__":
    main()

