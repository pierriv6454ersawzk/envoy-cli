"""Tests for envoy.lint."""

import pytest
from envoy.lint import lint_env, format_lint_result, LintIssue


def test_clean_env_produces_no_issues():
    result = lint_env({'DATABASE_URL': 'postgres://localhost/db', 'DEBUG': 'false'})
    assert result.issues == []
    assert not result.has_errors
    assert not result.has_warnings


def test_lowercase_key_triggers_warning():
    result = lint_env({'database_url': 'postgres://localhost/db'})
    warnings = [i for i in result.issues if i.severity == 'warning']
    assert any('convention' in i.message for i in warnings)


def test_mixed_case_key_triggers_warning():
    result = lint_env({'MyKey': 'value'})
    assert result.has_warnings


def test_empty_value_triggers_warning():
    result = lint_env({'API_KEY': ''})
    warnings = [i for i in result.issues if 'empty' in i.message.lower()]
    assert len(warnings) == 1
    assert warnings[0].severity == 'warning'


def test_control_character_in_value_triggers_error():
    result = lint_env({'SECRET': 'hello\x01world'})
    errors = [i for i in result.issues if i.severity == 'error']
    assert any('control' in i.message.lower() for i in errors)
    assert result.has_errors


def test_leading_whitespace_in_value_triggers_warning():
    result = lint_env({'PORT': '  8080'})
    warnings = [i for i in result.issues if 'whitespace' in i.message.lower()]
    assert len(warnings) == 1


def test_trailing_whitespace_in_value_triggers_warning():
    result = lint_env({'PORT': '8080  '})
    warnings = [i for i in result.issues if 'whitespace' in i.message.lower()]
    assert len(warnings) == 1


def test_multiple_issues_in_single_env():
    result = lint_env({
        'bad-key': '',
        'GOOD_KEY': 'ok',
    })
    keys_with_issues = {i.key for i in result.issues}
    assert 'bad-key' in keys_with_issues
    # GOOD_KEY has no issues
    assert 'GOOD_KEY' not in keys_with_issues


def test_format_lint_result_no_issues():
    result = lint_env({'VALID': 'value'})
    output = format_lint_result(result)
    assert output == 'No issues found.'


def test_format_lint_result_shows_errors_and_warnings():
    result = lint_env({'bad key': '', 'X': 'hello\x02'})
    output = format_lint_result(result)
    assert '[ERROR]' in output
    assert '[WARN]' in output


def test_has_errors_false_when_only_warnings():
    result = lint_env({'lowercase': 'value'})
    assert result.has_warnings
    assert not result.has_errors
