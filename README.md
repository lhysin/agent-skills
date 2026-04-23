# agent-skills

Skill repository distributed through `skills.sh`.

## Available skills

- `md-gen`: convert file paths, URLs, or raw content into consistently structured markdown documents using a standardized template.
- `confluence-docs`: publish and verify Confluence pages from local Markdown, Mermaid, and CLI-driven workflows.
- `clean-dead-code`: find, verify, and remove dead code with an evidence-driven and language-agnostic workflow.
- `go-cli-builder`: design and implement high-quality Go CLI tools following clig.dev guidelines.
- `springboot-scaffold`: generate Spring Boot project structure with domain (order), external integration (payment), and configuration files (build.gradle, application.yml).

## Install

```bash
npx skills add lhysin/agent-skills --skill md-gen -a claude-code -g -y

npx skills add lhysin/agent-skills --skill confluence-docs -a claude-code -g -y

npx skills add lhysin/agent-skills --skill clean-dead-code -a claude-code -g -y

npx skills add lhysin/agent-skills --skill go-cli-builder -a claude-code -y

npx skills add lhysin/agent-skills --skill springboot-scaffold -a claude-code -y
```
