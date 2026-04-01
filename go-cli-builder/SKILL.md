---
name: go-cli-builder
description: Design and implement high-quality CLI tools using Go and Cobra, following clig.dev guidelines. Use for new CLI projects, code reviews, adding subcommands, help text, error handling, and all CLI-related work. Triggered by requests like "build Go CLI", "command-line tool", "Cobra project", "CLI code review", or "create CLI with flags".
---

# Go CLI Builder

A comprehensive skill for building high-quality command-line interface (CLI) tools using Go, following the [clig.dev](https://clig.dev/) guidelines.

## When to Use This Skill

- Starting a new Go CLI project from scratch
- Reviewing and improving existing Go CLI code against best practices
- Adding subcommands, flags, or help text to CLI tools
- Implementing error handling, output formatting, or user experience improvements
- Converting scripts into proper CLI tools

## Core Philosophy (from clig.dev)

### 1. Human-First Design
Design for humans first, even if your tool is also used programmatically. Modern CLIs should prioritize the human experience while maintaining composability.

### 2. Simple Parts That Work Together
Build small, modular programs with clean interfaces. Use standard UNIX mechanisms:
- stdin/stdout/stderr for I/O
- Signals for control
- Exit codes for success/failure reporting
- Plain text for piping; JSON for structured data

### 3. Consistency Across Programs
Terminal conventions are "hardwired into our fingers." Follow existing patterns to make your CLI intuitive and guessable. Break convention only when it significantly compromises usability.

### 4. Saying (Just) Enough
- Too little output: user wonders if the program is broken
- Too much output: user drowned in irrelevant information
- Find the balance through clear, concise communication

### 5. Ease of Discovery
Make your CLI self-documenting:
- Comprehensive help with examples first
- Suggest corrections for mistyped commands
- Recommend next steps in workflows
- Link to web documentation

### 6. Conversation as the Norm
CLI interaction is inherently conversational:
- Guide users back on track when they make mistakes
- Make intermediate state clear in multi-step processes
- Confirm before destructive operations

### 7. Robustness
- Handle unexpected input gracefully
- Make operations idempotent where possible
- Feel solid and responsive
- Fail fast with clear error messages

### 8. Empathy
CLI tools are a programmer's creative toolkit. Give users the feeling that you're on their side, want them to succeed, and have thought carefully about their problems.

## The Basics (Essential Rules)

**Get these wrong, and your program will be broken or very hard to use.**

### Use a CLI Argument Parsing Library

**For Go, use Cobra (recommended) or urfave/cli:**

```bash
go get github.com/spf13/cobra@latest
```

Cobra provides:
- Command and subcommand structure
- Flag parsing (short and long forms)
- Help text generation
- Shell completions
- Suggestions for mistyped commands

### Exit Codes

**Return zero on success, non-zero on failure:**

```go
// Success
os.Exit(0)

// General error
os.Exit(1)

// Specific errors (map to most important failure modes)
os.Exit(2) // Invalid arguments
os.Exit(3) // Configuration error
os.Exit(4) // Network error
```

### Output Streams

**stdout**: Primary output, machine-readable content
```go
fmt.Println("result data") // Goes to stdout
```

**stderr**: Log messages, errors, progress
```go
fmt.Fprintln(os.Stderr, "Error: file not found")
```

This ensures piping works correctly:
```bash
myapp | grep "pattern"  # stderr messages are displayed, not piped
```

## New CLI Project Workflow

### Step 1: Project Structure

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

### Step 2: Initialize Go Module

```bash
mkdir myapp && cd myapp
go mod init github.com/yourusername/myapp
go get github.com/spf13/cobra@latest
go get github.com/mattn/go-isatty  # TTY detection
go get github.com/fatih/color      # Optional: colors
```

### Step 3: Implement Root Command

Use `references/root-template.go` as your starting point. Key components:

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
    // Flags
    jsonOutput bool
    quietMode  bool
    noColor    bool
    
    rootCmd = &cobra.Command{
        Use:   "myapp",
        Short: "Brief description of what myapp does",
        Long: `A longer description that spans multiple lines
and likely contains examples and usage of using your application.

For example:
    myapp file.txt
    myapp --json output.json`,
        Example: `  # Process a single file
  myapp input.txt
  
  # Output as JSON
  myapp --json input.txt > output.json`,
        
        // Run executes when no subcommands are provided
        RunE: func(cmd *cobra.Command, args []string) error {
            return run(args)
        },
    }
)

