# 現場AIプロンプト自動生成システム

このリポジトリは、プロジェクト履歴や現場ナレッジを元に「AI指示プロンプト」を自動生成するための資産管理・自動化ツール集です。

## 使い方
1. `genba_ai_knowledge.json`または`リポジトリの履歴`を用意
2. `prompt_generator.py`でAI種別（copilot/claudeなど）とプロジェクトを選択して実行
3. 出力されたプロンプトをそのままAI（Copilot/Claude等）にコピペ

## 主要ファイル
- `prompt_generator.py`: 自動プロンプト生成スクリプト
- `templates/`: AI種別ごとのプロンプトテンプレート
- `.github/workflows/generate_prompt.yml`: Actions自動化（例）
