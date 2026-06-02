# Gradle Wrapper Notes

`scripts/scaffold.py` is responsible for wrapper generation.

Preferred command inside the generated project:

```bash
gradle wrapper --gradle-version 9.4.1
chmod +x gradlew
```

The generator runs this automatically when:

- `--wrapper auto` is used and a local `gradle` command is available.
- `--wrapper required` is used and a local `gradle` command is available.

Validation behavior:

- Missing `gradlew`, `gradlew.bat`, or `gradle/wrapper/gradle-wrapper.properties` is a warning by default.
- Missing wrapper files become an error when validation is run with `--strict-wrapper`.

Do not handcraft `gradle-wrapper.jar` in the skill body. Let Gradle generate it, or return the generator warning so the user can run the wrapper command locally.
