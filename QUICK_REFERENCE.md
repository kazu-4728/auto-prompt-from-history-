# Quick Reference Guide

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate Claude prompt
python prompt_generator.py --ai claude

# Generate Copilot prompt and save
python prompt_generator.py --ai copilot --output copilot_prompt.md
```

## 📋 Command Line Options

| Option | Required | Description | Example |
|--------|----------|-------------|---------|
| `--ai` | ✅ | AI type (`copilot`, `claude`) | `--ai claude` |
| `--project` | ❌ | Project name | `--project "材料配置シュミレータ"` |
| `--knowledge` | ❌ | Knowledge file path | `--knowledge custom.json` |
| `--output` | ❌ | Output file | `--output prompt.md` |

## 🔧 API Function

```python
generate_prompt(ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json")
```

**Parameters:**
- `ai_type`: `"copilot"` or `"claude"`
- `project_name`: Optional project name
- `knowledge_file`: Path to JSON knowledge file

**Returns:** Generated prompt string

## 📄 Knowledge File Format

```json
{
  "projects": [
    {
      "name": "Project Name",
      "design_history": [
        {"date": "2025-01-01", "summary": "Design change"}
      ],
      "bug_reports": [
        {"date": "2025-01-02", "problem": "Bug description"}
      ],
      "rules": ["Rule 1", "Rule 2"],
      "prompts": [
        {"date": "2025-01-03", "prompt": "Previous prompt"}
      ]
    }
  ]
}
```

## 🎯 Common Use Cases

### 1. Basic Prompt Generation
```bash
python prompt_generator.py --ai claude
```

### 2. Specific Project
```bash
python prompt_generator.py --ai copilot --project "材料配置シュミレータ"
```

### 3. Custom Knowledge File
```bash
python prompt_generator.py --ai claude --knowledge my_project.json --output my_prompt.md
```

### 4. Programmatic Usage
```python
from prompt_generator import generate_prompt

# Generate prompt
prompt = generate_prompt("claude", "材料配置シュミレータ")
print(prompt)
```

## 🛠️ Template Variables

Available in all templates:
- `project_name`: Project name
- `design_history`: List of design changes
- `bug_reports`: List of known bugs
- `rules`: List of project rules
- `prompts`: List of historical prompts

## ⚡ GitHub Actions

Automatically generates prompts on:
- Issues opened
- Pull requests opened/updated
- Push to main branch

Artifacts: `copilot_prompt.md`, `claude_prompt.md`

## 🚨 Common Errors

| Error | Solution |
|-------|----------|
| `FileNotFoundError` | Check knowledge file path |
| `TemplateNotFound` | Ensure template files exist |
| `JSONDecodeError` | Validate JSON syntax |

## 📁 File Structure

```
project/
├── prompt_generator.py          # Main script
├── genba_ai_knowledge.json      # Knowledge database
├── claude_prompt.md.j2          # Claude template
├── copilot_prompt.md.j2         # Copilot template
├── requirements.txt             # Dependencies
└── .github/workflows/           # GitHub Actions
```

## 🔍 Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For detailed documentation, see `API_DOCUMENTATION.md`