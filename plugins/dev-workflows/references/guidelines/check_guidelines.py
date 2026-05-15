#!/usr/bin/env python3
"""
Automated GUIDEline compliance checker for Dynatrace apps.

Scans code for common GUIDEline violations and reports findings.

Usage:
    python3 check_guidelines.py /path/to/code/
    python3 check_guidelines.py /path/to/code/ --guideline appheader
    python3 check_guidelines.py /path/to/code/ --output json
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Violation:
    guideline: str
    severity: str  # critical, warning, info
    rule: str
    message: str
    file: str
    line: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class CheckResult:
    guideline: str
    passed: bool
    violations: list = field(default_factory=list)
    files_checked: int = 0


class GuidelineChecker:
    """Base class for guideline-specific checkers."""

    def __init__(self):
        self.violations = []

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        raise NotImplementedError


class AppHeaderChecker(GuidelineChecker):
    """Check AppHeader guideline compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        # Check for AppHeader import
        has_appheader = 'AppHeader' in content

        if has_appheader:
            # Check for help menu (mandatory)
            if 'HelpMenu' not in content and 'AppHeader.HelpMenu' not in content:
                violations.append(Violation(
                    guideline='appheader',
                    severity='critical',
                    rule='Help menu is mandatory',
                    message='AppHeader found but HelpMenu component is missing',
                    file=filepath,
                    suggestion='Add <AppHeader.HelpMenu entries={{...}} /> to your AppHeader'
                ))

            # Check for menus section
            if 'AppHeader.Menus' not in content:
                violations.append(Violation(
                    guideline='appheader',
                    severity='critical',
                    rule='Menus section required',
                    message='AppHeader.Menus wrapper is missing',
                    file=filepath,
                    suggestion='Wrap help menu and settings in <AppHeader.Menus>'
                ))

            # Check for settings icon order (should be before help)
            settings_match = re.search(r'SettingIcon|SettingsIcon', content)
            help_match = re.search(r'HelpMenu|HelpIcon', content)
            if settings_match and help_match:
                if settings_match.start() > help_match.start():
                    violations.append(Violation(
                        guideline='appheader',
                        severity='warning',
                        rule='Menu order: settings before help',
                        message='Settings icon should appear before help menu',
                        file=filepath,
                        suggestion='Reorder menus: settings on left, help on right'
                    ))

        return violations


class DataTableChecker(GuidelineChecker):
    """Check DataTable guideline compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        has_datatable = 'DataTable' in content

        if has_datatable:
            # Check for loading state
            if 'loading' not in content.lower() and 'isLoading' not in content:
                violations.append(Violation(
                    guideline='datatable',
                    severity='warning',
                    rule='Loading states required',
                    message='DataTable may be missing loading state handling',
                    file=filepath,
                    suggestion='Add loading prop or state to show loading indicator'
                ))

            # Check for empty state
            if 'emptyState' not in content and 'EmptyState' not in content:
                violations.append(Violation(
                    guideline='datatable',
                    severity='warning',
                    rule='Empty state required',
                    message='DataTable may be missing empty state handling',
                    file=filepath,
                    suggestion='Add emptyState prop to handle no-data scenarios'
                ))

        return violations


class FilterFieldChecker(GuidelineChecker):
    """Check FilterField guideline compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        has_filterfield = 'FilterField' in content

        if has_filterfield:
            # Check for FilterBar (should not combine with FilterField)
            if 'FilterBar' in content:
                violations.append(Violation(
                    guideline='filterfield',
                    severity='critical',
                    rule='Do not combine FilterField and FilterBar',
                    message='FilterField and FilterBar should not be used together for the same dataset',
                    file=filepath,
                    suggestion='Choose either FilterField (complex filtering) or FilterBar (simple filtering)'
                ))

            # Check for debounce
            if 'debounce' not in content.lower() and 'setTimeout' not in content:
                violations.append(Violation(
                    guideline='filterfield',
                    severity='warning',
                    rule='Debounce required for suggestions',
                    message='FilterField suggestions should be debounced (300ms minimum)',
                    file=filepath,
                    suggestion='Add debounce to suggestion callback to avoid excessive requests'
                ))

        return violations


