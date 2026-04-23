# build.gradle Template

## Dependency Selection Rationale
- **spring-boot-starter-actuator** — Provides health, metrics, info endpoints. Required for production
- **spring-boot-starter-log4j2** — Used over logback. Balances performance and flexibility
- **springdoc-openapi-starter-webmvc-ui** — Swagger3 UI auto-generated, no separate JSON config needed
- **H2 as runtimeOnly + testRuntimeOnly only** — Auto-excluded from prod build; safety mechanism
- **postgresql runtimeOnly** — Production DB defaults to PostgreSQL

```groovy
plugins {
    id 'java'
    id 'org.springframework.boot' version "${spring_boot_version}"
    id 'io.spring.dependency-management' version '1.1.7'
}

group = '{$ROOT}'
version = '0.0.1-SNAPSHOT'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(java_version as Integer)
    }
}

configurations {
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-log4j2'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation "org.springdoc:springdoc-openapi-starter-webmvc-ui:${openapi_version}"

    runtimeOnly 'org.postgresql:postgresql'
    runtimeOnly 'com.h2database:h2'

    compileOnly "org.projectlombok:lombok:${lombok_version}"
    annotationProcessor "org.projectlombok:lombok:${lombok_version}"

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testCompileOnly "org.projectlombok:lombok:${lombok_version}"
    testAnnotationProcessor "org.projectlombok:lombok:${lombok_version}"
    testRuntimeOnly 'com.h2database:h2'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.boot:spring-boot-dependencies:${spring_boot_version}"
    }
}

configurations.configureEach {
    exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'
}

tasks.named('test') {
    useJUnitPlatform()
}
```