func init() {
    // Global flags
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

func shouldUseColor() bool {
    if noColor {
        return false
    }
    if os.Getenv("NO_COLOR") != "" {
        return false
    }
    if os.Getenv("TERM") == "dumb" {
        return false
    }
    return isInteractive()
}
```

### Step 4: Handle Missing Arguments

Show concise help when arguments are required but not provided:

```go
RunE: func(cmd *cobra.Command, args []string) error {
    if len(args) == 0 {
        // Show concise help and exit
        fmt.Fprintln(os.Stderr, "Error: requires at least one file argument")
        fmt.Fprintf(os.Stderr, "Usage: %s [flags] <file>\n\n", cmd.UseLine())
        fmt.Fprintln(os.Stderr, "For more help: myapp --help")
        os.Exit(1)
    }
    return run(args)
},
```

## Help Text Design

### Concise Help (Default)

When run without required arguments, show:
- Brief description
- 1-2 common examples
- Common flags
- Pointer to full help

```go
var rootCmd = &cobra.Command{
    Use:   "myapp [flags] <file>",
    Short: "Process files and generate reports",
    Long: `myapp processes input files and generates formatted reports.

Examples:
    myapp report.txt              # Basic processing
    myapp --format=json data.csv  # JSON output

Use "myapp --help" for all options.`,
}
```

### Full Help (--help)

Cobra auto-generates this, but customize it:

```go
rootCmd.SetUsageTemplate(`Usage:{{if .Runnable}}
  {{.UseLine}}{{end}}{{if .HasAvailableSubCommands}}
  {{.CommandPath}} [command]{{end}}{{if gt (len .Aliases) 0}}

Aliases:
  {{.NameAndAliases}}{{end}}{{if .HasExample}}

Examples:
{{.Example}}{{end}}{{if .HasAvailableSubCommands}}

Available Commands:{{range .Commands}}{{if (or .IsAvailableCommand (eq .Name "help"))}}
  {{rpad .Name .NamePadding }} {{.Short}}{{end}}{{end}}{{end}}{{if .HasAvailableLocalFlags}}

Flags:
{{.LocalFlags.FlagUsages | trimTrailingWhitespaces}}{{end}}{{if .HasAvailableInheritedFlags}}

Global Flags:
{{.InheritedFlags.FlagUsages | trimTrailingWhitespaces}}{{end}}{{if .HasHelpSubCommands}}

Additional help topics:{{range .Commands}}{{if .IsAdditionalHelpTopicCommand}}
  {{rpad .CommandPath .CommandPathPadding}} {{.Short}}{{end}}{{end}}{{end}}{{if .HasAvailableSubCommands}}

Use "{{.CommandPath}} [command] --help" for more information about a command.{{end}}
`)
```

### Command Suggestions

Enable automatic suggestions for mistyped commands:

```go
rootCmd.SuggestionsMinimumDistance = 2
// Cobra automatically suggests corrections
```

## Output Design

### TTY Detection

**Always detect if running in an interactive terminal:**

```go
import "github.com/mattn/go-isatty"

func isInteractive() bool {
    return isatty.IsTerminal(os.Stdout.Fd()) || 
           isatty.IsCygwinTerminal(os.Stdout.Fd())
}
```

### Color Control

**Disable color when:**
- stdout/stderr is not a TTY
- `NO_COLOR` environment variable is set (any non-empty value)
- `TERM=dumb`
- `--no-color` flag passed
- `MYAPP_NO_COLOR` environment variable set

```go
func shouldUseColor() bool {
    if noColor || os.Getenv("MYAPP_NO_COLOR") != "" {
        return false
    }
    if os.Getenv("NO_COLOR") != "" {
        return false
    }
    if os.Getenv("TERM") == "dumb" {
        return false
    }
    if !isInteractive() {
        return false
    }
    return true
}
```

### JSON Output

**Always support `--json` for structured output:**

```go
if jsonOutput {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    enc.Encode(result)
} else {
    // Human-readable output
    fmt.Printf("Name: %s\n", result.Name)
    fmt.Printf("Status: %s\n", result.Status)
}
```

This enables piping to `jq` and integration with web services.

### Plain Output

**Support `--plain` for script-friendly tabular output:**

When human-readable formatting breaks line-based processing:

```go
if plainOutput {
    // One record per line
    fmt.Printf("%s\t%s\t%s\n", name, status, size)
} else {
    // Multi-line, formatted for humans
    fmt.Printf("Name:   %s\n", name)
    fmt.Printf("Status: %s\n", status)
    fmt.Printf("Size:   %s\n", size)
}
```

### Progress Indication

**Show progress for operations >100ms:**

```go
import "github.com/schollz/progressbar/v3"

if isInteractive() && !quietMode {
    bar := progressbar.NewOptions64(total,
        progressbar.OptionSetDescription("Processing..."),
        progressbar.OptionShowCount(),
        progressbar.OptionShowBytes(true),
    )
    
    for i := int64(0); i < total; i++ {
        bar.Add(1)
        // ... do work
    }
} else {
    fmt.Fprintf(os.Stderr, "Processing %d items...\n", total)
}
```

### No Animations in Non-TTY

```go
if !isInteractive() {
    // No progress bars, no spinners
    fmt.Fprintf(os.Stderr, "Starting operation...\n")
    // ... do work
    fmt.Fprintf(os.Stderr, "Complete\n")
}
```

### State Change Reporting

**Tell users what happened:**

```go
// Bad: no output
os.WriteFile(filename, data, 0644)

// Good: report state change
if err := os.WriteFile(filename, data, 0644); err != nil {
    return fmt.Errorf("failed to write %s: %w", filename, err)
}
if !quietMode {
    fmt.Fprintf(os.Stderr, "Created %s (%d bytes)\n", filename, len(data))
}
```

### Suggest Next Commands

**Guide users through workflows:**

```go
fmt.Println("Repository initialized.")
fmt.Println()
fmt.Println("Next steps:")
fmt.Println("  1. Add files:    myapp add <file>")
fmt.Println("  2. Commit:       myapp commit -m 'Initial commit'")
fmt.Println("  3. View status:  myapp status")
```

## Error Handling

### Human-Readable Errors

**Rewrite technical errors for humans:**

```go
// Bad
return fmt.Errorf("open %s: %w", filename, err)

// Good
cmd.SilenceErrors = true  // Don't print error twice
if os.IsNotExist(err) {
    fmt.Fprintf(os.Stderr, "Error: File not found: %s\n", filename)
    fmt.Fprintf(os.Stderr, "\nMake sure the file exists and you have permission to read it.\n")
    os.Exit(1)
}
```

### High Signal-to-Noise Ratio

**Group similar errors:**

```go
// Bad: multiple similar error lines
for _, file := range files {
    if err := process(file); err != nil {
        fmt.Fprintf(os.Stderr, "Error: failed to process %s: %v\n", file, err)
    }
}

// Good: grouped errors
var failedFiles []string
for _, file := range files {
    if err := process(file); err != nil {
        failedFiles = append(failedFiles, file)
    }
}

if len(failedFiles) > 0 {
    fmt.Fprintf(os.Stderr, "Error: Failed to process %d files:\n", len(failedFiles))
    for _, file := range failedFiles {
        fmt.Fprintf(os.Stderr, "  - %s\n", file)
    }
    fmt.Fprintf(os.Stderr, "\nCheck file permissions and try again.\n")
    os.Exit(1)
}
```

### Important Information Last

**Users look at the end of output:**

```go
// Bad: error at top, details below
fmt.Fprintf(os.Stderr, "Error: permission denied\n")
fmt.Fprintf(os.Stderr, "File: /etc/config.txt\n")
fmt.Fprintf(os.Stderr, "User: currentuser\n")

// Good: context first, error last
fmt.Fprintf(os.Stderr, "File: /etc/config.txt\n")
fmt.Fprintf(os.Stderr, "User: currentuser\n")
fmt.Fprintf(os.Stderr, "Error: permission denied\n")
```

### Debug Information

**Only show debug info with --debug flag:**

```go
if debug {
    fmt.Fprintf(os.Stderr, "[DEBUG] Request: %+v\n", req)
    fmt.Fprintf(os.Stderr, "[DEBUG] Response: %+v\n", resp)
}
```

### Unexpected Errors

**Provide bug report instructions:**

```go
if err != nil {
    fmt.Fprintf(os.Stderr, "Unexpected error: %v\n", err)
    fmt.Fprintf(os.Stderr, "\nThis appears to be a bug. Please report it at:\n")
    fmt.Fprintf(os.Stderr, "https://github.com/user/myapp/issues/new?title=bug:...\n")
    fmt.Fprintf(os.Stderr, "\nRun with --debug to see full stack trace.\n")
    os.Exit(1)
}
```

## Arguments and Flags

### Prefer Flags to Arguments

**Flags are clearer and more extensible:**

```bash
# Bad: unclear what arguments mean
myapp file.txt 100 true

# Good: self-documenting
myapp --file=file.txt --count=100 --verbose
```

### Full-Length Flags Required

**Always provide both short and long forms:**

```go
rootCmd.Flags().BoolP("verbose", "v", false, "Enable verbose output")
rootCmd.Flags().StringP("output", "o", "", "Output file path")
```

### Standard Flag Names

| Flag | Meaning |
|------|---------|
| `-a`, `--all` | All items |
| `-d`, `--debug` | Debug output |
| `-f`, `--force` | Force action |
| `-h`, `--help` | Help (only means help) |
| `-n`, `--dry-run` | Dry run - show what would happen |
| `--json` | JSON output |
| `-o`, `--output` | Output file |
| `-p`, `--port` | Port number |
| `-q`, `--quiet` | Quiet mode |
| `-u`, `--user` | User name/ID |
| `--version` | Version information |

### Multiple Arguments

**Fine for simple file operations:**

```go
// Good: multiple files to same operation
myapp rm file1.txt file2.txt file3.txt
myapp rm *.txt  // Works with globbing
```

### Two Arguments for Different Things

**Avoid unless it's a very common pattern:**

```go
// Okay: cp is universally understood
cp source.txt destination.txt

// Bad: unclear order
myapp file1.txt file2.txt  // Which is input? Which is output?
```

### Secrets Handling

**Never read secrets from flags:**

```go
// BAD: leaks to ps output and shell history
cmd.Flags().String("password", "", "Database password")

// GOOD: read from file
cmd.Flags().String("password-file", "", "Path to file containing password")

// Read password from file
passwordBytes, err := os.ReadFile(passwordFile)
if err != nil {
    return fmt.Errorf("failed to read password file: %w", err)
}
password := strings.TrimSpace(string(passwordBytes))
```

### stdin/stdout as Files

**Support `-` for stdin/stdout:**

```go
// Read from stdin
if inputFile == "-" {
    data, err := io.ReadAll(os.Stdin)
    // ...
}

// Write to stdout  
if outputFile == "-" {
    writer = os.Stdout
} else {
    writer, err = os.Create(outputFile)
}
```

Usage:
```bash
curl https://example.com/data.json | myapp --input=-
myapp --output=- | jq '.results'
```

### Optional Flag Values

**Allow "none" for optional values:**

```go
// ssh -F takes optional config file
// ssh -F none runs with no config
if configFile == "none" {
    // Don't load config
} else if configFile != "" {
    // Load specified config
} else {
    // Load default config
}
```

### Order Independence

**Make flags work before and after subcommands:**

```bash
myapp --debug subcommand
myapp subcommand --debug  # Should also work
```

## Interactivity

### Only Prompt in TTY Mode

```go
if isInteractive() && !noInput {
    // Prompt for missing values
    fmt.Print("Enter your name: ")
    fmt.Scanln(&name)
} else {
    // Fail with clear instruction
    return fmt.Errorf("name is required (use --name flag)")
}
```

### --no-input Flag

```go
var noInput bool
rootCmd.Flags().BoolVar(&noInput, "no-input", false, "Disable interactive prompts")

// In command logic:
if noInput && name == "" {
    return fmt.Errorf("--name is required when using --no-input")
}
```

### Password Input

**Don't echo passwords:**

```go
import "golang.org/x/term"

func readPassword(prompt string) (string, error) {
    fmt.Print(prompt)
    bytePassword, err := term.ReadPassword(int(os.Stdin.Fd()))
    if err != nil {
        return "", err
    }
    fmt.Println() // Newline after password
    return string(bytePassword), nil
}
```

### Dangerous Operations

**Confirm before destructive actions:**

```go
// Check if running interactively
if isInteractive() && !force {
    fmt.Fprintf(os.Stderr, "This will delete %d files permanently.\n", count)
    fmt.Fprint(os.Stderr, "Are you sure? [y/N]: ")
    
    var response string
    fmt.Scanln(&response)
    if strings.ToLower(response) != "y" && strings.ToLower(response) != "yes" {
        fmt.Fprintln(os.Stderr, "Aborted.")
        return nil
    }
}
```

## Subcommands

### Structure

```go
// root.go
var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "My application",
}

