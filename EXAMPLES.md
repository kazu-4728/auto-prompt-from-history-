# Usage Examples

This document provides comprehensive examples for using the 現場AIプロンプト自動生成システム in various scenarios.

## Table of Contents

1. [Basic Command Line Usage](#basic-command-line-usage)
2. [Programmatic Usage](#programmatic-usage)
3. [Custom Knowledge Files](#custom-knowledge-files)
4. [Template Customization](#template-customization)
5. [Integration Examples](#integration-examples)
6. [Batch Processing](#batch-processing)
7. [Error Handling](#error-handling)
8. [GitHub Actions Usage](#github-actions-usage)

## Basic Command Line Usage

### Example 1: Generate Claude Prompt (Default Project)

```bash
python prompt_generator.py --ai claude
```

**Output:**
```markdown
# Claude用 現場AI指示テンプレート

プロジェクト名: 材料配置シュミレータ

設計経緯・目的:
- 2025-06-01: アルゴリズムA→Bへ変更

現場ルール:
- ユーザー入力のギャップは厳守すること

バグ・注意事項:
- 2025-06-12: 材料が追加できないバグ発生

必ず上記現場ノウハウを反映して作業してください。
```

### Example 2: Generate Copilot Prompt with Output File

```bash
python prompt_generator.py --ai copilot --output copilot_instructions.md
```

**Output File (copilot_instructions.md):**
```markdown
# Copilot用 現場AI指示テンプレート

## プロジェクト名: 材料配置シュミレータ

### 設計経緯・目的
- 2025-06-01: アルゴリズムA→Bへ変更

### 現場ルール
- ユーザー入力のギャップは厳守すること

### バグ・注意点
- 2025-06-12: 材料が追加できないバグ発生

### 指示
- 添付JSONに従い、現場ノウハウを必ず反映して作業してください。
```

### Example 3: Use Custom Knowledge File

```bash
python prompt_generator.py --ai claude --knowledge my_project_knowledge.json --output custom_prompt.md
```

## Programmatic Usage

### Example 1: Basic Function Call

```python
from prompt_generator import generate_prompt

# Generate prompt for Claude
claude_prompt = generate_prompt("claude")
print(claude_prompt)

# Generate prompt for Copilot
copilot_prompt = generate_prompt("copilot")
print(copilot_prompt)
```

### Example 2: Specific Project Selection

```python
from prompt_generator import generate_prompt

# Generate prompt for specific project
prompt = generate_prompt(
    ai_type="claude",
    project_name="材料配置シュミレータ"
)

# Save to file
with open("specific_project_prompt.md", "w", encoding="utf-8") as f:
    f.write(prompt)
```

### Example 3: Multiple Prompts Generation

```python
from prompt_generator import generate_prompt
import json

# Load knowledge file to get all projects
with open("genba_ai_knowledge.json", "r", encoding="utf-8") as f:
    knowledge = json.load(f)

# Generate prompts for all projects
for project in knowledge["projects"]:
    project_name = project["name"]
    
    # Generate Claude prompt
    claude_prompt = generate_prompt("claude", project_name)
    with open(f"claude_{project_name}.md", "w", encoding="utf-8") as f:
        f.write(claude_prompt)
    
    # Generate Copilot prompt
    copilot_prompt = generate_prompt("copilot", project_name)
    with open(f"copilot_{project_name}.md", "w", encoding="utf-8") as f:
        f.write(copilot_prompt)
    
    print(f"Generated prompts for {project_name}")
```

## Custom Knowledge Files

### Example 1: Create Custom Knowledge File

```python
import json

# Create custom knowledge structure
custom_knowledge = {
    "projects": [
        {
            "name": "Webアプリケーション開発",
            "design_history": [
                {
                    "date": "2025-01-01",
                    "summary": "React + TypeScript構成に決定"
                },
                {
                    "date": "2025-01-15",
                    "summary": "APIはREST形式で実装"
                }
            ],
            "bug_reports": [
                {
                    "date": "2025-01-20",
                    "problem": "ログイン機能でセッション切れが発生"
                }
            ],
            "rules": [
                "TypeScriptの型定義は必須",
                "APIレスポンスは必ずエラーハンドリングを含める",
                "コンポーネントはReusableに設計する"
            ],
            "prompts": [
                {
                    "date": "2025-01-10",
                    "prompt": "ユーザー認証機能をJWTで実装してください"
                }
            ]
        }
    ]
}

# Save custom knowledge file
with open("webapp_knowledge.json", "w", encoding="utf-8") as f:
    json.dump(custom_knowledge, f, ensure_ascii=False, indent=2)

print("Custom knowledge file created: webapp_knowledge.json")
```

### Example 2: Use Custom Knowledge File

```python
from prompt_generator import generate_prompt

# Generate prompt using custom knowledge
prompt = generate_prompt(
    ai_type="claude",
    project_name="Webアプリケーション開発",
    knowledge_file="webapp_knowledge.json"
)

print(prompt)
```

## Template Customization

### Example 1: Create Custom Template

Create a new template file `chatgpt_prompt.md.j2`:

```jinja2
# ChatGPT用 現場AI指示テンプレート

**プロジェクト**: {{ project_name }}

## 📋 設計履歴
{% for item in design_history %}
- **{{ item.date }}**: {{ item.summary }}
{% endfor %}

## ⚠️ 注意事項・バグ
{% for bug in bug_reports %}
- **{{ bug.date }}**: {{ bug.problem }}
{% endfor %}

## 📏 現場ルール
{% for rule in rules %}
- {{ rule }}
{% endfor %}

## 🎯 指示
上記の現場ノウハウと制約を必ず考慮して作業を行ってください。
```

### Example 2: Modify Script for Custom Template

```python
# Modified prompt_generator.py to support ChatGPT
import json
import argparse
from jinja2 import Environment, FileSystemLoader

def generate_prompt(ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json"):
    with open(knowledge_file, encoding="utf-8") as f:
        data = json.load(f)
    
    projects = data["projects"]
    project = projects[0]
    
    if project_name:
        for p in projects:
            if p["name"] == project_name:
                project = p
                break
    
    env = Environment(loader=FileSystemLoader("./templates"), autoescape=False)
    template = env.get_template(f"{ai_type}_prompt.md.j2")
    
    prompt = template.render(
        project_name=project["name"],
        design_history=project["design_history"],
        bug_reports=project["bug_reports"],
        rules=project["rules"],
        prompts=project["prompts"]
    )
    
    return prompt

# Usage with custom template
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", choices=["copilot", "claude", "chatgpt"], required=True)
    parser.add_argument("--project", help="プロジェクト名")
    parser.add_argument("--knowledge", default="genba_ai_knowledge.json")
    parser.add_argument("--output", help="出力ファイル名")
    
    args = parser.parse_args()
    prompt = generate_prompt(args.ai, args.project, args.knowledge)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"出力しました: {args.output}")
    else:
        print(prompt)
```

## Integration Examples

### Example 1: Web API Integration

```python
import requests
from prompt_generator import generate_prompt

class PromptAPI:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def send_prompt(self, ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json"):
        # Generate prompt
        prompt = generate_prompt(ai_type, project_name, knowledge_file)
        
        # Send to API
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "prompt": prompt,
                "ai_type": ai_type,
                "project": project_name
            },
            headers={"Content-Type": "application/json"}
        )
        
        return response.json()

# Usage
api = PromptAPI("https://api.example.com")
result = api.send_prompt("claude", "材料配置シュミレータ")
print(result)
```

### Example 2: Slack Bot Integration

```python
import slack_sdk
from prompt_generator import generate_prompt

class SlackPromptBot:
    def __init__(self, token):
        self.client = slack_sdk.WebClient(token=token)
    
    def send_prompt_to_channel(self, channel, ai_type, project_name=None):
        # Generate prompt
        prompt = generate_prompt(ai_type, project_name)
        
        # Send to Slack
        response = self.client.chat_postMessage(
            channel=channel,
            text=f"Generated {ai_type} prompt for {project_name or 'default project'}:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{prompt}```"
                    }
                }
            ]
        )
        
        return response

# Usage
bot = SlackPromptBot("xoxb-your-token")
bot.send_prompt_to_channel("#dev-team", "claude", "材料配置シュミレータ")
```

### Example 3: Database Integration

```python
import sqlite3
from datetime import datetime
from prompt_generator import generate_prompt

class PromptDatabase:
    def __init__(self, db_path="prompts.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ai_type TEXT NOT NULL,
                project_name TEXT,
                prompt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prompt(self, ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json"):
        # Generate prompt
        prompt = generate_prompt(ai_type, project_name, knowledge_file)
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prompts (ai_type, project_name, prompt)
            VALUES (?, ?, ?)
        ''', (ai_type, project_name, prompt))
        
        conn.commit()
        conn.close()
        
        return prompt
    
    def get_prompts(self, ai_type=None, project_name=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM prompts WHERE 1=1"
        params = []
        
        if ai_type:
            query += " AND ai_type = ?"
            params.append(ai_type)
        
        if project_name:
            query += " AND project_name = ?"
            params.append(project_name)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        return results

# Usage
db = PromptDatabase()
prompt = db.save_prompt("claude", "材料配置シュミレータ")
print(f"Saved prompt: {prompt[:100]}...")

# Retrieve prompts
prompts = db.get_prompts(ai_type="claude")
print(f"Found {len(prompts)} Claude prompts")
```

## Batch Processing

### Example 1: Process Multiple Projects

```python
import os
from prompt_generator import generate_prompt
import json

def batch_generate_prompts(knowledge_file="genba_ai_knowledge.json", output_dir="prompts"):
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load knowledge file
    with open(knowledge_file, "r", encoding="utf-8") as f:
        knowledge = json.load(f)
    
    ai_types = ["claude", "copilot"]
    
    for project in knowledge["projects"]:
        project_name = project["name"]
        
        # Create project directory
        project_dir = os.path.join(output_dir, project_name.replace(" ", "_"))
        os.makedirs(project_dir, exist_ok=True)
        
        for ai_type in ai_types:
            # Generate prompt
            prompt = generate_prompt(ai_type, project_name, knowledge_file)
            
            # Save to file
            filename = f"{ai_type}_prompt.md"
            filepath = os.path.join(project_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(prompt)
            
            print(f"Generated {filepath}")

# Usage
batch_generate_prompts()
```

### Example 2: Scheduled Prompt Generation

```python
import schedule
import time
from datetime import datetime
from prompt_generator import generate_prompt

def scheduled_prompt_generation():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    ai_types = ["claude", "copilot"]
    
    for ai_type in ai_types:
        prompt = generate_prompt(ai_type)
        filename = f"{ai_type}_prompt_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        print(f"Generated scheduled prompt: {filename}")

# Schedule prompt generation every hour
schedule.every().hour.do(scheduled_prompt_generation)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
```

## Error Handling

### Example 1: Comprehensive Error Handling

```python
import json
import logging
from prompt_generator import generate_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_generate_prompt(ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json"):
    try:
        prompt = generate_prompt(ai_type, project_name, knowledge_file)
        logger.info(f"Successfully generated {ai_type} prompt for {project_name or 'default project'}")
        return prompt
    
    except FileNotFoundError as e:
        logger.error(f"Knowledge file not found: {e}")
        return None
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in knowledge file: {e}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

# Usage with error handling
prompt = safe_generate_prompt("claude", "材料配置シュミレータ")
if prompt:
    print(prompt)
else:
    print("Failed to generate prompt")
```

### Example 2: Validation Function

```python
import json
import os

def validate_knowledge_file(knowledge_file):
    """Validate knowledge file structure"""
    errors = []
    
    # Check if file exists
    if not os.path.exists(knowledge_file):
        errors.append(f"File not found: {knowledge_file}")
        return errors
    
    try:
        with open(knowledge_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")
        return errors
    
    # Check required structure
    if "projects" not in data:
        errors.append("Missing 'projects' key")
        return errors
    
    if not isinstance(data["projects"], list):
        errors.append("'projects' must be an array")
        return errors
    
    # Validate each project
    for i, project in enumerate(data["projects"]):
        required_fields = ["name", "design_history", "bug_reports", "rules", "prompts"]
        
        for field in required_fields:
            if field not in project:
                errors.append(f"Project {i}: Missing '{field}' field")
        
        # Validate design_history structure
        if "design_history" in project:
            for j, history in enumerate(project["design_history"]):
                if not isinstance(history, dict):
                    errors.append(f"Project {i}, design_history {j}: Must be object")
                elif "date" not in history or "summary" not in history:
                    errors.append(f"Project {i}, design_history {j}: Missing date or summary")
    
    return errors

# Usage
errors = validate_knowledge_file("genba_ai_knowledge.json")
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"- {error}")
else:
    print("Knowledge file is valid")
    prompt = generate_prompt("claude")
```

## GitHub Actions Usage

### Example 1: Custom Workflow

Create `.github/workflows/custom-prompt-generation.yml`:

```yaml
name: Custom Prompt Generation

on:
  workflow_dispatch:
    inputs:
      ai_type:
        description: 'AI Type'
        required: true
        default: 'claude'
        type: choice
        options:
          - claude
          - copilot
      project_name:
        description: 'Project Name (optional)'
        required: false
        type: string
      knowledge_file:
        description: 'Knowledge File Path'
        required: false
        default: 'genba_ai_knowledge.json'
        type: string

jobs:
  generate-prompt:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate Prompt
        run: |
          if [ -n "${{ github.event.inputs.project_name }}" ]; then
            python prompt_generator.py \
              --ai ${{ github.event.inputs.ai_type }} \
              --project "${{ github.event.inputs.project_name }}" \
              --knowledge ${{ github.event.inputs.knowledge_file }} \
              --output generated_prompt.md
          else
            python prompt_generator.py \
              --ai ${{ github.event.inputs.ai_type }} \
              --knowledge ${{ github.event.inputs.knowledge_file }} \
              --output generated_prompt.md
          fi
      
      - name: Upload Generated Prompt
        uses: actions/upload-artifact@v4
        with:
          name: generated-prompt-${{ github.event.inputs.ai_type }}
          path: generated_prompt.md
      
      - name: Comment on Issue (if triggered by issue)
        if: github.event_name == 'issues'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const prompt = fs.readFileSync('generated_prompt.md', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Generated ${{ github.event.inputs.ai_type }} Prompt\n\n\`\`\`markdown\n${prompt}\n\`\`\``
            });
```

### Example 2: Multi-Environment Deployment

```yaml
name: Deploy Prompts to Multiple Environments

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  generate-and-deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [development, staging, production]
        ai_type: [claude, copilot]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Generate Prompt
        run: |
          python prompt_generator.py \
            --ai ${{ matrix.ai_type }} \
            --knowledge knowledge_${{ matrix.environment }}.json \
            --output ${{ matrix.environment }}_${{ matrix.ai_type }}_prompt.md
      
      - name: Deploy to Environment
        run: |
          echo "Deploying ${{ matrix.ai_type }} prompt to ${{ matrix.environment }}"
          # Add your deployment logic here
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: prompts-${{ matrix.environment }}
          path: ${{ matrix.environment }}_*_prompt.md
```

These examples demonstrate the flexibility and power of the 現場AIプロンプト自動生成システム across various use cases and integration scenarios.