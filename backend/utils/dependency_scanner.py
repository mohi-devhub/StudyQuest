"""
Dependency Vulnerability Scanner
Scans npm and pip dependencies for known CVEs
"""
import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Vulnerability:
    """Represents a dependency vulnerability"""
    package: str
    severity: str
    cve: str
    description: str
    vulnerable_versions: str
    patched_versions: str
    dependency_type: str  # 'npm' or 'pip'


class DependencyScanner:
    """Scans dependencies for known CVEs"""
    
    SEVERITY_ORDER = {'critical': 0, 'high': 1, 'moderate': 2, 'medium': 2, 'low': 3, 'info': 4}
    
    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.vulnerabilities: List[Vulnerability] = []
    
    def scan_npm_packages(self, frontend_path: str = 'frontend') -> List[Vulnerability]:
        """Run npm audit and parse results"""
        npm_vulns = []
        frontend_dir = self.root_path / frontend_path
        
        if not (frontend_dir / 'package.json').exists():
            print(f"No package.json found in {frontend_dir}")
            return npm_vulns
        
        try:
            print(f"Running npm audit in {frontend_dir}...")
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                # Parse npm audit v7+ format
                if 'vulnerabilities' in audit_data:
                    for pkg_name, vuln_data in audit_data.get('vulnerabilities', {}).items():
                        severity = vuln_data.get('severity', 'unknown')
                        
                        # Get CVE info
                        via = vuln_data.get('via', [])
                        cve_list = []
                        description = ''
                        
                        for v in via:
                            if isinstance(v, dict):
                                if 'cve' in v:
                                    cve_list.extend(v['cve'])
                                if 'title' in v:
                                    description = v['title']
                        
                        vuln = Vulnerability(
                            package=pkg_name,
                            severity=severity,
                            cve=', '.join(cve_list) if cve_list else 'N/A',
                            description=description or vuln_data.get('name', 'No description'),
                            vulnerable_versions=vuln_data.get('range', 'unknown'),
                            patched_versions=vuln_data.get('fixAvailable', {}).get('version', 'unknown') if isinstance(vuln_data.get('fixAvailable'), dict) else 'unknown',
                            dependency_type='npm'
                        )
                        npm_vulns.append(vuln)
                
                # Parse npm audit v6 format (fallback)
                elif 'advisories' in audit_data:
                    for advisory_id, advisory in audit_data.get('advisories', {}).items():
                        vuln = Vulnerability(
                            package=advisory.get('module_name', 'unknown'),
                            severity=advisory.get('severity', 'unknown'),
                            cve=advisory.get('cves', ['N/A'])[0] if advisory.get('cves') else 'N/A',
                            description=advisory.get('title', 'No description'),
                            vulnerable_versions=advisory.get('vulnerable_versions', 'unknown'),
                            patched_versions=advisory.get('patched_versions', 'unknown'),
                            dependency_type='npm'
                        )
                        npm_vulns.append(vuln)
        
        except subprocess.TimeoutExpired:
            print("npm audit timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing npm audit output: {e}")
        except Exception as e:
            print(f"Error running npm audit: {e}")
        
        return npm_vulns
    
    def scan_pip_packages(self, backend_path: str = 'backend') -> List[Vulnerability]:
        """Run pip-audit and parse results"""
        pip_vulns = []
        backend_dir = self.root_path / backend_path
        
        if not (backend_dir / 'requirements.txt').exists():
            print(f"No requirements.txt found in {backend_dir}")
            return pip_vulns
        
        # Check if pip-audit is installed
        try:
            subprocess.run(['pip-audit', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("pip-audit not installed. Installing...")
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pip-audit'], check=True)
            except Exception as e:
                print(f"Failed to install pip-audit: {e}")
                return pip_vulns
        
        try:
            print(f"Running pip-audit in {backend_dir}...")
            result = subprocess.run(
                ['pip-audit', '--format', 'json', '-r', 'requirements.txt'],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                # Parse pip-audit format
                for vuln_data in audit_data.get('dependencies', []):
                    for vuln in vuln_data.get('vulns', []):
                        vulnerability = Vulnerability(
                            package=vuln_data.get('name', 'unknown'),
                            severity=self._map_pip_severity(vuln.get('id', '')),
                            cve=vuln.get('id', 'N/A'),
                            description=vuln.get('description', 'No description'),
                            vulnerable_versions=vuln_data.get('version', 'unknown'),
                            patched_versions=', '.join(vuln.get('fix_versions', [])) if vuln.get('fix_versions') else 'unknown',
                            dependency_type='pip'
                        )
                        pip_vulns.append(vulnerability)
        
        except subprocess.TimeoutExpired:
            print("pip-audit timed out")
        except json.JSONDecodeError as e:
            print(f"Error parsing pip-audit output: {e}")
        except Exception as e:
            print(f"Error running pip-audit: {e}")
        
        return pip_vulns
    
    def _map_pip_severity(self, cve_id: str) -> str:
        """Map CVE to severity (simplified - would need CVE database for accurate mapping)"""
        # This is a simplified mapping. In production, you'd query a CVE database
        return 'medium'  # Default to medium if we can't determine
    
    def categorize_vulnerabilities(self, vulns: List[Vulnerability]) -> Dict[str, List[Vulnerability]]:
        """Categorize vulnerabilities by severity"""
        categorized = {
            'critical': [],
            'high': [],
            'moderate': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        for vuln in vulns:
            severity = vuln.severity.lower()
            if severity in categorized:
                categorized[severity].append(vuln)
            else:
                categorized['medium'].append(vuln)
        
        return categorized
    
    def prioritize_vulnerabilities(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Sort vulnerabilities by severity"""
        return sorted(vulns, key=lambda v: self.SEVERITY_ORDER.get(v.severity.lower(), 99))
    
    def generate_report(self) -> str:
        """Generate vulnerability report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("DEPENDENCY VULNERABILITY SCAN REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTotal vulnerabilities found: {len(self.vulnerabilities)}\n")
        
        if not self.vulnerabilities:
            report_lines.append("✓ No vulnerabilities detected!\n")
            return "\n".join(report_lines)
        
        # Categorize by severity
        categorized = self.categorize_vulnerabilities(self.vulnerabilities)
        
        # Report by severity
        for severity in ['critical', 'high', 'moderate', 'medium', 'low', 'info']:
            vulns = categorized.get(severity, [])
            if vulns:
                report_lines.append(f"\n{severity.upper()} SEVERITY ({len(vulns)} vulnerabilities)")
                report_lines.append("-" * 80)
                
                for vuln in vulns:
                    report_lines.append(f"\n  Package: {vuln.package} ({vuln.dependency_type})")
                    report_lines.append(f"  CVE: {vuln.cve}")
                    report_lines.append(f"  Description: {vuln.description}")
                    report_lines.append(f"  Vulnerable Versions: {vuln.vulnerable_versions}")
                    report_lines.append(f"  Patched Versions: {vuln.patched_versions}")
                    report_lines.append("")
        
        report_lines.append("\n" + "=" * 80)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 80)
        report_lines.append("1. Update packages with critical/high vulnerabilities immediately")
        report_lines.append("2. Review and update moderate/medium vulnerabilities")
        report_lines.append("3. Set up automated dependency scanning in CI/CD")
        report_lines.append("4. Regularly run security audits")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str):
        """Save report to file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {filename}")
    
    def scan_all(self) -> List[Vulnerability]:
        """Scan both npm and pip dependencies"""
        print("Scanning dependencies for vulnerabilities...\n")
        
        npm_vulns = self.scan_npm_packages()
        pip_vulns = self.scan_pip_packages()
        
        self.vulnerabilities = npm_vulns + pip_vulns
        return self.vulnerabilities


def main():
    """Main function to run the scanner"""
    scanner = DependencyScanner('.')
    vulnerabilities = scanner.scan_all()
    
    # Print report
    print("\n" + scanner.generate_report())
    
    # Save to file
    scanner.save_report('DEPENDENCY_SCAN_REPORT.txt')
    
    # Exit with error code if critical/high vulnerabilities found
    critical_high = [v for v in vulnerabilities if v.severity.lower() in ['critical', 'high']]
    sys.exit(1 if critical_high else 0)


if __name__ == '__main__':
    main()
