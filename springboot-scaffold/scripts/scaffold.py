#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULTS = {
    "java_version": "25",
    "spring_boot_version": "4.0.5",
    "lombok_version": "1.18.42",
    "openapi_version": "3.0.1",
    "gradle_version": "9.4.1",
}

ROOT_RE = re.compile(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$")
APPNAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
TEXT_SUFFIXES = {".gradle", ".properties", ".yml", ".yaml", ".java", ".md", ".txt", ".bat", ".sh"}
TEXT_NAMES = {".gitignore", "gradlew"}
IGNORED_TEXT_SCAN_DIRS = {".gradle", "build", ".git"}


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover - argparse callback
        raise ValueError(message)


def render(template: str, context: dict[str, str]) -> str:
    result = template
    for key, value in context.items():
        result = result.replace("{{" + key + "}}", value)
    return result.strip() + "\n"


def package_path(root: str) -> Path:
    return Path(*root.split("."))


def rel_text(path: Path, target: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def next_collision_path(path: Path) -> Path:
    candidate = path.with_name(path.name + ".new")
    index = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.new.{index}")
        index += 1
    return candidate


def write_file(
    target: Path,
    relative: Path,
    content: str,
    force: bool,
    written: list[str],
    collisions: list[dict[str, str]],
) -> None:
    destination = target / relative
    if destination.exists() and not force:
        collision = next_collision_path(destination)
        collisions.append(
            {
                "existing": rel_text(destination, target),
                "written": rel_text(collision, target),
            }
        )
        destination = collision

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    written.append(rel_text(destination, target))


def touch_gitkeep(target: Path, relative: Path, written: list[str]) -> None:
    path = target / relative / ".gitkeep"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        written.append(rel_text(path, target))


def build_gradle() -> str:
    return """plugins {
    id 'java'
    id 'org.springframework.boot' version "${spring_boot_version}"
    id 'io.spring.dependency-management' version '1.1.7'
}

group = '{{ROOT}}'
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
    developmentOnly 'com.h2database:h2'

    compileOnly "org.projectlombok:lombok:${lombok_version}"
    annotationProcessor "org.projectlombok:lombok:${lombok_version}"

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testCompileOnly "org.projectlombok:lombok:${lombok_version}"
    testAnnotationProcessor "org.projectlombok:lombok:${lombok_version}"
    testRuntimeOnly 'com.h2database:h2'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
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
"""


def gradle_properties(context: dict[str, str]) -> str:
    return """# Java
java_version={{JAVA_VERSION}}

# Spring Boot
spring_boot_version={{SPRING_BOOT_VERSION}}

# Lombok
lombok_version={{LOMBOK_VERSION}}

# OpenAPI
openapi_version={{OPENAPI_VERSION}}

# Gradle
gradle_version={{GRADLE_VERSION}}
"""


def application_yml() -> dict[Path, str]:
    return {
        Path("src/main/resources/application.yml"): """spring:
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

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when_authorized
""",
        Path("src/main/resources/application-dev.yml"): """spring:
  datasource:
    url: jdbc:h2:mem:devdb;MODE=PostgreSQL;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
""",
        Path("src/main/resources/application-prod.yml"): """spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/${APP_NAME:app}
    driver-class-name: org.postgresql.Driver
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: validate
""",
    }


def gitignore() -> str:
    return """# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar

# IDE
.idea/
*.iws
*.ipr
*.iml
.vscode/
*.swp
*.swo
*~

# Eclipse
.classpath
.project
.settings/
.metadata/

# NetBeans
nbproject/private/
nbbuild/
dist/
nbdist/
.nb-gradle/

# Spring Boot
*.log
logs/

# H2 Database
*.db
*.mv.db
*.trace.db

# OS
.DS_Store
Thumbs.db

# Environment
.env
*.env.local
application-local.yml
application-local.properties

# Build archives
*.class
*.jar
*.war
*.ear
*.zip
*.tar.gz
*.rar

# Test output
test-results/
coverage/

# Merge leftovers
*.bak
*.tmp
*.orig
"""


def readme(context: dict[str, str]) -> str:
    return """# {{APPNAME}}

Project {{APPNAME}}.

## Tech Stack

- Java {{JAVA_VERSION}}
- Spring Boot {{SPRING_BOOT_VERSION}}
- Spring Data JPA
- H2 (development/test)
- PostgreSQL (production)
- Lombok
- Log4j2
- Springdoc OpenAPI

## Build and Run

```bash
./gradlew build
./gradlew bootRun
./gradlew test
```

## API Documentation

- Swagger UI: http://localhost:8080/swagger-ui.html
- OpenAPI Spec: http://localhost:8080/v3/api-docs

## Profiles

| Profile | Description |
|---|---|
| default | H2 in-memory DB |
| dev | H2 development DB |
| prod | PostgreSQL production DB |

## Environment Variables

| Variable | Description |
|---|---|
| APP_NAME | Application database name |
| DB_USERNAME | Production DB username |
| DB_PASSWORD | Production DB password |
"""


def core_java_templates(context: dict[str, str]) -> dict[Path, str]:
    root_path = package_path(context["ROOT"])
    app = context["APPNAME"]
    return {
        Path("src/main/java") / root_path / f"{app}Application.java": """package {{ROOT}};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {{APPNAME}}Application {
    public static void main(String[] args) {
        SpringApplication.run({{APPNAME}}Application.class, args);
    }
}
""",
        Path("src/main/java") / root_path / "common/exception/ErrorCode.java": """package {{ROOT}}.common.exception;

public enum ErrorCode {
    BAD_REQUEST("BAD_REQUEST", "Bad request."),
    INTERNAL_ERROR("INTERNAL_ERROR", "Internal server error.");

    private final String code;
    private final String message;

    ErrorCode(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }
}
""",
        Path("src/main/java") / root_path / "common/exception/BaseException.java": """package {{ROOT}}.common.exception;

public class BaseException extends RuntimeException {
    private final ErrorCode errorCode;

    public BaseException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public BaseException(ErrorCode errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }
}
""",
        Path("src/main/java") / root_path / "common/advice/GlobalExceptionHandler.java": """package {{ROOT}}.common.advice;

import {{ROOT}}.common.exception.BaseException;
import {{ROOT}}.common.exception.ErrorCode;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BaseException.class)
    public ResponseEntity<Map<String, Object>> handleBaseException(BaseException ex) {
        Map<String, Object> body = new LinkedHashMap<>();
        ErrorCode errorCode = ex.getErrorCode();
        body.put("code", errorCode.getCode());
        body.put("message", ex.getMessage());
        return new ResponseEntity<>(body, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("code", "VALIDATION_ERROR");
        body.put("message", ex.getBindingResult().getFieldErrors().stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .reduce((a, b) -> a + "; " + b)
            .orElse("Validation failed"));
        return new ResponseEntity<>(body, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleException(Exception ex) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("code", ErrorCode.INTERNAL_ERROR.getCode());
        body.put("message", ErrorCode.INTERNAL_ERROR.getMessage());
        return new ResponseEntity<>(body, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
""",
        Path("src/main/java") / root_path / "config/OpenApiConfig.java": """package {{ROOT}}.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("{{APPNAME}} API")
                .version("1.0")
                .description("{{APPNAME}} API Documentation"))
            .servers(List.of(
                new Server().url("/").description("Default Server")
            ));
    }
}
""",
    }


def skeleton_java_templates(context: dict[str, str]) -> dict[Path, str]:
    root_path = package_path(context["ROOT"])
    base = Path("src/main/java") / root_path
    test_base = Path("src/test/java") / root_path
    return {
        base / "domain/order/controller/OrderController.java": """package {{ROOT}}.domain.order.controller;

import {{ROOT}}.domain.order.dto.OrderDto;
import {{ROOT}}.domain.order.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Tag(name = "Order API", description = "Order operations")
public class OrderController {
    private final OrderService orderService;

    @Operation(summary = "List orders")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Orders returned")
    })
    @GetMapping
    public ResponseEntity<List<OrderDto>> findAll() {
        return ResponseEntity.ok(orderService.findAll());
    }

    @Operation(summary = "Get order by ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Order returned"),
        @ApiResponse(responseCode = "404", description = "Order not found")
    })
    @GetMapping("/{id}")
    public ResponseEntity<OrderDto> findById(@PathVariable Long id) {
        return ResponseEntity.ok(orderService.findById(id));
    }

    @Operation(summary = "Create order")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Order created")
    })
    @PostMapping
    public ResponseEntity<OrderDto> save(@Valid @RequestBody OrderDto dto) {
        return ResponseEntity.ok(orderService.save(dto));
    }
}
""",
        base / "domain/order/service/OrderService.java": """package {{ROOT}}.domain.order.service;

import {{ROOT}}.domain.order.dto.OrderDto;
import {{ROOT}}.domain.order.entity.Order;
import {{ROOT}}.domain.order.repository.OrderRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;

    @Transactional(readOnly = true)
    public List<OrderDto> findAll() {
        return orderRepository.findAll().stream()
            .map(this::toDto)
            .toList();
    }

    @Transactional(readOnly = true)
    public OrderDto findById(Long id) {
        return orderRepository.findById(id)
            .map(this::toDto)
            .orElseThrow(() -> new RuntimeException("Order not found"));
    }

    @Transactional
    public OrderDto save(OrderDto dto) {
        Order entity = Order.builder()
            .productName(dto.productName())
            .quantity(dto.quantity())
            .price(dto.price())
            .build();
        return toDto(orderRepository.save(entity));
    }

    private OrderDto toDto(Order entity) {
        return OrderDto.builder()
            .id(entity.getId())
            .productName(entity.getProductName())
            .quantity(entity.getQuantity())
            .price(entity.getPrice())
            .build();
    }
}
""",
        base / "domain/order/repository/OrderRepository.java": """package {{ROOT}}.domain.order.repository;

import {{ROOT}}.domain.order.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}
""",
        base / "domain/order/entity/Order.java": """package {{ROOT}}.domain.order.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "orders")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "product_name", nullable = false)
    private String productName;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false)
    private Long price;
}
""",
        base / "domain/order/dto/OrderDto.java": """package {{ROOT}}.domain.order.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;

@Builder
public record OrderDto(
    Long id,

    @NotBlank(message = "Product name is required")
    String productName,

    @NotNull(message = "Quantity is required")
    @Min(value = 1, message = "Quantity must be at least 1")
    Integer quantity,

    @NotNull(message = "Price is required")
    @Min(value = 0, message = "Price must be non-negative")
    Long price
) {}
""",
        base / "external/payment/client/PaymentClient.java": """package {{ROOT}}.external.payment.client;

import org.springframework.stereotype.Component;

@Component
public class PaymentClient {
    public void requestPayment(Long orderId, Long amount) {
        throw new UnsupportedOperationException("Implement payment integration");
    }
}
""",
        base / "external/payment/model/request/PaymentRequest.java": """package {{ROOT}}.external.payment.model.request;

import lombok.Builder;

@Builder
public record PaymentRequest(
    Long orderId,
    Long amount,
    String paymentMethod
) {}
""",
        base / "external/payment/model/response/PaymentResponse.java": """package {{ROOT}}.external.payment.model.response;

import lombok.Builder;

@Builder
public record PaymentResponse(
    String transactionId,
    String status,
    Long amount
) {}
""",
        test_base / "domain/order/service/OrderServiceTest.java": """package {{ROOT}}.domain.order.service;

import {{ROOT}}.domain.order.dto.OrderDto;
import {{ROOT}}.domain.order.entity.Order;
import {{ROOT}}.domain.order.repository.OrderRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    void findAllReturnsOrders() {
        Order order = Order.builder()
            .id(1L)
            .productName("Test Product")
            .quantity(10)
            .price(1000L)
            .build();
        when(orderRepository.findAll()).thenReturn(List.of(order));

        List<OrderDto> result = orderService.findAll();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).productName()).isEqualTo("Test Product");
    }

    @Test
    void findByIdReturnsOrderWhenOrderExists() {
        Order order = Order.builder()
            .id(1L)
            .productName("Test Product")
            .quantity(10)
            .price(1000L)
            .build();
        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        OrderDto result = orderService.findById(1L);

        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.productName()).isEqualTo("Test Product");
    }

    @Test
    void saveReturnsSavedOrder() {
        OrderDto dto = OrderDto.builder()
            .productName("New Product")
            .quantity(5)
            .price(500L)
            .build();
        Order savedOrder = Order.builder()
            .id(1L)
            .productName("New Product")
            .quantity(5)
            .price(500L)
            .build();
        when(orderRepository.save(any(Order.class))).thenReturn(savedOrder);

        OrderDto result = orderService.save(dto);

        assertThat(result.id()).isEqualTo(1L);
        assertThat(result.productName()).isEqualTo("New Product");
    }
}
""",
    }


def base_directories(root: str) -> list[Path]:
    root_path = package_path(root)
    base = Path("src/main/java") / root_path
    return [
        base / "common/advice",
        base / "common/exception",
        base / "config",
        base / "domain",
        base / "domain/order",
        base / "external",
        base / "external/payment",
        Path("src/main/resources"),
        Path("src/test/java") / root_path,
    ]


def write_scaffold(
    target: Path,
    root: str,
    appname: str,
    java_version: str,
    skeleton: str,
    force: bool,
) -> dict[str, object]:
    context = {
        "ROOT": root,
        "APPNAME": appname,
        "JAVA_VERSION": java_version,
        "SPRING_BOOT_VERSION": DEFAULTS["spring_boot_version"],
        "LOMBOK_VERSION": DEFAULTS["lombok_version"],
        "OPENAPI_VERSION": DEFAULTS["openapi_version"],
        "GRADLE_VERSION": DEFAULTS["gradle_version"],
    }
    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    collisions: list[dict[str, str]] = []

    for directory in base_directories(root):
        (target / directory).mkdir(parents=True, exist_ok=True)

    files: dict[Path, str] = {
        Path("build.gradle"): build_gradle(),
        Path("settings.gradle"): "rootProject.name = '{{APPNAME}}'\n",
        Path("gradle.properties"): gradle_properties(context),
        Path(".gitignore"): gitignore(),
        Path("README.md"): readme(context),
    }
    files.update(application_yml())
    files.update(core_java_templates(context))
    if skeleton == "on":
        files.update(skeleton_java_templates(context))

    for relative, template in files.items():
        write_file(target, relative, render(template, context), force, written, collisions)

    if skeleton == "off":
        root_path = package_path(root)
        for directory in [
            Path("src/main/java") / root_path / "domain",
            Path("src/main/java") / root_path / "domain/order",
            Path("src/main/java") / root_path / "external",
            Path("src/main/java") / root_path / "external/payment",
        ]:
            touch_gitkeep(target, directory, written)

    return {
        "target": str(target),
        "files_written_count": len(written),
        "files_written_sample": written[:25],
        "collisions": collisions,
    }


def run_gradle_wrapper(target: Path, wrapper: str, force: bool, collisions: list[dict[str, str]]) -> dict[str, object]:
    if wrapper == "skip":
        return {"status": "skipped", "message": "--wrapper skip was requested"}
    if collisions and not force:
        return {
            "status": "skipped",
            "message": "Skipped wrapper generation because canonical files had collisions.",
        }

    gradle = shutil.which("gradle")
    if not gradle:
        status = "error" if wrapper == "required" else "skipped"
        return {
            "status": status,
            "message": "Gradle CLI was not found. Install Gradle or run gradle wrapper later.",
        }

    command = [gradle, "wrapper", "--gradle-version", DEFAULTS["gradle_version"]]
    try:
        completed = subprocess.run(
            command,
            cwd=target,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        status = "error" if wrapper == "required" else "failed"
        return {"status": status, "message": "gradle wrapper timed out after 180 seconds"}

    if completed.returncode != 0:
        status = "error" if wrapper == "required" else "failed"
        output = (completed.stderr or completed.stdout).strip().splitlines()
        return {
            "status": status,
            "message": "gradle wrapper failed",
            "output_sample": output[:20],
        }

    gradlew = target / "gradlew"
    if gradlew.exists():
        gradlew.chmod(0o755)
    return {"status": "generated", "command": " ".join(command)}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def is_text_scan_candidate(path: Path, target: Path) -> bool:
    try:
        relative = path.relative_to(target)
    except ValueError:
        return False
    if any(part in IGNORED_TEXT_SCAN_DIRS for part in relative.parts):
        return False
    return path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES


def validate_project(
    target: Path,
    root: str,
    appname: str,
    java_version: str,
    skeleton: str,
    strict_wrapper: bool,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    rules: list[dict[str, object]] = []

    def check(name: str, passed: bool, message: str, severity: str = "error") -> None:
        rules.append({"name": name, "passed": passed, "severity": severity, "message": message})
        if not passed:
            if severity == "warning":
                warnings.append(message)
            else:
                errors.append(message)

    root_path = package_path(root)
    base = Path("src/main/java") / root_path
    test_base = Path("src/test/java") / root_path

    required_files = [
        Path("build.gradle"),
        Path("settings.gradle"),
        Path("gradle.properties"),
        Path(".gitignore"),
        Path("README.md"),
        Path("src/main/resources/application.yml"),
        Path("src/main/resources/application-dev.yml"),
        Path("src/main/resources/application-prod.yml"),
        base / f"{appname}Application.java",
        base / "common/exception/ErrorCode.java",
        base / "common/exception/BaseException.java",
        base / "common/advice/GlobalExceptionHandler.java",
        base / "config/OpenApiConfig.java",
    ]
    missing_required = [str(path) for path in required_files if not (target / path).exists()]
    check("required-files", not missing_required, f"Missing required files: {missing_required}")

    required_dirs = base_directories(root)
    missing_dirs = [str(path) for path in required_dirs if not (target / path).is_dir()]
    check("required-directories", not missing_dirs, f"Missing required directories: {missing_dirs}")

    gradle_text = read_text(target / "build.gradle")
    gradle_required_tokens = [
        "spring-boot-starter-web",
        "spring-boot-starter-data-jpa",
        "spring-boot-starter-validation",
        "spring-boot-starter-log4j2",
        "spring-boot-starter-actuator",
        "springdoc-openapi-starter-webmvc-ui",
        "runtimeOnly 'org.postgresql:postgresql'",
        "developmentOnly 'com.h2database:h2'",
        "testRuntimeOnly 'com.h2database:h2'",
        "exclude group: 'org.springframework.boot', module: 'spring-boot-starter-logging'",
        f"group = '{root}'",
    ]
    missing_gradle_tokens = [token for token in gradle_required_tokens if token not in gradle_text]
    check("build-gradle-rules", not missing_gradle_tokens, f"build.gradle missing rules: {missing_gradle_tokens}")
    check(
        "h2-not-production-runtime",
        "runtimeOnly 'com.h2database:h2'" not in gradle_text,
        "H2 must not be declared as runtimeOnly; use developmentOnly and testRuntimeOnly.",
    )

    properties_text = read_text(target / "gradle.properties")
    property_tokens = [
        f"java_version={java_version}",
        f"spring_boot_version={DEFAULTS['spring_boot_version']}",
        f"lombok_version={DEFAULTS['lombok_version']}",
        f"openapi_version={DEFAULTS['openapi_version']}",
        f"gradle_version={DEFAULTS['gradle_version']}",
    ]
    missing_properties = [token for token in property_tokens if token not in properties_text]
    check("version-properties", not missing_properties, f"gradle.properties missing: {missing_properties}")

    prod_yml = read_text(target / "src/main/resources/application-prod.yml")
    check(
        "prod-database-rules",
        "jdbc:postgresql://" in prod_yml and "ddl-auto: validate" in prod_yml,
        "application-prod.yml must use PostgreSQL and ddl-auto: validate.",
    )

    app_text = read_text(target / base / f"{appname}Application.java")
    check(
        "application-class",
        f"package {root};" in app_text and "@SpringBootApplication" in app_text,
        "Application class must use the requested root package and @SpringBootApplication.",
    )

    wrapper_files = [
        Path("gradlew"),
        Path("gradlew.bat"),
        Path("gradle/wrapper/gradle-wrapper.properties"),
    ]
    missing_wrapper = [str(path) for path in wrapper_files if not (target / path).exists()]
    wrapper_severity = "error" if strict_wrapper else "warning"
    check(
        "gradle-wrapper-files",
        not missing_wrapper,
        f"Missing Gradle wrapper files: {missing_wrapper}",
        severity=wrapper_severity,
    )

    java_files = list((target / "src").rglob("*.java")) if (target / "src").exists() else []
    wrong_packages = []
    for java_file in java_files:
        text = read_text(java_file)
        if f"package {root}" not in text:
            wrong_packages.append(rel_text(java_file, target))
    check("java-package-declarations", not wrong_packages, f"Java files with wrong package: {wrong_packages}")

    unresolved_files = []
    for path in target.rglob("*"):
        if not path.is_file():
            continue
        if not is_text_scan_candidate(path, target):
            continue
        text = read_text(path)
        if "{{" in text or "}}" in text or "{$" in text:
            unresolved_files.append(rel_text(path, target))
    check("no-unresolved-placeholders", not unresolved_files, f"Files with unresolved placeholders: {unresolved_files}")

    skeleton_files = [
        base / "domain/order/controller/OrderController.java",
        base / "domain/order/service/OrderService.java",
        base / "domain/order/repository/OrderRepository.java",
        base / "domain/order/entity/Order.java",
        base / "domain/order/dto/OrderDto.java",
        base / "external/payment/client/PaymentClient.java",
        base / "external/payment/model/request/PaymentRequest.java",
        base / "external/payment/model/response/PaymentResponse.java",
        test_base / "domain/order/service/OrderServiceTest.java",
    ]
    if skeleton == "on":
        missing_skeleton = [str(path) for path in skeleton_files if not (target / path).exists()]
        check("skeleton-source-files", not missing_skeleton, f"Missing skeleton files: {missing_skeleton}")
        order_entity = read_text(target / base / "domain/order/entity/Order.java")
        order_service = read_text(target / base / "domain/order/service/OrderService.java")
        check(
            "skeleton-domain-rules",
            '@Table(name = "orders")' in order_entity and "@Transactional" in order_service,
            "Order entity must use explicit table name and service methods must be transactional.",
        )
    else:
        present_skeleton = [str(path) for path in skeleton_files if (target / path).exists()]
        check("no-sample-source-when-off", not present_skeleton, f"Skeleton files must be absent: {present_skeleton}")
        gitkeep_dirs = [
            base / "domain",
            base / "domain/order",
            base / "external",
            base / "external/payment",
        ]
        missing_gitkeep = [str(path / ".gitkeep") for path in gitkeep_dirs if not (target / path / ".gitkeep").exists()]
        check("gitkeep-for-empty-packages", not missing_gitkeep, f"Missing .gitkeep files: {missing_gitkeep}")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "passed": sum(1 for rule in rules if rule["passed"]),
            "failed": sum(1 for rule in rules if not rule["passed"] and rule["severity"] == "error"),
            "warnings": sum(1 for rule in rules if not rule["passed"] and rule["severity"] == "warning"),
            "total": len(rules),
        },
        "rules": rules,
    }


def validate_arguments(root: str | None, appname: str | None, java_version: str, skeleton: str) -> list[str]:
    errors = []
    if not root:
        errors.append("Missing --root. Example: --root com.example")
    elif not ROOT_RE.match(root):
        errors.append("--root must be a lowercase Java package name such as com.example")
    if not appname:
        errors.append("Missing --appname. Example: --appname DemoApp")
    elif not APPNAME_RE.match(appname):
        errors.append("--appname must be a Java class name starting with an uppercase letter")
    if not str(java_version).isdigit() or int(java_version) < 17:
        errors.append("--java-version must be an integer >= 17")
    if skeleton not in {"on", "off"}:
        errors.append("--skeleton must be either on or off")
    return errors


def next_actions(root: str | None, appname: str | None, target: str | None, skeleton: str | None) -> list[dict[str, object]]:
    root_value = root or "<group-id>"
    app_value = appname or "<app-name>"
    target_value = target or "."
    skeleton_value = skeleton or "off"
    return [
        {
            "command": "python3 springboot-scaffold/scripts/scaffold.py validate --root <group-id> --appname <app-name> [--target <path>] [--skeleton <on|off>]",
            "description": "Validate the generated scaffold against deterministic rules.",
            "params": {
                "group-id": {"value": root_value, "description": "Java package root"},
                "app-name": {"value": app_value, "description": "SpringBootApplication class prefix"},
                "path": {"value": target_value, "default": ".", "description": "Project root directory"},
                "on|off": {"value": skeleton_value, "enum": ["on", "off"]},
            },
        },
        {
            "command": "cd <path> && ./gradlew test",
            "description": "Run the generated project's tests after validation passes.",
            "params": {
                "path": {"value": target_value, "description": "Project root directory"},
            },
        },
    ]


def emit(payload: dict[str, object], code: int) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return code


def command_tree(command: str) -> int:
    return emit(
        {
            "ok": True,
            "command": command,
            "result": {
                "description": "Generate or validate a Spring Boot scaffold.",
                "defaults": DEFAULTS,
                "commands": [
                    {
                        "name": "generate",
                        "usage": "scaffold.py generate --root <group-id> --appname <app-name> [--target <path>] [--java-version 25] [--skeleton off|on] [--wrapper auto|skip|required] [--force] [--no-validate]",
                    },
                    {
                        "name": "validate",
                        "usage": "scaffold.py validate --root <group-id> --appname <app-name> [--target <path>] [--java-version 25] [--skeleton off|on] [--strict-wrapper]",
                    },
                ],
            },
            "next_actions": next_actions(None, None, None, None),
        },
        0,
    )


def parse(argv: list[str]) -> tuple[str, argparse.Namespace]:
    if argv and argv[0] in {"generate", "validate"}:
        mode = argv[0]
        argv = argv[1:]
    else:
        mode = "generate"

    parser = JsonArgumentParser(add_help=False)
    parser.add_argument("--root")
    parser.add_argument("--appname")
    parser.add_argument("--java-version", default=DEFAULTS["java_version"])
    parser.add_argument("--skeleton", default="off", choices=["on", "off"])
    parser.add_argument("--target", default=".")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    parser.add_argument("--wrapper", default="auto", choices=["auto", "skip", "required"])
    parser.add_argument("--strict-wrapper", action="store_true")
    return mode, parser.parse_args(argv)


def main(argv: list[str]) -> int:
    command = " ".join([Path(sys.argv[0]).name] + argv)
    if not argv or any(arg in {"--help", "-h", "help"} for arg in argv):
        return command_tree(command)

    try:
        mode, args = parse(argv)
    except (ValueError, SystemExit) as exc:
        return emit(
            {
                "ok": False,
                "command": command,
                "error": {"code": "INVALID_ARGUMENT", "message": str(exc)},
                "fix": "Run with --help to inspect valid parameters.",
                "next_actions": next_actions(None, None, None, None),
            },
            2,
        )

    argument_errors = validate_arguments(args.root, args.appname, args.java_version, args.skeleton)
    if argument_errors:
        return emit(
            {
                "ok": False,
                "command": command,
                "error": {"code": "INVALID_ARGUMENT", "message": "; ".join(argument_errors)},
                "fix": "Provide --root and --appname using Java naming conventions.",
                "next_actions": next_actions(args.root, args.appname, args.target, args.skeleton),
            },
            2,
        )

    target = Path(args.target).expanduser().resolve()
    if mode == "validate":
        validation = validate_project(
            target=target,
            root=args.root,
            appname=args.appname,
            java_version=args.java_version,
            skeleton=args.skeleton,
            strict_wrapper=args.strict_wrapper,
        )
        return emit(
            {
                "ok": validation["ok"],
                "command": command,
                "result": {
                    "target": str(target),
                    "root": args.root,
                    "appname": args.appname,
                    "skeleton": args.skeleton,
                    "validation": validation,
                },
                "next_actions": next_actions(args.root, args.appname, str(target), args.skeleton),
            },
            0 if validation["ok"] else 1,
        )

    generation = write_scaffold(
        target=target,
        root=args.root,
        appname=args.appname,
        java_version=args.java_version,
        skeleton=args.skeleton,
        force=args.force,
    )
    wrapper = run_gradle_wrapper(target, args.wrapper, args.force, generation["collisions"])
    validation = None
    if not args.no_validate:
        validation = validate_project(
            target=target,
            root=args.root,
            appname=args.appname,
            java_version=args.java_version,
            skeleton=args.skeleton,
            strict_wrapper=args.wrapper == "required",
        )

    ok = wrapper.get("status") != "error" and (validation is None or validation["ok"])
    return emit(
        {
            "ok": ok,
            "command": command,
            "result": {
                "root": args.root,
                "appname": args.appname,
                "java_version": args.java_version,
                "skeleton": args.skeleton,
                "generation": generation,
                "wrapper": wrapper,
                "validation": validation,
            },
            "next_actions": next_actions(args.root, args.appname, str(target), args.skeleton),
        },
        0 if ok else 1,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