class AccessibilityChecker(GuidelineChecker):
    """Check WCAG accessibility guideline compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        # Check for images without alt text
        img_without_alt = re.findall(r'<img[^>]*(?<!alt=")[^>]*>', content)
        for match in img_without_alt:
            if 'alt=' not in match:
                violations.append(Violation(
                    guideline='accessibility',
                    severity='critical',
                    rule='Images must have alt text',
                    message='Found <img> without alt attribute',
                    file=filepath,
                    suggestion='Add alt="description" to all images'
                ))
                break  # Report once per file

        # Check for buttons without accessible names
        icon_only_buttons = re.findall(r'<Button[^>]*>\s*<[^>]*Icon[^>]*/>\s*</Button>', content)
        for match in icon_only_buttons:
            if 'aria-label' not in match:
                violations.append(Violation(
                    guideline='accessibility',
                    severity='critical',
                    rule='Icon-only buttons need aria-label',
                    message='Found icon-only button without aria-label',
                    file=filepath,
                    suggestion='Add aria-label="description" to icon-only buttons'
                ))
                break

        # Check for onClick without keyboard handler
        onclick_count = len(re.findall(r'onClick', content))
        onkeydown_count = len(re.findall(r'onKeyDown|onKeyPress|onKeyUp', content))
        if onclick_count > 0 and onkeydown_count == 0:
            violations.append(Violation(
                guideline='accessibility',
                severity='warning',
                rule='Keyboard handlers for interactive elements',
                message='Found onClick handlers but no keyboard event handlers',
                file=filepath,
                suggestion='Add onKeyDown handlers for keyboard accessibility'
            ))

        return violations


class TerminologyChecker(GuidelineChecker):
    """Check alerting terminology compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        # Look for potential terminology issues in user-facing strings
        # This is heuristic - looks for string literals

        # Pattern: "notification" where "alert" might be correct
        # (when action is required)
        action_with_notification = re.findall(
            r'["\'].*(?:action required|must respond|immediate|urgent).*notification.*["\']',
            content, re.IGNORECASE
        )
        if action_with_notification:
            violations.append(Violation(
                guideline='alerting-terminology',
                severity='warning',
                rule='Use "alert" when user action is required',
                message='Found "notification" used with action-required context',
                file=filepath,
                suggestion='If user must take timely action, use "alert" instead of "notification"'
            ))

        return violations


class SettingsChecker(GuidelineChecker):
    """Check settings guideline compliance."""

    def check_file(self, filepath: str, content: str) -> list[Violation]:
        violations = []

        # Check for settings schema patterns
        if 'schema' in filepath.lower() or 'settings' in filepath.lower():
            # Check for proper schema structure
            if '"type"' in content or "'type'" in content:
                if '"description"' not in content and "'description'" not in content:
                    violations.append(Violation(
                        guideline='settings',
                        severity='warning',
                        rule='Settings should have descriptions',
                        message='Settings schema may be missing description fields',
                        file=filepath,
                        suggestion='Add description to all setting fields for better UX'
                    ))

        return violations


def get_checkers(guideline: Optional[str] = None) -> list[GuidelineChecker]:
    """Get checkers to run based on guideline filter."""
    all_checkers = {
        'appheader': AppHeaderChecker(),
        'datatable': DataTableChecker(),
        'filterfield': FilterFieldChecker(),
        'accessibility': AccessibilityChecker(),
        'alerting-terminology': TerminologyChecker(),
        'settings': SettingsChecker(),
    }

    if guideline:
        if guideline not in all_checkers:
            print(f"Unknown guideline: {guideline}")
            print(f"Available: {', '.join(all_checkers.keys())}")
            sys.exit(1)
        return [all_checkers[guideline]]

    return list(all_checkers.values())


def scan_directory(path: str, checkers: list[GuidelineChecker]) -> list[Violation]:
    """Scan directory for violations."""
    violations = []
    extensions = {'.ts', '.tsx', '.js', '.jsx', '.json'}

    path_obj = Path(path)

    if path_obj.is_file():
        files = [path_obj]
    else:
        files = [f for f in path_obj.rglob('*') if f.suffix in extensions]

    for filepath in files:
        # Skip node_modules and dist
        if 'node_modules' in str(filepath) or '/dist/' in str(filepath):
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
            for checker in checkers:
                violations.extend(checker.check_file(str(filepath), content))
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return violations


def format_violations(violations: list[Violation], output_format: str) -> str:
    """Format violations for output."""
    if output_format == 'json':
        return json.dumps([asdict(v) for v in violations], indent=2)

    if not violations:
        return "No violations found."

    lines = [f"Found {len(violations)} violation(s):\n"]

    # Group by severity
    critical = [v for v in violations if v.severity == 'critical']
    warning = [v for v in violations if v.severity == 'warning']
    info = [v for v in violations if v.severity == 'info']

    for severity, group in [('CRITICAL', critical), ('WARNING', warning), ('INFO', info)]:
        if group:
            lines.append(f"\n## {severity} ({len(group)})\n")
            for v in group:
                lines.append(f"- [{v.guideline}] {v.message}")
                lines.append(f"  File: {v.file}")
                if v.suggestion:
                    lines.append(f"  Fix: {v.suggestion}")
                lines.append("")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Check code for GUIDEline compliance')
    parser.add_argument('path', help='File or directory to check')
    parser.add_argument('--guideline', '-g', help='Check specific guideline only')
    parser.add_argument('--output', '-o', choices=['text', 'json'], default='text',
                        help='Output format (default: text)')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path not found: {args.path}")
        sys.exit(1)

    checkers = get_checkers(args.guideline)
    violations = scan_directory(args.path, checkers)

    print(format_violations(violations, args.output))

    # Exit with error code if critical violations found
    critical_count = sum(1 for v in violations if v.severity == 'critical')
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
