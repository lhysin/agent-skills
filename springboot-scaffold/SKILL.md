---
name: springboot-scaffold
description: |
  Generate, validate, and convention-audit a Spring Boot project scaffold. Use this skill when the user asks for Spring Boot project creation, Spring Boot scaffolding, scaffold validation, Spring Boot code convention checks, "스프링부트 프로젝트 생성", "스프링부트 스캐폴딩", "새 스프링부트 앱 만들기", "코드 컨벤션 검수", "코딩 컨벤션 점검", or invokes /springboot-scaffold.
  The scaffold is generated mechanically through scripts/scaffold.py and then checked with deterministic rules for package layout, Gradle dependencies, profiles, .gitkeep behavior, optional sample domain code, and baseline Java/Spring convention rules.

  Usage:
    /springboot-scaffold --root GROUP_ID --appname APP_NAME [--java-version 25] [--skeleton on|off] [--target PATH] [--convention basic|strict|off] [--help]
---

# Spring Boot Scaffold

## Primary Rule

Generate and validate the actual project skeleton with `scripts/scaffold.py`. Do not hand-copy templates or manually audit conventions when the script can run.

Script path relative to this skill:

```bash
python3 springboot-scaffold/scripts/scaffold.py
```

When running from another working directory, use the absolute skill path.

## Invocation Mapping

For a normal request, run:

```bash
python3 springboot-scaffold/scripts/scaffold.py generate --root <group-id> --appname <app-name> --target <project-root> --java-version <version> --skeleton <on|off>
```

If the user omits `--target`, use the current working directory. If the user omits `--java-version`, use `25`. If the user omits `--skeleton`, use `off`. If the user omits `--convention`, use `basic`.

If the user asks for help or passes `--help`, run:

```bash
python3 springboot-scaffold/scripts/scaffold.py --help
```

The script returns JSON. Read `ok`, `result.validation`, `result.generation.collisions`, and `next_actions` before responding.

## Parameters

| Parameter | Required | Default | Rule |
|---|---:|---:|---|
| `--root` | yes | - | Lowercase Java package root, for example `com.example` |
| `--appname` | yes | - | Java class name starting with uppercase, for example `DemoApp` |
| `--target` | no | `.` | Project root to write into |
| `--java-version` | no | `25` | Integer `>= 17` |
| `--skeleton` | no | `off` | `off` creates base packages only; `on` also creates sample order/payment code |
| `--convention` | no | `basic` | `basic` audits stable conventions; `strict` turns advisory convention checks into errors; `off` skips convention audit |

Invalid parameters should be handled by the script. Return its JSON error message instead of inventing a different error.

## Validation

Generation validates automatically unless `--no-validate` is passed. To validate an existing scaffold, run:

```bash
python3 springboot-scaffold/scripts/scaffold.py validate --root <group-id> --appname <app-name> --target <project-root> --java-version <version> --skeleton <on|off>
```

Use `--strict-wrapper` only when wrapper files must be treated as a hard failure. Without it, missing wrapper files are warnings because wrapper generation depends on a local Gradle CLI.

The validator checks these rules:

- Required project files exist: `build.gradle`, `settings.gradle`, `gradle.properties`, `.gitignore`, `README.md`, application YAML files, application class, common exception/advice classes, and OpenAPI config.
- Java package declarations use the requested `--root`.
- `gradle.properties` contains one source of truth for Java, Spring Boot, Lombok, OpenAPI, and Gradle versions.
- `build.gradle` includes web, JPA, validation, Log4j2, actuator, springdoc, Lombok, PostgreSQL, and test dependencies.
- H2 is allowed only as `developmentOnly` and `testRuntimeOnly`; it must not be production `runtimeOnly`.
- `application-prod.yml` uses PostgreSQL and `ddl-auto: validate`.
- `skeleton=off` creates `.gitkeep` files for empty `domain`, `domain/order`, `external`, and `external/payment` packages and does not create sample order/payment source files.
- `skeleton=on` creates order domain, payment external, and `OrderServiceTest.java`; `Order` uses an explicit table name and `OrderService` uses `@Transactional`.
- No generated file contains unresolved placeholders.

## Convention Audit

The default `--convention basic` mode adds deterministic Java/Spring checks to validation:

- Java package declarations match the source path under `src/main/java` or `src/test/java`.
- Public Java type names match their filenames.
- Wildcard imports are not used.
- Layer packages use predictable suffixes, such as `controller` -> `*Controller`, `service` -> `*Service`, `repository` -> `*Repository`, `dto` -> `*Dto`, `request` -> `*Request`, and `response` -> `*Response`.
- Lombok, Java record/class usage, validation annotations, logging calls, test names, and selected API documentation conventions follow the CJOS common v5 baseline in `references/code-convention.md`.
- Service classes under `.service` use `@Transactional` when present.
- JPA entities use explicit `@Table` names.

`basic` reports CJOS-specific project decisions, such as non-CJOS root packages, missing `.editorconfig`, missing formatter/checkstyle configuration, missing JaCoCo, or missing CJOS Logback fragments, as warnings. `strict` treats those advisory convention gaps as validation errors. Use `off` only when the user explicitly wants structure validation without convention audit.

Do not enforce API versioning by default. Apply API versioning only when the user or target project explicitly requires a version compatibility strategy.

## Collision Policy

Without `--force`, an existing file is not overwritten. The script writes the generated content to `{filename}.new` or `{filename}.new.N`, reports the collision in JSON, skips wrapper generation, and validates the canonical files that remain in place.

Use `--force` only when the user clearly wants to overwrite existing scaffold files.

## Generated Shape

All modes create:

```text
build.gradle
settings.gradle
gradle.properties
.gitignore
README.md
src/main/java/<root>/<AppName>Application.java
src/main/java/<root>/common/advice/GlobalExceptionHandler.java
src/main/java/<root>/common/exception/BaseException.java
src/main/java/<root>/common/exception/ErrorCode.java
src/main/java/<root>/config/OpenApiConfig.java
src/main/resources/application.yml
src/main/resources/application-dev.yml
src/main/resources/application-prod.yml
```

`skeleton=on` also creates sample files under:

```text
src/main/java/<root>/domain/order/
src/main/java/<root>/external/payment/
src/test/java/<root>/domain/order/service/OrderServiceTest.java
```

## Reference Loading

`scripts/scaffold.py` is the source of truth. Load files in `references/` only when the script cannot run or the user explicitly asks to inspect the template or convention notes:

- `references/build.gradle.md` for dependency rationale.
- `references/application.yml.md` for profile rationale.
- `references/java.md` and `references/test.md` for class template notes.
- `references/gradlew.md` for wrapper fallback context.
- `references/code-convention.md` for the current convention audit baseline and the boundary between automatic checks and reviewer judgment.

## Do Not Generate

- Do not handwrite the scaffold when the generator script can run.
- Do not skip validation after generation.
- Do not skip the convention audit unless the user asks for `--convention off`.
- Do not put H2 in production `runtimeOnly`.
- Do not generate JPA entities for SQL-keyword tables without explicit `@Table(name = "...")`.
- Do not create sample order/payment source files when `--skeleton off`.
- Do not overwrite existing files unless the user asked for overwrite or `--force`.
