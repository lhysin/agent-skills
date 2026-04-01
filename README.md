# agent-skills

Skill repository distributed through `skills.sh`.

## Available skills

- `confluence-docs`: publish and verify Confluence pages from local Markdown, Mermaid, and CLI-driven workflows.
- `clean-dead-code`: find, verify, and remove dead code with an evidence-driven and language-agnostic workflow.
- `go-cli-builder`: design and implement high-quality Go CLI tools following clig.dev guidelines.

## Install

```bash
npx skills add lhysin/agent-skills --skill confluence-docs -a claude-code -g -y

npx skills add lhysin/agent-skills --skill clean-dead-code -a claude-code -g -y

npx skills add lhysin/agent-skills --skill go-cli-builder -a claude-code -g -y
```
