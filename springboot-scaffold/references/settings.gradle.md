# settings.gradle 템플릿 (버전 정의 포함)

```groovy
pluginManagement {
    def javaVersion = project.findProperty('java_version') ?: '25'
    def springBootVersion = project.findProperty('spring_boot_version') ?: '4.0.5'
    def lombokVersion = project.findProperty('lombok_version') ?: '1.18.42'
    def openapiVersion = project.findProperty('openapi_version') ?: '2.8.4'

    ext {
        set('javaVersion', javaVersion)
        set('springBootVersion', springBootVersion)
        set('lombokVersion', lombokVersion)
        set('openapiVersion', openapiVersion)
    }
}

rootProject.name = '{$AppName}'
```