// subcommand.go
var createCmd = &cobra.Command{
    Use:   "create [name]",
    Short: "Create a new resource",
    Example: `  myapp create myresource
  myapp create --type=advanced myresource`,
    RunE: func(cmd *cobra.Command, args []string) error {
        // Implementation
    },
}

func init() {
    rootCmd.AddCommand(createCmd)
    createCmd.Flags().String("type", "basic", "Resource type")
}
```

### Naming Convention

Use `noun verb` pattern (like Docker):

```bash
myapp container create
myapp container start
myapp container stop
myapp image pull
myapp image push
```

### Consistency

- Same flag names across subcommands
- Similar output formatting
- Consistent help style

## Robustness

### Responsive > Fast

**Print something within 100ms:**

```go
// Start a spinner or message immediately
fmt.Fprintf(os.Stderr, "Starting...\n")

// Do work
result, err := longRunningOperation()
```

### Timeouts

**Always set timeouts:**

```go
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
if err != nil {
    return err
}

client := &http.Client{Timeout: 30 * time.Second}
resp, err := client.Do(req)
```

### Recoverable Operations

**Make it safe to run again:**

```go
// Check if already done before doing work
if _, err := os.Stat(outputFile); err == nil {
    if !force {
        return fmt.Errorf("output file already exists (use --force to overwrite)")
    }
}
```

### Signal Handling

**Handle Ctrl+C gracefully:**

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel()

// Set up signal handling
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

go func() {
    <-sigCh
    fmt.Fprintln(os.Stderr, "\nInterrupt received. Cleaning up...")
    cancel()
    
    // Wait for second interrupt
    <-sigCh
    fmt.Fprintln(os.Stderr, "\nForced exit.")
    os.Exit(1)
}()

// Do work with ctx
err := doWork(ctx)
```

