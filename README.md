# agent-skills

Skill repository distributed through `skills.sh`.

## Available skills

- `confluence-docs`: publish and verify Confluence pages from local Markdown, Mermaid, and CLI-driven workflows.
- `clean-dead-code`: find, verify, and remove dead code with an evidence-driven and language-agnostic workflow.
- `go-cli-builder`: design and implement high-quality Go CLI tools following clig.dev guidelines.
- `springboot-scaffold`: mechanically generate and validate a Spring Boot project scaffold, including Gradle files, profiles, base packages, and optional order/payment sample code.

## Install

```bash
npx skills add lhysin/agent-skills --skill confluence-docs -a claude-code -g -y

npx skills add lhysin/agent-skills --skill clean-dead-code -a claude-code -g -y

npx skills add lhysin/agent-skills --skill go-cli-builder -a claude-code -y

npx skills add lhysin/agent-skills --skill springboot-scaffold -a claude-code -y
```
