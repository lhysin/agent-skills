# Java Templates

## When to Read This File
- When generating `common/exception`, `common/advice`, or `config` classes
- When `Skeleton=off`: create .gitkeep in all package directories
- When `Skeleton=on`: also generates Order/Payment related classes

## Template Substitution Rules

| Placeholder | Description |
|-------------|-------------|
| `{$ROOT}` | Actual group ID (e.g., com.example) |
| `{$AppName}` | Actual application name |
| `{$JavaVersion}` | Java version (default: 25) |
| `{$SpringBootVersion}` | Spring Boot version (default: 4.0.1) |
| `{$LombokVersion}` | Lombok version (default: 1.18.42) |

## {$AppName}Application.java

```java
package {$ROOT};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class {$AppName}Application {
    public static void main(String[] args) {
        SpringApplication.run({$AppName}Application.class, args);
    }
}
```

---

## ErrorCode.java (common/exception)

```java
package {$ROOT}.common.exception;

public enum ErrorCode {
    // TODO: Define error codes
    // INVALID_INPUT("INVALID_INPUT", "Invalid input."),
    ;
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
```

---

## BaseException.java (common/exception)

```java
package {$ROOT}.common.exception;

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
```

---

## GlobalExceptionHandler.java (common/advice)

```java
package {$ROOT}.common.advice;

import {$ROOT}.common.exception.BaseException;
import {$ROOT}.common.exception.ErrorCode;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BaseException.class)
    public ResponseEntity<Map<String, Object>> handleBaseException(BaseException ex) {
        Map<String, Object> body = new HashMap<>();
        ErrorCode errorCode = ex.getErrorCode();
        body.put("code", errorCode.getCode());
        body.put("message", ex.getMessage());
        return new ResponseEntity<>(body, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex) {
        Map<String, Object> body = new HashMap<>();
        body.put("code", "VALIDATION_ERROR");
        body.put("message", ex.getBindingResult().getFieldErrors().stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .reduce((a, b) -> a + "; " + b)
            .orElse("Validation failed"));
        return new ResponseEntity<>(body, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleException(Exception ex) {
        Map<String, Object> body = new HashMap<>();
        body.put("code", "INTERNAL_ERROR");
        body.put("message", "An unexpected error occurred.");
        return new ResponseEntity<>(body, HttpStatus.INTERNAL_SERVER_ERROR);
    }
}
```

---

## OpenApiConfig.java (config)

```java
package {$ROOT}.config;

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
                .title("{$AppName} API")
                .version("1.0")
                .description("{$AppName} API Documentation"))
            .servers(List.of(
                new Server().url("/").description("Default Server")
            ));
    }
}
```

---

## Classes Generated When Skeleton is ON

### domain/order/controller/OrderController.java

```java
package {$ROOT}.domain.order.controller;

import {$ROOT}.domain.order.dto.OrderDto;
import {$ROOT}.domain.order.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Tag(name = "주문 API", description = "주문 관련 API")
public class OrderController {
    private final OrderService orderService;

    @Operation(summary = "주문 목록 조회", description = "모든 주문을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공")
    })
    @GetMapping
    public ResponseEntity<List<OrderDto>> findAll() {
        return ResponseEntity.ok(orderService.findAll());
    }

    @Operation(summary = "주문 조회", description = "ID로 주문을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공"),
        @ApiResponse(responseCode = "404", description = "주문을 찾을 수 없음")
    })
    @GetMapping("/{id}")
    public ResponseEntity<OrderDto> findById(
            @Parameter(description = "주문 ID") @PathVariable Long id) {
        return ResponseEntity.ok(orderService.findById(id));
    }

    @Operation(summary = "주문 생성", description = "새 주문을 생성합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "생성 성공")
    })
    @PostMapping
    public ResponseEntity<OrderDto> save(@Valid @RequestBody OrderDto dto) {
        return ResponseEntity.ok(orderService.save(dto));
    }
}
```

### domain/order/service/OrderService.java

```java
package {$ROOT}.domain.order.service;

import {$ROOT}.domain.order.dto.OrderDto;
import {$ROOT}.domain.order.entity.Order;
import {$ROOT}.domain.order.repository.OrderRepository;
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
```

### domain/order/repository/OrderRepository.java

```java
package {$ROOT}.domain.order.repository;

import {$ROOT}.domain.order.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}
```

### domain/order/entity/Order.java

```java
package {$ROOT}.domain.order.entity;

import jakarta.persistence.*;
import lombok.*;

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

    @Column(nullable = false)
    private String productName;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false)
    private Long price;
}
```

### domain/order/dto/OrderDto.java

```java
package {$ROOT}.domain.order.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;

@Builder
public record OrderDto(
    Long id,

    @NotBlank(message = "상품명은 필수입니다")
    String productName,

    @NotNull(message = "수량은 필수입니다")
    @Min(value = 1, message = "수량은 1 이상이어야 합니다")
    Integer quantity,

    @NotNull(message = "가격은 필수입니다")
    @Min(value = 0, message = "가격은 0 이상이어야 합니다")
    Long price
) {}
```

---

### external/payment/client/PaymentClient.java

```java
package {$ROOT}.external.payment.client;

import org.springframework.stereotype.Component;

@Component
public class PaymentClient {
    // TODO: Implement external payment API integration
}
```

### external/payment/model/request/PaymentRequest.java

```java
package {$ROOT}.external.payment.model.request;

import lombok.Builder;

@Builder
public record PaymentRequest(
    Long orderId,
    Long amount,
    String paymentMethod
) {}
```

### external/payment/model/response/PaymentResponse.java

```java
package {$ROOT}.external.payment.model.response;

import lombok.Builder;

@Builder
public record PaymentResponse(
    String transactionId,
    String status,
    Long amount
) {}
```

---

## 템플릿 치환 규칙

| 플레이스홀더 | 설명 |
|-------------|------|
| `{$ROOT}` | 실제 그룹 ID (예: com.example) |
| `{$AppName}` | 실제 애플리케이션 이름 |
| `{$JavaVersion}` | Java 버전 (기본값: 25) |
| `{$SpringBootVersion}` | Spring Boot 버전 (기본값: 4.0.1) |
| `{$LombokVersion}` | Lombok 버전 (기본값: 1.18.42) |