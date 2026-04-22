# .gitignore 템플릿

```
# Gradle
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

# Build
*.class
*.jar
*.war
*.ear
*.zip
*.tar.gz
*.rar

# Test
test-results/
/coverage/
*.class

# Misc
*.bak
*.tmp
*.orig
