# API Documentation - 現場AIプロンプト自動生成システム

## Overview

The 現場AIプロンプト自動生成システム (Genba AI Prompt Auto-Generation System) is a Python-based tool that automatically generates AI instruction prompts based on project history and field knowledge. It supports multiple AI platforms including Copilot and Claude.

## Table of Contents

1. [Core API Functions](#core-api-functions)
2. [Command Line Interface](#command-line-interface)
3. [Data Structures](#data-structures)
4. [Template System](#template-system)
5. [GitHub Actions Integration](#github-actions-integration)
6. [Usage Examples](#usage-examples)
7. [Configuration](#configuration)

## Core API Functions

### `generate_prompt(ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json")`

**Description**: Main function that generates AI-specific prompts based on project knowledge and history.

**Parameters**:
- `ai_type` (str, required): The target AI platform. Supported values: `"copilot"`, `"claude"`
- `project_name` (str, optional): Name of the specific project to generate prompt for. If not provided, uses the first project in the knowledge file
- `knowledge_file` (str, optional): Path to the knowledge JSON file. Default: `"genba_ai_knowledge.json"`

**Returns**: 
- `str`: Generated prompt text formatted for the specified AI platform

**Raises**:
- `FileNotFoundError`: If the knowledge file doesn't exist
- `json.JSONDecodeError`: If the knowledge file contains invalid JSON
- `jinja2.exceptions.TemplateNotFound`: If the template file for the specified AI type doesn't exist

**Example**:
```python
from prompt_generator import generate_prompt

# Generate Claude prompt for default project
claude_prompt = generate_prompt("claude")

# Generate Copilot prompt for specific project
copilot_prompt = generate_prompt("copilot", project_name="材料配置シュミレータ")

# Use custom knowledge file
custom_prompt = generate_prompt("claude", knowledge_file="custom_knowledge.json")
```

## Command Line Interface

### Main Script: `prompt_generator.py`

**Usage**: `python prompt_generator.py [OPTIONS]`

**Arguments**:

| Argument | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `--ai` | choice | Yes | AI platform type (`copilot` or `claude`) | `--ai claude` |
| `--project` | string | No | Project name to generate prompt for | `--project "材料配置シュミレータ"` |
| `--knowledge` | string | No | Path to knowledge file (default: `genba_ai_knowledge.json`) | `--knowledge custom.json` |
| `--output` | string | No | Output file path (default: stdout) | `--output output.md` |

**Exit Codes**:
- `0`: Success
- `1`: Error (file not found, invalid JSON, etc.)

**Examples**:
```bash
# Generate Claude prompt and output to console
python prompt_generator.py --ai claude

# Generate Copilot prompt for specific project and save to file
python prompt_generator.py --ai copilot --project "材料配置シュミレータ" --output copilot_prompt.md

# Use custom knowledge file
python prompt_generator.py --ai claude --knowledge custom_knowledge.json --output claude_output.md
```

## Data Structures

### Knowledge File Structure (`genba_ai_knowledge.json`)

The knowledge file follows this JSON schema:

```json
{
  "projects": [
    {
      "name": "string",
      "design_history": [
        {
          "date": "YYYY-MM-DD",
          "summary": "string"
        }
      ],
      "bug_reports": [
        {
          "date": "YYYY-MM-DD", 
          "problem": "string"
        }
      ],
      "rules": ["string"],
      "prompts": [
        {
          "date": "YYYY-MM-DD",
          "prompt": "string"
        }
      ]
    }
  ]
}
```

**Field Descriptions**:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `projects` | array | Array of project objects | Yes |
| `projects[].name` | string | Project name identifier | Yes |
| `projects[].design_history` | array | Historical design decisions and changes | Yes |
| `projects[].design_history[].date` | string | Date of design change (ISO format) | Yes |
| `projects[].design_history[].summary` | string | Summary of the design change | Yes |
| `projects[].bug_reports` | array | Known bugs and issues | Yes |
| `projects[].bug_reports[].date` | string | Date bug was reported (ISO format) | Yes |
| `projects[].bug_reports[].problem` | string | Description of the bug/problem | Yes |
| `projects[].rules` | array | Project-specific rules and guidelines | Yes |
| `projects[].prompts` | array | Historical prompts used for the project | Yes |
| `projects[].prompts[].date` | string | Date prompt was created (ISO format) | Yes |
| `projects[].prompts[].prompt` | string | The actual prompt text | Yes |

**Example**:
```json
{
  "projects": [
    {
      "name": "材料配置シュミレータ",
      "design_history": [
        {
          "date": "2025-06-01",
          "summary": "アルゴリズムA→Bへ変更"
        }
      ],
      "bug_reports": [
        {
          "date": "2025-06-12",
          "problem": "材料が追加できないバグ発生"
        }
      ],
      "rules": [
        "ユーザー入力のギャップは厳守すること"
      ],
      "prompts": [
        {
          "date": "2025-06-10",
          "prompt": "材料サイズ、間隔、アルゴリズムを指定して配置してください。"
        }
      ]
    }
  ]
}
```

## Template System

The system uses Jinja2 templates to generate AI-specific prompts. Templates are stored as `.md.j2` files.

### Template Variables

All templates receive the following variables:

| Variable | Type | Description |
|----------|------|-------------|
| `project_name` | string | Name of the project |
| `design_history` | array | List of design history objects |
| `bug_reports` | array | List of bug report objects |
| `rules` | array | List of project rules |
| `prompts` | array | List of historical prompts |

### Available Templates

#### 1. Claude Template (`claude_prompt.md.j2`)

**Purpose**: Generates prompts optimized for Claude AI

**Output Format**: Simple markdown with clear sections

**Template Structure**:
```jinja2
# Claude用 現場AI指示テンプレート

プロジェクト名: {{ project_name }}

設計経緯・目的:
{% for item in design_history %}
- {{ item.date }}: {{ item.summary }}
{% endfor %}

現場ルール:
{% for rule in rules %}
- {{ rule }}
{% endfor %}

バグ・注意事項:
{% for bug in bug_reports %}
- {{ bug.date }}: {{ bug.problem }}
{% endfor %}

必ず上記現場ノウハウを反映して作業してください。
```

#### 2. Copilot Template (`copilot_prompt.md.j2`)

**Purpose**: Generates prompts optimized for GitHub Copilot

**Output Format**: Structured markdown with headers

**Template Structure**:
```jinja2
# Copilot用 現場AI指示テンプレート

## プロジェクト名: {{ project_name }}

### 設計経緯・目的
{% for item in design_history %}
- {{ item.date }}: {{ item.summary }}
{% endfor %}

### 現場ルール
{% for rule in rules %}
- {{ rule }}
{% endfor %}

### バグ・注意点
{% for bug in bug_reports %}
- {{ bug.date }}: {{ bug.problem }}
{% endfor %}

### 指示
- 添付JSONに従い、現場ノウハウを必ず反映して作業してください。
```

### Creating Custom Templates

To create a new template for a different AI platform:

1. Create a new file: `{ai_type}_prompt.md.j2`
2. Use Jinja2 syntax with the available template variables
3. Update the `--ai` argument choices in the script

**Example Custom Template**:
```jinja2
# Custom AI Template

Project: {{ project_name }}

## History
{% for item in design_history %}
{{ item.date }}: {{ item.summary }}
{% endfor %}

## Rules
{% for rule in rules %}
- {{ rule }}
{% endfor %}
```

## GitHub Actions Integration

### Workflow: `generate-prompt.yml`

**Purpose**: Automatically generates prompts on repository events

**Triggers**:
- Issues opened
- Pull requests opened or synchronized
- Push to main branch

**Steps**:
1. Checkout repository
2. Set up Python 3.11
3. Install dependencies
4. Generate Copilot prompt
5. Generate Claude prompt
6. Upload artifacts

**Artifacts**: 
- `copilot_prompt.md`
- `claude_prompt.md`

**Configuration**:
```yaml
name: Generate AI Prompt

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened, synchronize]
  push:
    branches:
      - main

jobs:
  prompt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate Copilot Prompt
        run: python prompt_generator.py --ai copilot --output copilot_prompt.md
      - name: Generate Claude Prompt
        run: python prompt_generator.py --ai claude --output claude_prompt.md
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: prompts
          path: |
            copilot_prompt.md
            claude_prompt.md
```

## Usage Examples

### Basic Usage

```bash
# Generate Claude prompt
python prompt_generator.py --ai claude

# Generate Copilot prompt and save to file
python prompt_generator.py --ai copilot --output my_prompt.md
```

### Advanced Usage

```bash
# Generate prompt for specific project
python prompt_generator.py --ai claude --project "材料配置シュミレータ"

# Use custom knowledge file
python prompt_generator.py --ai copilot --knowledge custom_knowledge.json --output custom_prompt.md
```

### Programmatic Usage

```python
import json
from prompt_generator import generate_prompt

# Load and modify knowledge data
with open("genba_ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# Add new project
new_project = {
    "name": "新プロジェクト",
    "design_history": [{"date": "2025-01-01", "summary": "プロジェクト開始"}],
    "bug_reports": [],
    "rules": ["新しいルール"],
    "prompts": []
}
knowledge["projects"].append(new_project)

# Save updated knowledge
with open("updated_knowledge.json", "w", encoding="utf-8") as f:
    json.dump(knowledge, f, ensure_ascii=False, indent=2)

# Generate prompt with updated knowledge
prompt = generate_prompt("claude", project_name="新プロジェクト", knowledge_file="updated_knowledge.json")
print(prompt)
```

### Integration with Other Tools

```python
# Example: Integration with web API
import requests
from prompt_generator import generate_prompt

def send_prompt_to_api(ai_type, project_name=None):
    prompt = generate_prompt(ai_type, project_name)
    
    response = requests.post("https://api.example.com/generate", {
        "prompt": prompt,
        "ai_type": ai_type
    })
    
    return response.json()

# Usage
result = send_prompt_to_api("claude", "材料配置シュミレータ")
```

## Configuration

### Environment Setup

**Python Version**: 3.11 or higher

**Dependencies**:
```txt
jinja2
```

**Installation**:
```bash
pip install -r requirements.txt
```

**Alternative (Conda)**:
```bash
conda env create -f environment.yml
conda activate genba-ai
```

### File Structure

```
project/
├── prompt_generator.py          # Main script
├── genba_ai_knowledge.json      # Knowledge database
├── claude_prompt.md.j2          # Claude template
├── copilot_prompt.md.j2         # Copilot template
├── requirements.txt             # Python dependencies
├── environment.yml              # Conda environment
├── .github/
│   └── workflows/
│       └── generate-prompt.yml  # GitHub Actions workflow
└── README.md                    # Project documentation
```

### Error Handling

The system includes comprehensive error handling:

**File Not Found**:
```python
try:
    prompt = generate_prompt("claude", knowledge_file="missing.json")
except FileNotFoundError as e:
    print(f"Knowledge file not found: {e}")
```

**Invalid JSON**:
```python
try:
    prompt = generate_prompt("claude")
except json.JSONDecodeError as e:
    print(f"Invalid JSON in knowledge file: {e}")
```

**Template Not Found**:
```python
try:
    prompt = generate_prompt("unsupported_ai")
except Exception as e:
    print(f"Template error: {e}")
```

## Best Practices

1. **Knowledge File Management**:
   - Keep knowledge files in version control
   - Use consistent date formats (YYYY-MM-DD)
   - Regularly update project history and rules

2. **Template Customization**:
   - Test templates with sample data
   - Keep templates focused on specific AI platforms
   - Use clear, structured formatting

3. **Automation**:
   - Use GitHub Actions for consistent prompt generation
   - Archive generated prompts as artifacts
   - Set up notifications for prompt updates

4. **Error Prevention**:
   - Validate JSON files before committing
   - Use descriptive project names
   - Include comprehensive error handling in custom integrations

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: [Errno 2] No such file or directory: 'genba_ai_knowledge.json'`
**Solution**: Ensure the knowledge file exists in the current directory or specify the correct path with `--knowledge`

**Issue**: `jinja2.exceptions.TemplateNotFound: claude_prompt.md.j2`
**Solution**: Ensure template files are in the correct location and have proper file extensions

**Issue**: `json.JSONDecodeError: Expecting property name enclosed in double quotes`
**Solution**: Validate JSON syntax in the knowledge file

### Debug Mode

To enable verbose output for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your code here
prompt = generate_prompt("claude")
```

## Contributing

When adding new features:

1. Update this documentation
2. Add appropriate error handling
3. Include usage examples
4. Test with various input scenarios
5. Update GitHub Actions workflow if needed

## License

This project is licensed under the terms specified in the LICENSE file.