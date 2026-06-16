# Code Convention Baseline

This file describes the convention audit currently bundled with `springboot-scaffold`.

## Source Status

This baseline was extracted from the local CJOS common v5 wiki on 2026-06-16.

Source root:

```text
/Users/lhysin/Development/workspace-cjos/nextstyle/wiki/business/platform/cjos-common-v5
```

Included source documents:

- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.1 코딩 컨벤션.md`
- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.2 ORM.md`
- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.3 API 개발 규칙.md`
- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.4 예외 처리 구현.md`
- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.5 로그 구현.md`
- `30. 표준 애플리케이션 개발 가이드/30.3 구현 규칙/30.3.11 테스트 구현.md`
- `31. 표준 프레임워크 설정 가이드/31.1 표준 애플리케이션 스캐폴드.md`
- `31. 표준 프레임워크 설정 가이드/31.4 프레임워크 로깅 설정.md`

Excluded by request:

- Clean Architecture concept explanations.
- Hexagonal Architecture concept explanations.
- UseCase, Port, Adapter dependency-direction rules.
- Package placement rules that only make sense in a hexagonal layout.

## Audit Modes

| Mode | Use when | Behavior |
|---|---|---|
| `basic` | Default scaffold generation or validation | Stable Java/Spring conventions fail validation; unresolved tooling decisions are warnings. |
| `strict` | CI-style convention gate or final project review | Advisory convention checks become errors. |
| `off` | User explicitly wants only scaffold structure checks | Convention checks are skipped. |

## Automatic Checks

These are deterministic and safe to run in `scripts/scaffold.py validate`.

- The CJOS root package should follow `cj.enm.<site>.<service>.<application-type>`, where `application-type` is `bffapi`, `domainapi`, or `batch`.
- Java package declarations must match the source path under `src/main/java` or `src/test/java`.
- Public Java type names must match filenames.
- Wildcard imports are not allowed.
- Common Spring layer packages should use predictable filename suffixes:
  - `controller` -> `*Controller`
  - `service` -> `*Service`
  - `repository` -> `*Repository`
  - `dto` -> `*Dto`
  - `config` -> `*Config`
  - `client` -> `*Client`
  - `request` -> `*Request`
  - `response` -> `*Response`
- Service classes under `.service` should use `@Transactional`.
- JPA entities should declare an explicit `@Table` name.
- JPA entities should be `class`, not `record`.
- `*Request`, `*Response`, `*Command`, and `*Query` models should be `record`.
- Lombok usage should not include `@Data`, general-model `@Setter`, `toBuilder = true`, `val`, or production-code `var`.
- Numeric validation should use `@Min`, `@Max`, `@Positive`, or related annotations instead of `@Size`.
- Controller classes should include OpenAPI `@Tag`, handler methods should include `@Operation` and `@ApiResponse`, and exposed path/query/header parameters should use `@Parameter`.
- Application logs should not use `System.out.println`, `System.err.println`, dynamic `event={}`, or dynamic `message={}`.
- Test class suffixes should be `*Test`, `*SliceTest`, or `*ArchitectureTest`.
- Test methods should follow `{action}_when{condition}_{expectedResult}` and use `@DisplayName`.
- Gradle should include `jacoco` and 70% line coverage verification when the project is treated as a CJOS standard application.
- `logback-spring.xml` should include the CJOS Logback fragments when the project is treated as a CJOS standard application.
- Projects should eventually declare a formatting or style tool, such as Spotless or Checkstyle.
- Projects should eventually include `.editorconfig`.

## Reviewer Checks

Keep these as human review guidance unless the rule becomes precise enough for a script.

- Names should express business meaning, not just technical shape.
- Controllers should stay thin and delegate business behavior.
- Services should own transaction boundaries.
- DTOs should avoid leaking persistence-only concerns.
- Exception responses should stay consistent across validation, domain, and unexpected errors.
- Package boundaries should reflect domain ownership rather than incidental implementation detail.
- Use `RuntimeException` or `IllegalArgumentException` carefully: domain value-object immediate validation can use `IllegalArgumentException`, but API business errors should use the application's standard exception model.
- API versioning is optional. Apply it only when the project explicitly needs a version compatibility strategy.
- API compatibility changes should not delete or rename existing request/response fields within the same major version.
- Error responses should not expose internal exception messages, stack traces, or sensitive implementation details.
- Logs should not include sensitive data or unnecessary request/response bodies.
- Unit tests should verify contracts and edge cases, not implementation details.
- Controller slice tests should verify request mapping, response status, and Bean Validation failures.
- Resilience, event, HTTP client, and security rules should be reviewed only when those features are present.

## Future Convention Updates

When importing or refreshing a Confluence convention document:

1. Read the page with the Confluence CLI.
2. Extract only actionable conventions into this file.
3. Mark each convention as automatic or reviewer-only.
4. Add deterministic rules to `scripts/scaffold.py` only when false positives are unlikely.
5. Keep the Confluence page ID and retrieval date in `Source Status`.
