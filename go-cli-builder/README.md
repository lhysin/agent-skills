# Go CLI Builder

A comprehensive skill for building high-quality command-line interface (CLI) tools using Go, following the [clig.dev](https://clig.dev/) guidelines.

## Overview

This skill helps you create professional, user-friendly CLI applications that follow industry best practices. It emphasizes **human-first design** while maintaining composability and robustness.

## Key Features

- **CLI Best Practices**: Based on [clig.dev](https://clig.dev/) guidelines
- **Cobra Framework**: Production-ready command structure
- **Context Management**: kubectl-style authentication contexts for multi-environment support
- **Authentication**: API keys, tokens, OAuth support
- **TTY Detection**: Smart output based on terminal capabilities
- **JSON Output**: Machine-readable output support
- **Signal Handling**: Graceful shutdown on Ctrl+C

## Quick Start

### 1. Install Dependencies

```bash
go get github.com/spf13/cobra@latest
go get github.com/mattn/go-isatty
go get github.com/fatih/color  # Optional, for colors
```

### 2. Create Project Structure

```bash
mkdir myapp && cd myapp
go mod init github.com/yourusername/myapp
mkdir -p cmd internal/config internal/output
```

### 3. Copy Root Template

```bash
cp references/root-template.go cmd/root.go
```

### 4. Customize and Build

Edit `cmd/root.go` to customize for your application, then build:

```bash
go build -o myapp
./myapp --help
```

## Core Principles (from clig.dev)

### 1. Human-First Design
- Design for humans first, even if also used programmatically
- Provide clear error messages and suggestions
- Show helpful examples in help text

### 2. Composability
- Use stdout for data, stderr for messages
- Return proper exit codes (0 = success, non-zero = failure)
- Support JSON output with `--json`
- Work correctly in pipelines

### 3. Consistency
- Follow standard flag names (`-h`, `--help`, `--version`, etc.)
- Use noun-verb subcommand pattern (`docker container create`)
- Respect environment variables (`NO_COLOR`, `TERM`, `XDG_CONFIG_HOME`)

### 4. Robustness
- Handle Ctrl+C gracefully
- Set timeouts on network operations
- Validate inputs and provide helpful error messages
- Make operations idempotent where possible

## Authentication & Context Management

For APIs and services that require authentication, implement context-based management (like `kubectl`):

```bash
# Login to create a context
myapp login production --server=https://api.prod.com --api-key=KEY

# List all contexts
myapp context list

# Switch context
myapp context set staging

# Show current context
myapp context show

# Logout (clear credentials)
myapp logout
```

See [SKILL.md](SKILL.md) for complete implementation details.

## Project Structure

```
myapp/
├── cmd/
│   ├── root.go          # Root command with global flags
│   ├── version.go       # Version subcommand
│   ├── login.go         # Authentication
│   └── context.go       # Context management
├── internal/
│   ├── config/          # Configuration management
│   ├── output/          # Output formatting utilities
│   └── auth/            # Authentication utilities
├── main.go              # Entry point
└── go.mod
```

## Essential Checklist

Before releasing your CLI, verify:

- [ ] Exit code 0 on success, non-zero on failure
- [ ] Primary output to `stdout`, errors/messages to `stderr`
- [ ] `-h` and `--help` work everywhere
- [ ] `--version` displays version information
- [ ] `--json` flag for structured output
- [ ] TTY detection for colors and animations
- [ ] `NO_COLOR` environment variable respected
- [ ] Human-readable error messages
- [ ] Ctrl+C handled gracefully
- [ ] Secrets never read from flags
- [ ] Context management for multi-environment support (if applicable)

See [references/checklist.md](references/checklist.md) for the complete checklist.

## Common Patterns

### TTY Detection

```go
import "github.com/mattn/go-isatty"

func isInteractive() bool {
    return isatty.IsTerminal(os.Stdout.Fd())
}
```

### Color Control

```go
func shouldUseColor() bool {
    if os.Getenv("NO_COLOR") != "" {
        return false
    }
    if os.Getenv("TERM") == "dumb" {
        return false
    }
    return isInteractive()
}
```

### JSON Output

```go
if jsonOutput {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    enc.Encode(result)
} else {
    fmt.Printf("Name: %s\n", result.Name)
}
```

### Signal Handling

```go
ctx, cancel := context.WithCancel(context.Background())
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, os.Interrupt)

go func() {
    <-sigCh
    fmt.Fprintln(os.Stderr, "\nShutting down...")
    cancel()
}()
```

## Recommended Libraries

| Purpose | Library |
|---------|---------|
| CLI Framework | [Cobra](https://github.com/spf13/cobra) |
| TTY Detection | [go-isatty](https://github.com/mattn/go-isatty) |
| Colors | [color](https://github.com/fatih/color) |
| Progress Bars | [progressbar](https://github.com/schollz/progressbar) |
| Configuration | [Viper](https://github.com/spf13/viper) |

## Resources

- [SKILL.md](SKILL.md) - Complete skill documentation
- [references/checklist.md](references/checklist.md) - Quality checklist
- [references/examples.md](references/examples.md) - Code examples
- [references/root-template.go](references/root-template.go) - Starter template
- [clig.dev](https://clig.dev/) - Command Line Interface Guidelines

## Distribution

### Single Binary

```bash
# Linux
go build -o myapp-linux-amd64

# macOS
GOOS=darwin GOARCH=amd64 go build -o myapp-darwin-amd64

# Windows
GOOS=windows GOARCH=amd64 go build -o myapp-windows-amd64.exe
```

### Using goreleaser

```bash
go install github.com/goreleaser/goreleaser@latest
goreleaser release
```

## License

This skill is provided as-is for building CLI applications.

## Contributing

Follow the clig.dev guidelines when contributing examples or improvements.