Example output:
```
^CGracefully stopping... (press Ctrl+C again to force)
```

## Configuration

### XDG Specification

Follow [XDG Base Directory Spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html):

```go
func configDir() string {
    if dir := os.Getenv("XDG_CONFIG_HOME"); dir != "" {
        return filepath.Join(dir, "myapp")
    }
    home, _ := os.UserHomeDir()
    return filepath.Join(home, ".config", "myapp")
}
```

### Precedence (High to Low)

1. Flags
2. Shell environment variables
3. Project-level config (`.myapprc`, `.env`)
4. User-level config (`~/.config/myapp/`)
5. System-wide config (`/etc/myapp/`)

### Config Libraries

**Use Viper for complex configuration:**

```bash
go get github.com/spf13/viper
```

```go
import "github.com/spf13/viper"

func initConfig() {
    viper.SetConfigName("myapp")
    viper.SetConfigType("yaml")
    viper.AddConfigPath(".")
    viper.AddConfigPath(configDir())
    
    if err := viper.ReadInConfig(); err != nil {
        // Config file not required
    }
    
    // Bind env vars
    viper.BindEnv("api_key", "MYAPP_API_KEY")
}
```

## Environment Variables

### Standard Variables to Check

| Variable | Purpose |
|----------|---------|
| `NO_COLOR` / `FORCE_COLOR` | Color control |
| `DEBUG` | Verbose output |
| `EDITOR` | Text editor |
| `HTTP_PROXY`, `HTTPS_PROXY` | Network proxy |
| `PAGER` | Output pager (e.g., `less`) |
| `HOME` | Home directory |
| `TMPDIR` | Temporary files |
| `TERM` | Terminal type |

