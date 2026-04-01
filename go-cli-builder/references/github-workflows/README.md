# GitHub Actions Workflows for Go CLI

This directory contains example GitHub Actions workflows for Go CLI projects.

## Files

### ci.yml
Continuous Integration workflow that runs on every push and pull request.

**Features:**
- Runs on `feature/**` and `fix/**` branches
- Sets up Go 1.26
- Downloads dependencies
- Runs all tests (`go test ./...`)
- Builds the binary
- Runs linting (`go vet`)

**Triggers:**
- Push to `feature/*` or `fix/*` branches
- Pull requests to `feature/*` or `fix/*` branches

### release.yml
Automated release workflow using GoReleaser.

**Features:**
- Triggers on push to `main` branch
- Uses GoReleaser for automated releases
- Creates GitHub releases with binaries for multiple platforms
- Publishes to GitHub Releases page

**Requirements:**
- `GITHUB_TOKEN` secret (automatically provided by GitHub Actions)
- `.goreleaser.yaml` file in project root
- Git tags for versioning (e.g., `v1.0.0`)

## Setup

1. Copy these files to your project's `.github/workflows/` directory

2. Update `go-version` if needed (currently 1.26)

3. Update build path if your main package is not in `./cmd/`:
   ```yaml
   # In ci.yml
   - name: Build
     run: go build -o myapp .
   # or
   - name: Build
     run: go build -o myapp ./main.go
   ```

4. Create `.goreleaser.yaml` for release workflow:
   ```yaml
   project_name: myapp
   builds:
     - binary: myapp
       goos:
         - linux
         - darwin
         - windows
       goarch:
         - amd64
         - arm64
   archives:
     - format: tar.gz
       format_overrides:
         - goos: windows
           format: zip
   ```

5. Create and push a tag to trigger release:
   ```bash
   git tag -a v1.0.0 -m "First release"
   git push origin v1.0.0
   ```

## Customization

### Add More Checks

Add static analysis tools to `ci.yml`:

```yaml
- name: Run staticcheck
  uses: dominikh/staticcheck-action@v1.3.0
  with:
    version: "2023.1.7"

- name: Run golint
  run: |
    go install golang.org/x/lint/golint@latest
    golint ./...
```

### Add Security Scanning

```yaml
- name: Run Gosec Security Scanner
  uses: securego/gosec@master
  with:
    args: ./...
```

### Matrix Testing

Test against multiple Go versions:

```yaml
strategy:
  matrix:
    go-version: ['1.21', '1.22', '1.26']
    
steps:
  - uses: actions/setup-go@v5
    with:
      go-version: ${{ matrix.go-version }}
```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GoReleaser Documentation](https://goreleaser.com/)
- [setup-go Action](https://github.com/actions/setup-go)
