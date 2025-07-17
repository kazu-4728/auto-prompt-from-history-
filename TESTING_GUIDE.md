# Testing Guide

This guide provides comprehensive testing strategies and examples for the 現場AIプロンプト自動生成システム.

## Table of Contents

1. [Testing Overview](#testing-overview)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [Template Testing](#template-testing)
5. [CLI Testing](#cli-testing)
6. [Error Handling Testing](#error-handling-testing)
7. [Performance Testing](#performance-testing)
8. [GitHub Actions Testing](#github-actions-testing)
9. [Test Data Management](#test-data-management)
10. [Continuous Testing](#continuous-testing)

## Testing Overview

### Test Structure

```
tests/
├── unit/
│   ├── test_prompt_generator.py
│   ├── test_templates.py
│   └── test_validation.py
├── integration/
│   ├── test_cli.py
│   ├── test_file_operations.py
│   └── test_workflows.py
├── fixtures/
│   ├── test_knowledge.json
│   ├── invalid_knowledge.json
│   └── multiple_projects.json
├── templates/
│   ├── test_claude_prompt.md.j2
│   └── test_copilot_prompt.md.j2
└── conftest.py
```

### Test Dependencies

```bash
pip install pytest pytest-mock pytest-cov
```

## Unit Testing

### Test Setup (`conftest.py`)

```python
import pytest
import json
import tempfile
import os
from pathlib import Path

@pytest.fixture
def sample_knowledge():
    """Sample knowledge data for testing"""
    return {
        "projects": [
            {
                "name": "テストプロジェクト",
                "design_history": [
                    {
                        "date": "2025-01-01",
                        "summary": "初期設計完了"
                    },
                    {
                        "date": "2025-01-15",
                        "summary": "アーキテクチャ変更"
                    }
                ],
                "bug_reports": [
                    {
                        "date": "2025-01-20",
                        "problem": "メモリリークが発生"
                    }
                ],
                "rules": [
                    "テストカバレッジ90%以上",
                    "コードレビュー必須"
                ],
                "prompts": [
                    {
                        "date": "2025-01-10",
                        "prompt": "ユニットテストを作成してください"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def temp_knowledge_file(sample_knowledge):
    """Create temporary knowledge file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_knowledge, f, ensure_ascii=False, indent=2)
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def temp_template_dir():
    """Create temporary template directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test templates
        claude_template = """# Claude Test Template
Project: {{ project_name }}
Rules: {% for rule in rules %}{{ rule }}{% endfor %}"""
        
        copilot_template = """# Copilot Test Template
## Project: {{ project_name }}
### Rules
{% for rule in rules %}
- {{ rule }}
{% endfor %}"""
        
        Path(temp_dir, "claude_prompt.md.j2").write_text(claude_template, encoding='utf-8')
        Path(temp_dir, "copilot_prompt.md.j2").write_text(copilot_template, encoding='utf-8')
        
        yield temp_dir
```

### Core Function Tests (`test_prompt_generator.py`)

```python
import pytest
import json
import os
from unittest.mock import patch, mock_open
from prompt_generator import generate_prompt

class TestGeneratePrompt:
    
    def test_generate_claude_prompt_default_project(self, temp_knowledge_file):
        """Test Claude prompt generation with default project"""
        result = generate_prompt("claude", knowledge_file=temp_knowledge_file)
        
        assert "テストプロジェクト" in result
        assert "初期設計完了" in result
        assert "メモリリークが発生" in result
        assert "テストカバレッジ90%以上" in result
        assert "Claude用" in result
    
    def test_generate_copilot_prompt_default_project(self, temp_knowledge_file):
        """Test Copilot prompt generation with default project"""
        result = generate_prompt("copilot", knowledge_file=temp_knowledge_file)
        
        assert "テストプロジェクト" in result
        assert "初期設計完了" in result
        assert "メモリリークが発生" in result
        assert "テストカバレッジ90%以上" in result
        assert "Copilot用" in result
    
    def test_generate_prompt_specific_project(self, temp_knowledge_file):
        """Test prompt generation for specific project"""
        result = generate_prompt("claude", "テストプロジェクト", temp_knowledge_file)
        
        assert "テストプロジェクト" in result
        assert "初期設計完了" in result
    
    def test_generate_prompt_nonexistent_project(self, temp_knowledge_file):
        """Test prompt generation for non-existent project (should use default)"""
        result = generate_prompt("claude", "存在しないプロジェクト", temp_knowledge_file)
        
        # Should fall back to first project
        assert "テストプロジェクト" in result
    
    def test_generate_prompt_file_not_found(self):
        """Test error handling when knowledge file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            generate_prompt("claude", knowledge_file="nonexistent.json")
    
    def test_generate_prompt_invalid_json(self):
        """Test error handling for invalid JSON"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                generate_prompt("claude")
    
    def test_generate_prompt_missing_template(self, temp_knowledge_file):
        """Test error handling for missing template"""
        with pytest.raises(Exception):  # jinja2.exceptions.TemplateNotFound
            generate_prompt("unsupported_ai", knowledge_file=temp_knowledge_file)
    
    def test_generate_prompt_empty_knowledge_file(self):
        """Test error handling for empty knowledge file"""
        with patch("builtins.open", mock_open(read_data="{}")):
            with pytest.raises(KeyError):
                generate_prompt("claude")
    
    def test_generate_prompt_malformed_project_structure(self):
        """Test error handling for malformed project structure"""
        malformed_data = {
            "projects": [
                {
                    "name": "test",
                    # Missing required fields
                }
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(malformed_data))):
            with pytest.raises(KeyError):
                generate_prompt("claude")

class TestPromptContent:
    
    def test_prompt_contains_all_sections(self, temp_knowledge_file):
        """Test that generated prompt contains all expected sections"""
        result = generate_prompt("claude", knowledge_file=temp_knowledge_file)
        
        # Check for all major sections
        assert "設計経緯" in result or "設計履歴" in result
        assert "ルール" in result or "規則" in result
        assert "バグ" in result or "注意" in result
        assert "プロジェクト" in result
    
    def test_prompt_formatting_consistency(self, temp_knowledge_file):
        """Test that prompt formatting is consistent"""
        claude_result = generate_prompt("claude", knowledge_file=temp_knowledge_file)
        copilot_result = generate_prompt("copilot", knowledge_file=temp_knowledge_file)
        
        # Both should contain the same core information
        assert "テストプロジェクト" in claude_result
        assert "テストプロジェクト" in copilot_result
        assert "初期設計完了" in claude_result
        assert "初期設計完了" in copilot_result
    
    def test_prompt_date_formatting(self, temp_knowledge_file):
        """Test that dates are properly formatted in prompts"""
        result = generate_prompt("claude", knowledge_file=temp_knowledge_file)
        
        # Check for proper date format
        assert "2025-01-01" in result
        assert "2025-01-15" in result
        assert "2025-01-20" in result
```

## Integration Testing

### CLI Integration Tests (`test_cli.py`)

```python
import pytest
import subprocess
import tempfile
import json
import os

class TestCLI:
    
    def test_cli_claude_basic(self, temp_knowledge_file):
        """Test basic Claude prompt generation via CLI"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--ai", "claude",
            "--knowledge", temp_knowledge_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode == 0
        assert "テストプロジェクト" in result.stdout
        assert "Claude用" in result.stdout
    
    def test_cli_copilot_basic(self, temp_knowledge_file):
        """Test basic Copilot prompt generation via CLI"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--ai", "copilot",
            "--knowledge", temp_knowledge_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode == 0
        assert "テストプロジェクト" in result.stdout
        assert "Copilot用" in result.stdout
    
    def test_cli_with_output_file(self, temp_knowledge_file):
        """Test CLI with output file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            result = subprocess.run([
                "python", "prompt_generator.py",
                "--ai", "claude",
                "--knowledge", temp_knowledge_file,
                "--output", output_file
            ], capture_output=True, text=True, encoding='utf-8')
            
            assert result.returncode == 0
            assert os.path.exists(output_file)
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "テストプロジェクト" in content
                assert "Claude用" in content
        
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_cli_specific_project(self, temp_knowledge_file):
        """Test CLI with specific project"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--ai", "claude",
            "--project", "テストプロジェクト",
            "--knowledge", temp_knowledge_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode == 0
        assert "テストプロジェクト" in result.stdout
    
    def test_cli_invalid_ai_type(self, temp_knowledge_file):
        """Test CLI with invalid AI type"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--ai", "invalid_ai",
            "--knowledge", temp_knowledge_file
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower()
    
    def test_cli_missing_knowledge_file(self):
        """Test CLI with missing knowledge file"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--ai", "claude",
            "--knowledge", "nonexistent.json"
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode != 0
    
    def test_cli_help(self):
        """Test CLI help output"""
        result = subprocess.run([
            "python", "prompt_generator.py",
            "--help"
        ], capture_output=True, text=True, encoding='utf-8')
        
        assert result.returncode == 0
        assert "--ai" in result.stdout
        assert "--project" in result.stdout
        assert "--knowledge" in result.stdout
        assert "--output" in result.stdout
```

## Template Testing

### Template Validation Tests (`test_templates.py`)

```python
import pytest
from jinja2 import Environment, FileSystemLoader, Template
import os

class TestTemplates:
    
    def test_claude_template_exists(self):
        """Test that Claude template file exists"""
        assert os.path.exists("claude_prompt.md.j2")
    
    def test_copilot_template_exists(self):
        """Test that Copilot template file exists"""
        assert os.path.exists("copilot_prompt.md.j2")
    
    def test_claude_template_syntax(self):
        """Test Claude template syntax is valid"""
        with open("claude_prompt.md.j2", 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Should not raise an exception
        template = Template(template_content)
        assert template is not None
    
    def test_copilot_template_syntax(self):
        """Test Copilot template syntax is valid"""
        with open("copilot_prompt.md.j2", 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Should not raise an exception
        template = Template(template_content)
        assert template is not None
    
    def test_template_rendering(self, sample_knowledge):
        """Test template rendering with sample data"""
        project = sample_knowledge["projects"][0]
        
        # Test Claude template
        with open("claude_prompt.md.j2", 'r', encoding='utf-8') as f:
            claude_template = Template(f.read())
        
        claude_result = claude_template.render(
            project_name=project["name"],
            design_history=project["design_history"],
            bug_reports=project["bug_reports"],
            rules=project["rules"],
            prompts=project["prompts"]
        )
        
        assert project["name"] in claude_result
        assert project["design_history"][0]["summary"] in claude_result
        assert project["bug_reports"][0]["problem"] in claude_result
        assert project["rules"][0] in claude_result
        
        # Test Copilot template
        with open("copilot_prompt.md.j2", 'r', encoding='utf-8') as f:
            copilot_template = Template(f.read())
        
        copilot_result = copilot_template.render(
            project_name=project["name"],
            design_history=project["design_history"],
            bug_reports=project["bug_reports"],
            rules=project["rules"],
            prompts=project["prompts"]
        )
        
        assert project["name"] in copilot_result
        assert project["design_history"][0]["summary"] in copilot_result
        assert project["bug_reports"][0]["problem"] in copilot_result
        assert project["rules"][0] in copilot_result
    
    def test_template_empty_data(self):
        """Test template rendering with empty data"""
        empty_data = {
            "project_name": "Empty Project",
            "design_history": [],
            "bug_reports": [],
            "rules": [],
            "prompts": []
        }
        
        # Should not crash with empty data
        with open("claude_prompt.md.j2", 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        result = template.render(**empty_data)
        assert "Empty Project" in result
        assert result is not None
    
    def test_template_special_characters(self):
        """Test template rendering with special characters"""
        special_data = {
            "project_name": "プロジェクト名<>&\"'",
            "design_history": [{"date": "2025-01-01", "summary": "特殊文字テスト<>&\"'"}],
            "bug_reports": [{"date": "2025-01-02", "problem": "バグ報告<>&\"'"}],
            "rules": ["ルール<>&\"'"],
            "prompts": [{"date": "2025-01-03", "prompt": "プロンプト<>&\"'"}]
        }
        
        with open("claude_prompt.md.j2", 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        result = template.render(**special_data)
        assert "プロジェクト名<>&\"'" in result
        assert "特殊文字テスト<>&\"'" in result
```

## Error Handling Testing

### Error Scenarios Tests (`test_error_handling.py`)

```python
import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from prompt_generator import generate_prompt

class TestErrorHandling:
    
    def test_file_permission_error(self):
        """Test handling of file permission errors"""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                generate_prompt("claude")
    
    def test_corrupted_json_file(self):
        """Test handling of corrupted JSON files"""
        corrupted_json = '{"projects": [{"name": "test", "design_history": [{'
        
        with patch("builtins.open", mock_open(read_data=corrupted_json)):
            with pytest.raises(json.JSONDecodeError):
                generate_prompt("claude")
    
    def test_missing_projects_key(self):
        """Test handling of missing projects key"""
        invalid_data = {"invalid_key": "value"}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(invalid_data))):
            with pytest.raises(KeyError):
                generate_prompt("claude")
    
    def test_empty_projects_array(self):
        """Test handling of empty projects array"""
        empty_projects = {"projects": []}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(empty_projects))):
            with pytest.raises(IndexError):
                generate_prompt("claude")
    
    def test_invalid_project_structure(self):
        """Test handling of invalid project structure"""
        invalid_project = {
            "projects": [
                {
                    "name": "test"
                    # Missing required fields
                }
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(invalid_project))):
            with pytest.raises(KeyError):
                generate_prompt("claude")
    
    def test_unicode_handling(self):
        """Test proper Unicode handling"""
        unicode_data = {
            "projects": [
                {
                    "name": "プロジェクト名🚀",
                    "design_history": [{"date": "2025-01-01", "summary": "設計変更🔧"}],
                    "bug_reports": [{"date": "2025-01-02", "problem": "バグ発生❌"}],
                    "rules": ["ルール📋"],
                    "prompts": [{"date": "2025-01-03", "prompt": "プロンプト💬"}]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(unicode_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        try:
            result = generate_prompt("claude", knowledge_file=temp_file)
            assert "プロジェクト名🚀" in result
            assert "設計変更🔧" in result
            assert "バグ発生❌" in result
        finally:
            os.unlink(temp_file)
```

## Performance Testing

### Performance Tests (`test_performance.py`)

```python
import pytest
import time
import json
import tempfile
from prompt_generator import generate_prompt

class TestPerformance:
    
    def test_large_knowledge_file_performance(self):
        """Test performance with large knowledge file"""
        # Create large knowledge file
        large_data = {
            "projects": []
        }
        
        # Add 100 projects with extensive data
        for i in range(100):
            project = {
                "name": f"プロジェクト{i}",
                "design_history": [
                    {"date": f"2025-{j:02d}-01", "summary": f"設計変更{j}"}
                    for j in range(1, 13)  # 12 months
                ],
                "bug_reports": [
                    {"date": f"2025-{j:02d}-15", "problem": f"バグ報告{j}"}
                    for j in range(1, 13)  # 12 months
                ],
                "rules": [f"ルール{k}" for k in range(10)],
                "prompts": [
                    {"date": f"2025-{j:02d}-10", "prompt": f"プロンプト{j}"}
                    for j in range(1, 13)  # 12 months
                ]
            }
            large_data["projects"].append(project)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(large_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        try:
            start_time = time.time()
            result = generate_prompt("claude", knowledge_file=temp_file)
            end_time = time.time()
            
            # Should complete within 5 seconds
            assert end_time - start_time < 5.0
            assert "プロジェクト0" in result  # Should use first project
        finally:
            import os
            os.unlink(temp_file)
    
    def test_multiple_prompt_generation_performance(self, temp_knowledge_file):
        """Test performance of multiple prompt generations"""
        start_time = time.time()
        
        # Generate 50 prompts
        for i in range(50):
            ai_type = "claude" if i % 2 == 0 else "copilot"
            result = generate_prompt(ai_type, knowledge_file=temp_knowledge_file)
            assert result is not None
        
        end_time = time.time()
        
        # Should complete within 10 seconds
        assert end_time - start_time < 10.0
    
    def test_memory_usage(self, temp_knowledge_file):
        """Test memory usage doesn't grow excessively"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Generate many prompts
        for i in range(100):
            ai_type = "claude" if i % 2 == 0 else "copilot"
            result = generate_prompt(ai_type, knowledge_file=temp_knowledge_file)
            assert result is not None
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory usage should be reasonable (less than 50MB)
        assert peak < 50 * 1024 * 1024  # 50MB in bytes
```

## Test Data Management

### Test Fixtures (`fixtures/test_knowledge.json`)

```json
{
  "projects": [
    {
      "name": "テストプロジェクト1",
      "design_history": [
        {
          "date": "2025-01-01",
          "summary": "プロジェクト開始"
        },
        {
          "date": "2025-01-15",
          "summary": "アーキテクチャ決定"
        }
      ],
      "bug_reports": [
        {
          "date": "2025-01-20",
          "problem": "初期バグ発見"
        }
      ],
      "rules": [
        "テストファースト開発",
        "コードレビュー必須"
      ],
      "prompts": [
        {
          "date": "2025-01-10",
          "prompt": "初期プロンプト"
        }
      ]
    },
    {
      "name": "テストプロジェクト2",
      "design_history": [
        {
          "date": "2025-02-01",
          "summary": "第2プロジェクト開始"
        }
      ],
      "bug_reports": [],
      "rules": [
        "セキュリティ重視"
      ],
      "prompts": []
    }
  ]
}
```

## Continuous Testing

### GitHub Actions Test Workflow (`.github/workflows/test.yml`)

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-mock pytest-cov
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=prompt_generator --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Test CLI functionality
      run: |
        python prompt_generator.py --ai claude --help
        python prompt_generator.py --ai copilot --help
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_prompt_generator.py

# Run specific test class
pytest tests/unit/test_prompt_generator.py::TestGeneratePrompt

# Run specific test method
pytest tests/unit/test_prompt_generator.py::TestGeneratePrompt::test_generate_claude_prompt_default_project
```

### Coverage Testing

```bash
# Run tests with coverage
pytest --cov=prompt_generator

# Generate HTML coverage report
pytest --cov=prompt_generator --cov-report=html

# Generate XML coverage report
pytest --cov=prompt_generator --cov-report=xml
```

### Performance Testing

```bash
# Run only performance tests
pytest tests/performance/ -v

# Run with timing information
pytest --durations=10
```

## Test Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Fixtures**: Use fixtures for common test data and setup
3. **Mocking**: Mock external dependencies and file operations
4. **Coverage**: Aim for high test coverage (>90%)
5. **Performance**: Include performance tests for critical paths
6. **Error Cases**: Test error handling and edge cases
7. **Documentation**: Document complex test scenarios

This comprehensive testing guide ensures the reliability and maintainability of the 現場AIプロンプト自動生成システム.