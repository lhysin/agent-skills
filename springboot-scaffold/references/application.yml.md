# application.yml Template

## application.yml (default)

```yaml
spring:
  profiles:
    active: default
  datasource:
    url: jdbc:h2:mem:defaultdb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: update

# actuator
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when_authorized
```

---

## application-dev.yml

```yaml
spring:
  datasource:
    url: jdbc:h2:mem:devdb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
```

---

## application-prod.yml

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/${APP_NAME:app}
    driver-class-name: org.postgresql.Driver
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate
```