### Custom Variables

```go
// MYAPP_DEBUG for app-specific debug mode
if os.Getenv("MYAPP_DEBUG") != "" {
    debug = true
}

// MYAPP_NO_COLOR for app-specific color override
if os.Getenv("MYAPP_NO_COLOR") != "" {
    noColor = true
}
```

### .env Files

**Read `.env` for project-specific settings:**

```bash
go get github.com/joho/godotenv
```

```go
import "github.com/joho/godotenv"

func loadEnv() {
    // Load .env file if it exists
    godotenv.Load()
}
```

## Distribution

### Single Binary

**Go's strength - distribute as single binary:**

```bash
# Build for multiple platforms
go build -o myapp-linux-amd64
GOOS=darwin GOARCH=amd64 go build -o myapp-darwin-amd64
GOOS=windows GOARCH=amd64 go build -o myapp-windows-amd64.exe
```

### Use goreleaser

**Automate releases:**

```bash
go install github.com/goreleaser/goreleaser@latest
```

`.goreleaser.yaml`:
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

### Uninstall Instructions

**Make uninstall easy:**

```bash
# Installation
curl -sSL https://example.com/install.sh | sh

# Uninstallation  
myapp uninstall
# or
rm /usr/local/bin/myapp
rm -rf ~/.config/myapp
```

