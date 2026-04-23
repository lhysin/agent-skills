# settings.gradle 템플릿 (버전 정의 포함)

```groovy
ext {
    java_version = project.findProperty('java_version') ?: '25'
    spring_boot_version = project.findProperty('spring_boot_version') ?: '4.0.5'
    lombok_version = project.findProperty('lombok_version') ?: '1.18.42'
    openapi_version = project.findProperty('openapi_version') ?: '2.8.4'
}

rootProject.name = '{$AppName}'
```