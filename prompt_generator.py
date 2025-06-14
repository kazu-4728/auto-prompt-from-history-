import json
import argparse
from jinja2 import Environment, FileSystemLoader

def generate_prompt(ai_type, project_name=None, knowledge_file="genba_ai_knowledge.json"):
    with open(knowledge_file, encoding="utf-8") as f:
        data = json.load(f)
    projects = data["projects"]
    # プロジェクト指定なければ最初を選択
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", choices=["copilot", "claude"], required=True, help="AI種別")
    parser.add_argument("--project", help="プロジェクト名（省略可）")
    parser.add_argument("--knowledge", default="genba_ai_knowledge.json", help="ナレッジファイルパス")
    parser.add_argument("--output", help="出力ファイル名（省略時は標準出力）")
    args = parser.parse_args()
    prompt = generate_prompt(args.ai, args.project, args.knowledge)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"出力しました: {args.output}")
    else:
        print(prompt)