## Authentication and Context Management

For CLI tools that need to connect to APIs or services (like `kubectl`), implement context-based authentication:

### Context Pattern (kubectl-style)

Store multiple authentication contexts and allow users to switch between them:

```
~/.config/myapp/
├── config              # Main config with current context
├── contexts/
│   ├── production.json
│   ├── staging.json
│   └── development.json
└── credentials/
    └── tokens.json     # Encrypted or obfuscated tokens
```

### Configuration Structure

```go
package config

// Context represents a connection context
type Context struct {
    Name       string            `json:"name"`
    Server     string            `json:"server"`
    APIKey     string            `json:"api_key,omitempty"`
    Token      string            `json:"token,omitempty"`
    Username   string            `json:"username,omitempty"`
    AuthType   string            `json:"auth_type"` // apikey, token, oauth
    Headers    map[string]string `json:"headers,omitempty"`
    Insecure   bool              `json:"insecure,omitempty"`
}

// Config represents the main configuration
type Config struct {
    CurrentContext string              `json:"current_context"`
    Contexts       map[string]*Context `json:"contexts"`
}

func (c *Config) GetCurrentContext() (*Context, error) {
    if c.CurrentContext == "" {
        return nil, fmt.Errorf("no context selected. Run 'myapp context set <name>'")
    }
    
    ctx, ok := c.Contexts[c.CurrentContext]
    if !ok {
        return nil, fmt.Errorf("context '%s' not found", c.CurrentContext)
    }
    
    return ctx, nil
}

func (c *Config) SetContext(name string) error {
    if _, ok := c.Contexts[name]; !ok {
        available := make([]string, 0, len(c.Contexts))
        for n := range c.Contexts {
            available = append(available, n)
        }
        return fmt.Errorf("context '%s' not found. Available: %v", name, available)
    }
    
    c.CurrentContext = name
    return nil
}
```

### Login Command

