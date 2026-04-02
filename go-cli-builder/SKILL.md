---
name: go-cli-builder
description: Design and implement high-quality CLI tools using Go and Cobra, following clig.dev guidelines. Use for new CLI projects, code reviews, adding subcommands, help text, error handling, output formatting, and all CLI-related work. Also use when building interactive login/logout flows, authentication context management, or kubectl-style credential handling. Triggered by requests like "build Go CLI", "command-line tool", "Cobra project", "CLI code review", "create CLI with flags", "interactive login", "CLI authentication", or "context-based credentials".
---

# Go CLI Builder

A comprehensive skill for building high-quality command-line interface (CLI) tools using Go, following the [clig.dev](https://clig.dev/) guidelines.

## When to Use This Skill

- Starting a new Go CLI project from scratch
- Reviewing and improving existing Go CLI code against best practices
- Adding subcommands, flags, or help text to CLI tools
- Implementing error handling, output formatting, or user experience improvements
- Building interactive login/logout flows with authentication
- Implementing kubectl-style context-based credential management
- Converting scripts into proper CLI tools

## Core Philosophy (from clig.dev)

**Human-First Design**: Design for humans first, even if your tool is also used programmatically. CLI interaction is inherently conversational - guide users back on track, make intermediate state clear, and confirm before destructive operations.

**Simple Parts That Work Together**: Build small, modular programs with clean interfaces. Use stdin/stdout/stderr, signals, exit codes, plain text for piping, and JSON for structured data.

**Consistency + Discovery**: Follow existing terminal conventions ("hardwired into our fingers"). Make your CLI self-documenting with comprehensive help, command suggestions, and next-step guidance.

**Saying (Just) Enough + Robustness**: Too little output makes users wonder if it's broken; too much drowns them. Handle unexpected input gracefully, make operations idempotent, fail fast with clear error messages, and provide bug report instructions.

See [clig.dev](https://clig.dev/) for full guidelines.

## Getting Started

**New to Go CLI development?** Read `references/beginner-guide.md` first for project setup, basic templates, and quick start commands.

For experienced developers, this skill covers:
- TTY-aware interactive prompts with fallback to non-interactive mode
- Authentication context management (kubectl-style)
- Human-readable error rewriting and robust error handling
- Output formatting: JSON, plain text, progress indicators
- Subcommand structure and naming conventions
- Production deployment: goreleaser, CI/CD, multi-platform builds

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

### TTY Detection & Color Control

**Always detect if running in an interactive terminal and disable color in non-TTY:**

```go
func isInteractive() bool {
    return isatty.IsTerminal(os.Stdout.Fd()) || isatty.IsCygwinTerminal(os.Stdout.Fd())
}

func shouldUseColor() bool {
    if noColor || os.Getenv("NO_COLOR") != "" || os.Getenv("TERM") == "dumb" {
        return false
    }
    return isInteractive()
}
```

### JSON Output (--json)

```go
if jsonOutput {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    enc.Encode(result)
} else {
    fmt.Printf("Name: %s\nStatus: %s\n", result.Name, result.Status)
}
```

### Progress & State Reporting

```go
// Show progress for operations >100ms in TTY mode, text status otherwise
if isInteractive() && !quietMode {
    bar := progressbar.NewOptions64(total, progressbar.OptionSetDescription("Processing..."))
    for i := int64(0); i < total; i++ {
        bar.Add(1)
    }
} else {
    fmt.Fprintf(os.Stderr, "Processing %d items...\n", total)
}

// Always report state changes
if err := os.WriteFile(filename, data, 0644); err != nil {
    return err
}
fmt.Fprintf(os.Stderr, "Created %s (%d bytes)\n", filename, len(data))
```

### Suggest Next Commands

```go
fmt.Println("Repository initialized.")
fmt.Println("Next steps:")
fmt.Println("  1. Add files:    myapp add <file>")
fmt.Println("  2. Commit:       myapp commit -m 'Initial commit'")
```

## Error Handling

**Rewrite technical errors for humans and group similar errors:**

```go
// Human-readable errors with grouped output
cmd.SilenceErrors = true
if os.IsNotExist(err) {
    fmt.Fprintf(os.Stderr, "Error: File not found: %s\n", filename)
    fmt.Fprintf(os.Stderr, "Make sure the file exists and you have permission.\n")
    os.Exit(1)
}

// Group similar errors
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
    os.Exit(1)
}

// Context first, error last
fmt.Fprintf(os.Stderr, "File: %s\nUser: %s\nError: permission denied\n", file, user)

// Bug report instructions for unexpected errors
if err != nil {
    fmt.Fprintf(os.Stderr, "Unexpected error: %v\n", err)
    fmt.Fprintf(os.Stderr, "Report at: https://github.com/user/myapp/issues/new?title=bug:...\n")
    os.Exit(1)
}
```

## Arguments and Flags

**Prefer flags to arguments** - flags are clearer and more extensible. Provide both short and long forms (`-v, --verbose`). Never read secrets from flags; use `--password-file` instead.

**Standard flag names**: `-a/--all`, `-d/--debug`, `-f/--force`, `-h/--help`, `-n/--dry-run`, `--json`, `-o/--output`, `-q/--quiet`, `--version`.

**Use stdin/stdout as files**: Support `-` for stdin/stdout (e.g., `curl https://example.com/data.json | myapp --input=-`).

## Interactivity

**Prompt only in TTY mode, support `--no-input` for CI:**

```go
var noInput bool
rootCmd.Flags().BoolVarP(&noInput, "no-input", "n", false, "Disable interactive prompts")

func readPassword(prompt string) string {
    fmt.Print(prompt)
    bytePassword, _ := term.ReadPassword(int(os.Stdin.Fd()))
    fmt.Println()
    return string(bytePassword)
}

// Confirm destructive actions
if isInteractive() && !force {
    fmt.Fprintf(os.Stderr, "This will delete %d files permanently. Are you sure? [y/N]: ", count)
    var response string
    fmt.Scanln(&response)
    if strings.ToLower(response) != "y" && strings.ToLower(response) != "yes" {
        fmt.Fprintln(os.Stderr, "Aborted.")
        return nil
    }
}
```

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

## Subcommands

**Use `noun verb` naming** (like Docker): `myapp container create`, `myapp image pull`.

```go
var createCmd = &cobra.Command{
    Use:   "create [name]",
    Short: "Create a new resource",
    RunE: func(cmd *cobra.Command, args []string) error {
        // Implementation
    },
}
func init() {
    rootCmd.AddCommand(createCmd)
    createCmd.Flags().String("type", "basic", "Resource type")
}
```

**Keep consistency**: same flag names across subcommands, similar output formatting.

## Robustness & Configuration

**Print something within 100ms** - responsiveness over speed. **Set timeouts** on all network operations. **Handle signals** for graceful Ctrl+C recovery:

```go
// Timeouts and signal handling
ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
go func() {
    <-sigCh
    fmt.Fprintln(os.Stderr, "Gracefully stopping...")
    cancel()
}()

// Make operations safe to repeat
if _, err := os.Stat(outputFile); err == nil && !force {
    return fmt.Errorf("output file already exists (use --force)")
}
```

**XDG config directory** - follow the spec for storing configs:
```go
func configDir() string {
    if dir := os.Getenv("XDG_CONFIG_HOME"); dir != "" {
        return filepath.Join(dir, "myapp")
    }
    home, _ := os.UserHomeDir()
    return filepath.Join(home, ".config", "myapp")
}
```

**Config precedence** (high to low): Flags → Env vars → Project-level (`.myapprc`) → User-level (`~/.config/myapp/`) → System-wide (`/etc/myapp/`).

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

**Standard env vars**: `NO_COLOR`/`FORCE_COLOR` (color), `DEBUG` (verbose), `HTTP_PROXY`/`HTTPS_PROXY` (network), `TERM` (terminal type), `PAGER` (output). Use `godotenv.Load()` to read `.env` files.

## Distribution

**Go's strength: single binary** - build for multiple platforms:
```bash
GOOS=darwin GOARCH=amd64 go build -o myapp-darwin-amd64
GOOS=windows GOARCH=amd64 go build -o myapp-windows-amd64.exe
```

**Use goreleaser** for automated releases. Read `references/github-workflows/release.yml` for multi-platform builds.

### CI/CD Integration

**Automate testing and releases with GitHub Actions:**

Read `references/github-workflows/ci.yml` and `references/github-workflows/release.yml` when:
- Setting up CI for a new Go CLI project (ci.yml covers test, build, lint)
- Configuring automated releases with goreleaser (release.yml covers multi-platform builds)

**Quick Setup:**

1. Copy workflow files to `.github/workflows/`
2. Update `go-version` if needed
3. Adjust build path if your main package is not in `./cmd/`

**CI Features:**
- Test on every push and pull request
- Build verification
- Linting with `go vet`
- Multi-platform releases (Linux, macOS, Windows)
- ARM64 and AMD64 support

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

## README Documentation

**Always create bilingual README files** for CLI projects:

| File | Language | Purpose |
|------|----------|---------|
| `README.md` | English | International audience, use in package registries (GitHub, crates.io) |
| `README_ko.md` | Korean | Korean-speaking users and teams |

**README structure:**

```markdown
# CLI Name

Brief description (1-2 sentences).

## Installation

```bash
# Binary releases
curl -sSL https://example.com/install.sh | sh

# Via package managers
brew install myapp
```

## Usage

```bash
# Basic command
myapp [command] [flags]

# Examples
myapp login production
myapp context set staging
```

## Commands

| Command | Description |
|---------|-------------|
| `myapp login [name]` | Authenticate and create a context |
| `myapp logout [name]` | Logout and remove credentials |
| `myapp context list` | List all contexts |
| `myapp context set [name]` | Switch to a context |
```

**README_ko.md should be a direct translation** with same structure and examples.

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

### Authentication Command Helper Functions

These helpers eliminate code duplication across login, logout, and context commands:

```go
// selectContextInteractive displays available contexts and prompts for selection.
// Returns selected context name or error.
func selectContextInteractive(cfg *config.Config, prompt string) (string, error) {
    if len(cfg.Contexts) == 0 {
        return "", fmt.Errorf("no contexts available")
    }

    fmt.Fprintln(os.Stderr, "Available contexts:")
    names := make([]string, 0, len(cfg.Contexts))
    i := 1
    for name := range cfg.Contexts {
        marker := ""
        if name == cfg.CurrentContext {
            marker = " (current)"
        }
        fmt.Fprintf(os.Stderr, "  %d. %s%s\n", i, name, marker)
        names = append(names, name)
        i++
    }
    fmt.Fprintf(os.Stderr, "\n%s [1]: ", prompt)
    var selection string
    fmt.Scanln(&selection)

    if selection == "" {
        return names[0], nil
    }
    idx, err := strconv.Atoi(selection)
    if err != nil || idx < 1 || idx > len(names) {
        return "", fmt.Errorf("invalid selection")
    }
    return names[idx-1], nil
}

// confirmAction prompts for y/N confirmation. Returns true if confirmed.
func confirmAction(prompt string) bool {
    fmt.Fprintf(os.Stderr, "%s [y/N]: ", prompt)
    var response string
    fmt.Scanln(&response)
    return strings.ToLower(response) == "y" || strings.ToLower(response) == "yes"
}

// readSecret reads a password/token without echo
func readSecret() string {
    byteSecret, _ := term.ReadPassword(int(os.Stdin.Fd()))
    fmt.Println()
    return string(byteSecret)
}
```

### Login Command

```go
package cmd

var noInput bool

var loginCmd = &cobra.Command{
    Use:   "login [context-name]",
    Short: "Authenticate and create a new context",
    Example: `  myapp login                  # Interactive
  myapp login prod --server=https://api.example.com --api-key=KEY`,
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, _ := config.Load()
        if cfg == nil {
            cfg = &config.Config{Contexts: make(map[string]*config.Context)}
        }

        interactive := isInteractive() && !noInput
        var contextName, server, apiKey, token, username string
        var useToken, insecure bool

        // Get context name
        if len(args) > 0 {
            contextName = args[0]
        } else if interactive {
            fmt.Print("Context name: ")
            fmt.Scanln(&contextName)
        } else {
            return fmt.Errorf("context name required (use 'myapp login <name>')")
        }

        // Get server URL (interactive only in this simplified version)
        if interactive {
            fmt.Print("Server URL: ")
            fmt.Scanln(&server)
        }

        // Get credentials
        if interactive {
            fmt.Println("Auth method: 1=API Key, 2=Token")
            fmt.Print("Select: ")
            var sel string
            fmt.Scanln(&sel)
            if sel == "1" {
                fmt.Print("API Key: ")
                apiKey = readSecret()
            } else if sel == "2" {
                fmt.Print("Token: ")
                token = readSecret()
                useToken = true
            }
            if interactive && confirmAction("Allow insecure connections?") {
                insecure = true
            }
        }

        ctx := &config.Context{
            Name: contextName, Server: server, APIKey: apiKey, Token: token,
            Username: username, AuthType: determineAuthType(apiKey, token), Insecure: insecure,
        }

        fmt.Fprintf(os.Stderr, "Authenticating to %s...\n", server)
        if err := testConnection(ctx); err != nil {
            return fmt.Errorf("authentication failed: %w", err)
        }

        cfg.Contexts[contextName] = ctx
        cfg.CurrentContext = contextName
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save context: %w", err)
        }

        printSuccess(fmt.Sprintf("Logged in to '%s' (%s)", contextName, server))
        return nil
    },
}

