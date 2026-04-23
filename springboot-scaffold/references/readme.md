# {$AppName}

Project {$AppName}.

## Tech Stack

- Java 25
- Spring Boot 4.0.1
- Spring Data JPA
- H2 (development/test)
- PostgreSQL (production)
- Lombok
- Log4j2
- Springdoc OpenAPI

## Project Structure

```
src/
├── main/
│   ├── java/
│   │   └── {$ROOT}/
│   │       ├── {$AppName}Application.java
│   │       ├── common/
│   │       ├── config/
│   │       ├── domain/
│   │       └── external/
│   └── resources/
│       ├── application.yml
│       └── log4j2.xml
└── test/
```

## Build and Run

### Build
```bash
./gradlew build
```

### Run
```bash
./gradlew bootRun
```

### Test
```bash
./gradlew test
```

## API Documentation

- Swagger UI: http://localhost:8080/swagger-ui.html
- OpenAPI Spec: http://localhost:8080/v3/api-docs

## Profiles

| Profile | Description |
|---------|-------------|
| default | H2 in-memory DB |
| dev | H2 development DB |
| prod | PostgreSQL production DB |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | app |
| DB_USERNAME | DB username | - |
| DB_PASSWORD | DB password | - |