```go
package cmd

var loginCmd = &cobra.Command{
    Use:   "login [context-name]",
    Short: "Authenticate and create a new context",
    Example: `  # Login with API key
  myapp login production --api-key=YOUR_API_KEY

  # Login with token (interactive)
  myapp login staging --token

  # Login to specific server
  myapp login dev --server=https://dev.example.com --api-key=KEY`,
    RunE: func(cmd *cobra.Command, args []string) error {
        if len(args) == 0 {
            return fmt.Errorf("context name required")
        }
        
        contextName := args[0]
        server, _ := cmd.Flags().GetString("server")
        apiKey, _ := cmd.Flags().GetString("api-key")
        useToken, _ := cmd.Flags().GetBool("token")
        username, _ := cmd.Flags().GetString("username")
        insecure, _ := cmd.Flags().GetBool("insecure")
        
        // Get credentials interactively if not provided
        if apiKey == "" && !useToken {
            return fmt.Errorf("--api-key or --token required")
        }
        
        var token string
        if useToken {
            var err error
            token, err = readPassword("Token: ")
            if err != nil {
                return err
            }
        }
        
        // Create context
        ctx := &config.Context{
            Name:     contextName,
            Server:   server,
            APIKey:   apiKey,
            Token:    token,
            Username: username,
            AuthType: determineAuthType(apiKey, token),
            Insecure: insecure,
        }
        
        // Test connection
        fmt.Fprintf(os.Stderr, "Authenticating to %s...\n", server)
        if err := testConnection(ctx); err != nil {
            return fmt.Errorf("authentication failed: %w", err)
        }
        
        // Save context
        cfg, _ := config.Load()
        if cfg.Contexts == nil {
            cfg.Contexts = make(map[string]*config.Context)
        }
        cfg.Contexts[contextName] = ctx
        cfg.CurrentContext = contextName
        
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save context: %w", err)
        }
        
        printSuccess(fmt.Sprintf("Logged in to '%s' (%s)", contextName, server))
        fmt.Fprintf(os.Stderr, "\nCurrent context: %s\n", contextName)
        
        return nil
    },
}

func init() {
    loginCmd.Flags().String("server", "", "Server URL (required)")
    loginCmd.Flags().String("api-key", "", "API key for authentication")
    loginCmd.Flags().Bool("token", false, "Use token authentication (will prompt)")
    loginCmd.Flags().String("username", "", "Username (if required)")
    loginCmd.Flags().Bool("insecure", false, "Allow insecure server connections")
    loginCmd.MarkFlagRequired("server")
}

func testConnection(ctx *config.Context) error {
    // Make a test API call
    client := createHTTPClient(ctx)
    resp, err := client.Get(ctx.Server + "/api/v1/ping")
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != 200 {
        return fmt.Errorf("server returned %d", resp.StatusCode)
    }
    
    return nil
}
```

### Context Commands

```go
package cmd

// myapp context list
var contextListCmd = &cobra.Command{
    Use:   "list",
    Short: "List all contexts",
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }
        
        if len(cfg.Contexts) == 0 {
            fmt.Fprintln(os.Stderr, "No contexts configured.")
            fmt.Fprintln(os.Stderr, "\nRun 'myapp login <name>' to add a context.")
            return nil
        }
        
        table := output.NewTable("NAME", "SERVER", "AUTH TYPE", "CURRENT")
        for name, ctx := range cfg.Contexts {
            current := ""
            if name == cfg.CurrentContext {
                current = "*"
            }
            table.AddRow(name, ctx.Server, ctx.AuthType, current)
        }
        
        return table.Print()
    },
}

// myapp context set <name>
var contextSetCmd = &cobra.Command{
    Use:   "set [name]",
    Short: "Set the current context",
    Example: `  myapp context set production
  myapp context set staging`,
    Args: cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }
        
        if err := cfg.SetContext(args[0]); err != nil {
            return err
        }
        
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save config: %w", err)
        }
        
        printSuccess(fmt.Sprintf("Switched to context '%s'", args[0]))
        return nil
    },
}

// myapp context delete <name>
var contextDeleteCmd = &cobra.Command{
    Use:   "delete [name]",
    Short: "Delete a context",
    Example: `  myapp context delete old-staging`,
    Args: cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }
        
        name := args[0]
        
        // Confirm deletion
        if !force {
            confirmed, err := Confirm(fmt.Sprintf("Delete context '%s'?", name))
            if err != nil {
                return err
            }
            if !confirmed {
                fmt.Fprintln(os.Stderr, "Cancelled.")
                return nil
            }
        }
        
        delete(cfg.Contexts, name)
        
        // If deleted context was current, clear it
        if cfg.CurrentContext == name {
            cfg.CurrentContext = ""
            fmt.Fprintln(os.Stderr, "Note: Deleted context was current. Run 'myapp context set <name>' to select another.")
        }
        
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save config: %w", err)
        }
        
        printSuccess(fmt.Sprintf("Deleted context '%s'", name))
        return nil
    },
}

