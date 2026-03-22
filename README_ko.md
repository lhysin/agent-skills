# agent-skills

`skills.sh`로 배포하는 스킬 저장소입니다.

## 포함된 스킬

- `confluence-docs`: 로컬 Markdown, Mermaid, CLI 워크플로를 기준으로 Confluence 문서를 반영하고 검증하는 스킬입니다.
- `clean-dead-code`: 언어에 종속되지 않은 방식으로 데드 코드 후보를 찾고, 근거를 확인한 뒤 안전하게 제거하는 스킬입니다.

## 설치

```bash
npx skills add lhysin/agent-skills --skill confluence-docs -a claude-code -g -y

npx skills add lhysin/agent-skills --skill clean-dead-code -a claude-code -g -y
```
