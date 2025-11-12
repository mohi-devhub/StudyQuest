"""
Secret Scanner Utility
Scans codebase for hardcoded secrets, API keys, passwords, and tokens
"""
import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import json


@dataclass
class SecurityIssue:
    """Represents a security issue found in the codebase"""
    severity: str
    category: str
    description: str
    file_path: str
    line_number: int
    line_content: str
    pattern_matched: str


class SecretScanner:
    """Scans codebase for hardcoded secrets"""
    
    # Regex patterns for detecting secrets
    PATTERNS = {
        'api_key': [
            r'(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
            r'(api[_-]?key|apikey)\s*[=:]\s*([A-Za-z0-9_\-]{20,})',
        ],
        'password': [
            r'(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']',
        ],
        'token': [
            r'(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\']([^"\']{20,})["\']',
            r'(bearer|jwt)\s+([A-Za-z0-9_\-\.]{20,})',
        ],
        'secret': [
            r'(secret|secret[_-]?key)\s*[=:]\s*["\']([^"\']{20,})["\']',
        ],
        'private_key': [
            r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        ],
        'aws_key': [
            r'(AKIA[0-9A-Z]{16})',
        ],
    }
    
    # Patterns to exclude (common false positives)
    EXCLUDE_PATTERNS = [
        r'\.env\.example',
        r'\.env\.local\.example',
        r'example[_-]?key',
        r'your[_-]?api[_-]?key',
        r'placeholder',
        r'<.*>',
        r'\{.*\}',
        r'\$\{.*\}',
        r'process\.env\.',
        r'os\.getenv',
        r'os\.environ',
        r'config\.',
        r'settings\.',
    ]
    
    # Directories to skip
    SKIP_DIRS = {
        'node_modules', 'venv', '__pycache__', '.git', '.next', 
        'dist', 'build', '.swc', 'cypress/videos', 'cypress/screenshots'
    }
    
    # File extensions to scan
    SCAN_EXTENSIONS = {'.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.yaml', '.yml', '.env'}
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.issues: List[SecurityIssue] = []
    
    def is_false_positive(self, line: str) -> bool:
        """Check if the line matches exclude patterns (false positives)"""
        line_lower = line.lower()
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, line_lower, re.IGNORECASE):
                return True
        return False
    
    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for secrets"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, start=1):
                # Skip if it's a false positive
                if self.is_false_positive(line):
                    continue
                
                # Check each pattern category
                for category, patterns in self.PATTERNS.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Additional validation: skip if value looks like a variable reference
                            matched_text = match.group(0)
                            if any(exclude in matched_text.lower() for exclude in ['env', 'config', 'settings']):
                                continue
                            
                            issue = SecurityIssue(
                                severity='high' if category in ['private_key', 'aws_key'] else 'medium',
                                category=category,
                                description=f'Potential {category.replace("_", " ")} found',
                                file_path=str(file_path.relative_to(self.root_path)),
                                line_number=line_num,
                                line_content=line.strip(),
                                pattern_matched=pattern
                            )
                            issues.append(issue)
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return issues
    
    def scan_directory(self, path: Path = None) -> List[SecurityIssue]:
        """Recursively scan directory for secrets"""
        if path is None:
            path = self.root_path
        
        all_issues = []
        
        for item in path.rglob('*'):
            # Skip directories in SKIP_DIRS
            if any(skip_dir in item.parts for skip_dir in self.SKIP_DIRS):
                continue
            
            # Only scan files with relevant extensions
            if item.is_file() and item.suffix in self.SCAN_EXTENSIONS:
                issues = self.scan_file(item)
                all_issues.extend(issues)
        
        self.issues = all_issues
        return all_issues
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate security report"""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate text format report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("SECRET SCANNER REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTotal issues found: {len(self.issues)}\n")
        
        if not self.issues:
            report_lines.append("✓ No hardcoded secrets detected!\n")
            return "\n".join(report_lines)
        
        # Group by severity
        by_severity = {}
        for issue in self.issues:
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)
        
        # Report by severity
        for severity in ['high', 'medium', 'low']:
            if severity in by_severity:
                issues = by_severity[severity]
                report_lines.append(f"\n{severity.upper()} SEVERITY ({len(issues)} issues)")
                report_lines.append("-" * 80)
                
                for issue in issues:
                    report_lines.append(f"\n  Category: {issue.category}")
                    report_lines.append(f"  File: {issue.file_path}:{issue.line_number}")
                    report_lines.append(f"  Description: {issue.description}")
                    report_lines.append(f"  Line: {issue.line_content[:100]}")
                    report_lines.append("")
        
        report_lines.append("\n" + "=" * 80)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 80)
        report_lines.append("1. Move all secrets to environment variables")
        report_lines.append("2. Use .env files (never commit to git)")
        report_lines.append("3. Update .gitignore to exclude .env files")
        report_lines.append("4. Rotate any exposed credentials immediately")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        report = {
            'total_issues': len(self.issues),
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'description': issue.description,
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'line_content': issue.line_content,
                }
                for issue in self.issues
            ]
        }
        return json.dumps(report, indent=2)
    
    def save_report(self, filename: str, output_format: str = 'text'):
        """Save report to file"""
        report = self.generate_report(output_format)
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {filename}")


def main():
    """Main function to run the scanner"""
    import sys
    
    # Get root path from command line or use current directory
    root_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print(f"Scanning {root_path} for hardcoded secrets...")
    scanner = SecretScanner(root_path)
    issues = scanner.scan_directory()
    
    # Print report
    print(scanner.generate_report())
    
    # Save to file
    scanner.save_report('SECRET_SCAN_REPORT.txt', 'text')
    scanner.save_report('SECRET_SCAN_REPORT.json', 'json')
    
    # Exit with error code if issues found
    sys.exit(1 if issues else 0)


if __name__ == '__main__':
    main()