// myapp context show
var contextShowCmd = &cobra.Command{
    Use:   "show",
    Short: "Show current context details",
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }
        
        ctx, err := cfg.GetCurrentContext()
        if err != nil {
            return err
        }
        
        if jsonOutput {
            return outputJSON(ctx)
        }
        
        fmt.Printf("Name:     %s\n", ctx.Name)
        fmt.Printf("Server:   %s\n", ctx.Server)
        fmt.Printf("Auth:     %s\n", ctx.AuthType)
        if ctx.Username != "" {
            fmt.Printf("Username: %s\n", ctx.Username)
        }
        fmt.Printf("Insecure: %t\n", ctx.Insecure)
        
        return nil
    },
}

var contextCmd = &cobra.Command{
    Use:   "context",
    Short: "Manage authentication contexts",
    Long:  `Manage multiple authentication contexts for different servers or environments.`,
}

func init() {
    contextCmd.AddCommand(contextListCmd)
    contextCmd.AddCommand(contextSetCmd)
    contextCmd.AddCommand(contextDeleteCmd)
    contextCmd.AddCommand(contextShowCmd)
    
    rootCmd.AddCommand(contextCmd)
}
```

### Logout Command

```go
package cmd

var logoutCmd = &cobra.Command{
    Use:   "logout [context-name]",
    Short: "Logout from a context (removes credentials)",
    Example: `  # Logout from current context
  myapp logout

  # Logout from specific context
  myapp logout production`,
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }
        
        var contextName string
        if len(args) > 0 {
            contextName = args[0]
        } else {
            contextName = cfg.CurrentContext
        }
        
        if contextName == "" {
            return fmt.Errorf("no context specified and no current context. Use 'myapp logout <context>'")
        }
        
        ctx, ok := cfg.Contexts[contextName]
        if !ok {
            return fmt.Errorf("context '%s' not found", contextName)
        }
        
        // Clear credentials
        ctx.APIKey = ""
        ctx.Token = ""
        
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save config: %w", err)
        }
        
        printSuccess(fmt.Sprintf("Logged out from '%s'", contextName))
        return nil
    },
}
```

### Using Context in Commands

```go
package cmd

var apiCallCmd = &cobra.Command{
    Use:   "api-call",
    Short: "Make an API call using current context",
    RunE: func(cmd *cobra.Command, args []string) error {
        // Load current context
        cfg, err := config.Load()
        if err != nil {
            return fmt.Errorf("failed to load config: %w", err)
        }
        
        ctx, err := cfg.GetCurrentContext()
        if err != nil {
            return err
        }
        
        // Create authenticated client
        client := createHTTPClient(ctx)
        
        // Make request
        resp, err := client.Get(ctx.Server + "/api/v1/resource")
        if err != nil {
            return fmt.Errorf("API call failed: %w", err)
        }
        defer resp.Body.Close()
        
        // Handle response...
        
        return nil
    },
}

func createHTTPClient(ctx *config.Context) *http.Client {
    client := &http.Client{
        Timeout: 30 * time.Second,
    }
    
    // SECURITY WARNING: InsecureSkipVerify should only be used for development
    // or testing with self-signed certificates. Never use in production!
    if ctx.Insecure {
        client.Transport = &http.Transport{
            TLSClientConfig: &tls.Config{
                InsecureSkipVerify: true, // nosec: G402 - Intentional for dev/test only
            },
        }
    }
    
    return client
}

// Add authentication headers
func addAuthHeaders(req *http.Request, ctx *config.Context) {
    switch ctx.AuthType {
    case "apikey":
        req.Header.Set("X-API-Key", ctx.APIKey)
    case "token":
        req.Header.Set("Authorization", "Bearer "+ctx.Token)
    case "basic":
        // Implement basic auth
    }
}
```

### Best Practices for Authentication

1. **Never store credentials in plain text** in the main config
2. **Use OS keyring** when available (macOS Keychain, Windows Credential Manager, Linux Secret Service)
3. **Support token refresh** for OAuth-style authentication
4. **Warn about insecure connections** when using `--insecure`
5. **Show current context** in prompt or status bar
6. **Auto-select context** if only one exists

### Complete Example

See `references/` directory for:
- `root-template.go` - Complete Cobra root command template
- `checklist.md` - CLI quality checklist
- `examples.md` - Additional code examples

## Quick Start Commands

Create a new CLI project in 30 seconds:

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

Now edit `cmd/root.go` to customize for your application!
