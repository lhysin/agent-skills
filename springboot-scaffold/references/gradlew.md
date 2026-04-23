# Gradle Wrapper

## Simple Template

Create gradlew by running:

```bash
gradle wrapper
```

Then make it executable:

```bash
chmod +x gradlew
```

## For Scaffolding Template

Since scaffolding cannot run `gradle wrapper` directly, use this minimal gradlew that downloads wrapper on first run:

```bash
#!/bin/sh

# Gradle Wrapper bootstrap
# Downloads wrapper jar on first run if not present

GRADLE_USER_HOME="${GRADLE_USER_HOME:-$HOME/.gradle}"
WRAPPER_JAR="$GRADLE_USER_HOME/wrapper/dists/gradle-8.14-bin/*/gradle-8.14/lib/gradle-wrapper.jar"

# If wrapper jar not found, bootstrap it
if [ ! -f "$WRAPPER_JAR" ] || [ ! -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    WRAPPER_URL="https://services.gradle.org/distributions/gradle-8.14-bin.zip"
    echo "Downloading Gradle wrapper..."
    mkdir -p "gradle/wrapper"
    curl -sL "$WRAPPER_URL" -o "/tmp/gradle-8.14-bin.zip"
    unzip -q "/tmp/gradle-8.14-bin.zip" -d "/tmp/" 2>/dev/null || true
    cp "/tmp/gradle-8.14/lib/gradle-wrapper-*.jar" "gradle/wrapper/gradle-wrapper.jar" 2>/dev/null || \
    cp "/tmp/gradle-8.14/lib/gradle-wrapper.jar" "gradle/wrapper/gradle-wrapper.jar" 2>/dev/null || true
fi

# Determine Java command
if [ -n "$JAVA_HOME" ] ; then
    JAVACMD="$JAVA_HOME/bin/java"
else
    JAVACMD="java"
fi

APP_HOME=$( cd "$( dirname "$0" )" && pwd )

exec "$JAVACMD" -classpath "$APP_HOME/gradle/wrapper/gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain "$@"
```

## Alternative: Download gradle-wrapper.jar directly

```bash
mkdir -p gradle/wrapper
curl -sL "https://raw.githubusercontent.com/gradle/gradle/v8.14.0/gradle/wrapper/gradle-wrapper.jar" -o gradle/wrapper/gradle-wrapper.jar
```