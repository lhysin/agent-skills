# Go CLI Beginner Guide

This guide covers the fundamentals of building Go CLI tools with Cobra.

## Project Structure

```
myapp/
├── cmd/
│   ├── root.go          # Root command definition
│   ├── version.go       # Version subcommand
│   └── subcommand.go    # Other subcommands
├── internal/
│   ├── config/          # Configuration management
│   └── output/          # Output formatting utilities
├── main.go              # Entry point
├── go.mod
└── go.sum
```

## Install Dependencies

```bash
mkdir myapp && cd myapp
go mod init github.com/yourusername/myapp
go get github.com/spf13/cobra@latest
go get github.com/mattn/go-isatty
go get github.com/fatih/color      # Optional: colors
go get golang.org/x/term           # For password input
```

## Basic Root Command Template

```go
package cmd

import (
    "fmt"
    "os"

    "github.com/fatih/color"
    "github.com/mattn/go-isatty"
    "github.com/spf13/cobra"
)

var (
    jsonOutput bool
    quietMode  bool
    noColor    bool

    rootCmd = &cobra.Command{
        Use:   "myapp",
        Short: "Brief description of what myapp does",
        Long: `A longer description that spans multiple lines
and likely contains examples.`,
        Example: `  myapp input.txt
  myapp --json output.json`,
        RunE: func(cmd *cobra.Command, args []string) error {
            return run(args)
        },
    }
)

func init() {
    rootCmd.PersistentFlags().BoolVar(&jsonOutput, "json", false, "Output in JSON format")
    rootCmd.PersistentFlags().BoolVarP(&quietMode, "quiet", "q", false, "Suppress non-essential output")
    rootCmd.PersistentFlags().BoolVar(&noColor, "no-color", false, "Disable colored output")
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}

func isInteractive() bool {
    return isatty.IsTerminal(os.Stdout.Fd()) ||
           isatty.IsCygwinTerminal(os.Stdout.Fd())
}
```

## Handle Missing Arguments

```go
RunE: func(cmd *cobra.Command, args []string) error {
    if len(args) == 0 {
        fmt.Fprintln(os.Stderr, "Error: requires at least one file argument")
        fmt.Fprintf(os.Stderr, "Usage: %s [flags] <file>\n\n", cmd.UseLine())
        fmt.Fprintln(os.Stderr, "For more help: myapp --help")
        os.Exit(1)
    }
    return run(args)
},
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Network error |

## Output Streams

- **stdout**: Primary output, machine-readable content
- **stderr**: Log messages, errors, progress

```go
fmt.Println("result data")                      // stdout
fmt.Fprintln(os.Stderr, "Error: file not found") // stderr
```

## Quick Start

```bash
# 1. Create project directory
mkdir myapp && cd myapp

# 2. Initialize Go module
go mod init github.com/yourusername/myapp

# 3. Install dependencies
go get github.com/spf13/cobra@latest
go get github.com/mattn/go-isatty

# 4. Create structure
mkdir -p cmd internal/config internal/output

# 5. Copy templates
cp references/root-template.go cmd/root.go
```

Then edit `cmd/root.go` to customize for your application!

For advanced topics like authentication, interactive prompts, and production deployment, see the main SKILL.md.