func init() {
    loginCmd.Flags().StringVar(&server, "server", "", "Server URL")
    loginCmd.Flags().StringVar(&apiKey, "api-key", "", "API key for authentication")
    loginCmd.Flags().BoolVar(&useToken, "token", false, "Use token authentication")
    loginCmd.Flags().StringVar(&username, "username", "", "Username")
    loginCmd.Flags().BoolVar(&insecure, "insecure", false, "Allow insecure connections")
    loginCmd.Flags().BoolVarP(&noInput, "no-input", "n", false, "Disable interactive prompts")
}

func testConnection(ctx *config.Context) error {
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

// myapp context set [name]
var contextSetCmd = &cobra.Command{
    Use:   "set [name]",
    Short: "Set the current context",
    Example: `  myapp context set           # Interactive selection
  myapp context set production  # Direct set
  myapp context set staging --no-input`,
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }

        var contextName string
        interactive := isInteractive() && !noInput

        if len(args) > 0 {
            contextName = args[0]
        } else if interactive {
            contextName, err = selectContextInteractive(cfg, "Select context")
            if err != nil {
                fmt.Fprintln(os.Stderr, "Run 'myapp login' to create one.")
                return nil
            }
        } else {
            return fmt.Errorf("context name required (use 'myapp context set <name>')")
        }

        if err := cfg.SetContext(contextName); err != nil {
            return err
        }
        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save config: %w", err)
        }

        printSuccess(fmt.Sprintf("Switched to context '%s'", contextName))
        return nil
    },
}

