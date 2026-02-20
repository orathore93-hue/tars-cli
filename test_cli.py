#!/usr/bin/env python3
"""
STARS CLI - Comprehensive Test Suite
Tests all commands and identifies issues
"""

import subprocess
import sys

def run_command(cmd, expect_success=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "✅" if (result.returncode == 0) == expect_success else "❌"
        return status, result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "⏱️", -1, "", "Timeout"
    except Exception as e:
        return "❌", -1, "", str(e)

def test_cli():
    """Test all CLI commands"""
    
    tests = [
        # Basic commands
        ("stars --help", True, "Help command"),
        ("stars version", True, "Version command"),
        
        # Setup commands
        ("echo 'n' | stars setup", True, "Setup command (decline)"),
        ("stars set-api-key --help", True, "Set API key help"),
        ("stars delete-api-key --help", True, "Delete API key help"),
        
        # Info commands (read-only, safe to test)
        ("stars nodes --help", True, "Nodes help"),
        ("stars pods --help", True, "Pods help"),
        ("stars deployments --help", True, "Deployments help"),
        ("stars services --help", True, "Services help"),
        ("stars namespaces --help", True, "Namespaces help"),
        ("stars events --help", True, "Events help"),
        ("stars context --help", True, "Context help"),
        
        # Diagnostic commands
        ("stars health --help", True, "Health help"),
        ("stars diagnose --help", True, "Diagnose help"),
        ("stars analyze --help", True, "Analyze help"),
        ("stars triage --help", True, "Triage help"),
        
        # SRE commands
        ("stars incident --help", True, "Incident help"),
        ("stars blast-radius --help", True, "Blast radius help"),
        ("stars fix-crashloop --help", True, "Fix crashloop help"),
        ("stars clear-evicted --help", True, "Clear evicted help"),
        ("stars rollback --help", True, "Rollback help"),
        ("stars oncall-report --help", True, "Oncall report help"),
        ("stars security-scan --help", True, "Security scan help"),
        
        # Utility commands
        ("stars welcome", True, "Welcome screen"),
        ("stars creator", True, "Creator info"),
        ("stars quote", True, "Quote command"),
    ]
    
    print("🧪 STARS CLI Test Suite\n")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for cmd, expect_success, description in tests:
        status, code, stdout, stderr = run_command(cmd, expect_success)
        
        if status == "✅":
            passed += 1
            print(f"{status} {description}")
        else:
            failed += 1
            print(f"{status} {description}")
            if stderr:
                print(f"   Error: {stderr[:100]}")
    
    print("=" * 80)
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_cli()
    sys.exit(0 if success else 1)
