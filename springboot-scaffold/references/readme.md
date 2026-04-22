# {$AppName}

{$AppName} 프로젝트입니다.

## 기술 스택

- Java 25
- Spring Boot 4.0.1
- Spring Data JPA
- H2 (개발/테스트)
- PostgreSQL (프로덕션)
- Lombok
- Log4j2
- Springdoc OpenAPI

## 프로젝트 구조

```
src/
├── main/
│   ├── java/
│   │   └── {$ROOT}/
│   │       ├── {$AppName}SpringBootApplication.java
│   │       ├── common/
│   │       ├── config/
│   │       ├── domain/
│   │       └── external/
│   └── resources/
│       ├── application.yml
│       └── log4j2.xml
└── test/
```

## 빌드 및 실행

### 빌드
```bash
./gradlew build
```

### 실행
```bash
./gradlew bootRun
```

### 테스트
```bash
./gradlew test
```

## API 문서

- Swagger UI: http://localhost:8080/swagger-ui.html
- OpenAPI Spec: http://localhost:8080/v3/api-docs

## 프로필

| 프로필 | 설명 |
|--------|------|
| default | H2 인메모리 DB |
| dev | H2 개발용 DB |
| prod | PostgreSQL 프로덕션 DB |

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| APP_NAME | 애플리케이션 이름 | app |
| DB_USERNAME | DB 사용자명 | - |
| DB_PASSWORD | DB 비밀번호 | - |