// myapp context delete [name]
var contextDeleteCmd = &cobra.Command{
    Use:   "delete [name]",
    Short: "Delete a context",
    Example: `  myapp context delete           # Interactive selection
  myapp context delete old-staging`,
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }

        var contextName string
        interactive := isInteractive() && !noInput

        if len(args) > 0 {
            contextName = args[0]
        } else if interactive {
            contextName, err = selectContextInteractive(cfg, "Select context to delete")
            if err != nil {
                return nil
            }
        } else {
            return fmt.Errorf("context name required (use 'myapp context delete <name>')")
        }

        ctx, ok := cfg.Contexts[contextName]
        if !ok {
            return fmt.Errorf("context '%s' not found", contextName)
        }

        if interactive && !confirmAction(fmt.Sprintf("Delete context '%s' (%s)?", contextName, ctx.Server)) {
            fmt.Fprintln(os.Stderr, "Cancelled.")
            return nil
        }

        delete(cfg.Contexts, contextName)
        if cfg.CurrentContext == contextName {
            cfg.CurrentContext = ""
            fmt.Fprintln(os.Stderr, "Note: Deleted context was current. Run 'myapp context set' to select another.")
        }

        if err := config.Save(cfg); err != nil {
            return fmt.Errorf("failed to save config: %w", err)
        }

        printSuccess(fmt.Sprintf("Deleted context '%s'", contextName))
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
    Example: `  myapp logout              # Interactive (current context)
  myapp logout production  # Direct specify`,
    RunE: func(cmd *cobra.Command, args []string) error {
        cfg, err := config.Load()
        if err != nil {
            return err
        }

        var contextName string
        interactive := isInteractive() && !noInput

        if len(args) > 0 {
            contextName = args[0]
        } else if interactive {
            contextName, err = selectContextInteractive(cfg, "Select context to logout")
            if err != nil {
                return nil
            }
        } else {
            contextName = cfg.CurrentContext
            if contextName == "" {
                return fmt.Errorf("no context specified and no current context")
            }
        }

        ctx, ok := cfg.Contexts[contextName]
        if !ok {
            return fmt.Errorf("context '%s' not found", contextName)
        }

        if interactive && !confirmAction(fmt.Sprintf("Logout from '%s' (%s)?", contextName, ctx.Server)) {
            fmt.Fprintln(os.Stderr, "Cancelled.")
            return nil
        }

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

## Reference Files

Use these references when working on specific tasks:

| Reference | When to Read |
|-----------|-------------|
| `references/beginner-guide.md` | First Go CLI project or need project setup basics |
| `references/root-template.go` | Need a starting point for a new CLI root command |
| `references/checklist.md` | Reviewing or auditing an existing CLI for quality |
| `references/examples.md` | Need additional code examples for specific features |
| `references/github-workflows/ci.yml` | Setting up CI/CD for a new Go CLI project |
| `references/github-workflows/release.yml` | Setting up automated releases with goreleaser |
