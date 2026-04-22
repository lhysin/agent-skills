---
name: springboot-scaffold
description: |
  스프링부트 프로젝트 스캐폴딩 자동화 스킬. 사용자가 "스프링부트 프로젝트 생성", "스프링부트 스캐폴딩", "새 스프링부트 앱 만들기", "spring boot scaffolding" 등이라고 말하거나 요청할 때 사용.
  도메인 구조(order)와 외부 연동(payment) 설정 파일(build.gradle, application.yml)도 함께 생성. ROOT와 AppName 필수.
  반드시 ROOT와 AppName 파라미터가 모두 제공되어야만 구동됨.
triggers:
  - "스프링부트 프로젝트 생성"
  - "스프링부트 스캐폴딩"
  - "새 스프링부트 앱"
  - "spring boot scaffolding"
  - "스프링부트 프로젝트 구조"
---

# 스프링부트 스캐폴딩 스킬

## 템플릿 파일
- `references/build.gradle.md` - build.gradle 템플릿 (actuator 포함)
- `references/settings.gradle.md` - settings.gradle 템플릿
- `references/gradle.properties.md` - gradle.properties 템플릿 (버전 관리)
- `references/java.md` - Java 클래스 템플릿
- `references/test.md` - 테스트 클래스 템플릿
- `references/application.yml.md` - application.yml 템플릿 (default, dev, prod + actuator)
- `references/gitignore.md` - .gitignore 템플릿
- `references/readme.md` - README.md 템플릿

## 필수 파라미터
- **ROOT**: 그룹 ID (필수, 없으면 구동 안함)
- **AppName**: SpringBootApplication 클래스명 (필수, 없으면 구동 안함)

## 선택적 파라미터 (기본값 있음)
| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `JavaVersion` | `25` | Java 버전 |
| `Skeleton` | `on` | 스켈레톤 파일 생성 여부 (on/off) |

## 스켈레톤 on/off 동작
- **on**: `domain/order`, `external/payment` 포함하여 전체 생성
- **off**: 기본 디렉토리 구조만 생성

## 프로젝트 구조

```
<ROOT>/
├── build.gradle
├── settings.gradle
├── gradle.properties
├── .gitignore
├── README.md
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── <ROOT>/
│   │   │       ├── <AppName>SpringBootApplication.java
│   │   │       ├── common/
│   │   │       │   ├── advice/
│   │   │       │   │   └── GlobalExceptionHandler.java
│   │   │       │   └── exception/
│   │   │       │       ├── BaseException.java
│   │   │       │       └── ErrorCode.java
│   │   │       ├── config/
│   │   │       │   └── OpenApiConfig.java
│   │   │       ├── domain/
│   │   │       │   └── order/
│   │   │       │       ├── controller/OrderController.java
│   │   │       │       ├── service/OrderService.java
│   │   │       │       ├── repository/OrderRepository.java
│   │   │       │       ├── entity/Order.java
│   │   │       │       └── dto/OrderDto.java
│   │   │       └── external/
│   │   │           └── payment/
│   │   │               ├── client/PaymentClient.java
│   │   │               └── model/
│   │   │                   ├── request/PaymentRequest.java
│   │   │                   └── response/PaymentResponse.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       └── application-prod.yml
│   └── test/
│       └── java/
│           └── <ROOT>/
│               └── domain/
│                   └── order/
│                       └── service/
│                           └── OrderServiceTest.java
```

## 템플릿 치환 규칙
- `{$ROOT}` → 실제 ROOT 값
- `{$AppName}` → 실제 AppName 값

## 동작 플로우
1. ROOT와 AppName 필수 파라미터 확인 (없으면 오류)
2. 선택적 파라미터 기본값 적용
3. 프로젝트 구조 생성 (디렉토리)
4. build.gradle, settings.gradle, gradle.properties, .gitignore, README.md 생성
5. application*.yml 파일 생성 (default, dev, prod + actuator)
6. common/exception, common/advice, config 클래스 생성
7. Skeleton이 on이면 order 도메인 + payment 외부 연동 + 테스트 클래스 생성
8. Skeleton이 off이면 기본 구조만 생성
9. 결과 요약 출력