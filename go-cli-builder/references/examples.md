# Go CLI Code Examples

Practical Go code examples for various CLI patterns following clig.dev guidelines.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Root Command Template](#root-command-template)
3. [Subcommand Structure](#subcommand-structure)
4. [Progress Indication](#progress-indication)
5. [Interactive Prompts](#interactive-prompts)
6. [Configuration Management](#configuration-management)
7. [Signal Handling](#signal-handling)
8. [Table Output](#table-output)
9. [File I/O](#file-io)
10. [Error Handling](#error-handling)
11. [Secrets Management](#secrets-management)
12. [Testing CLI Commands](#testing-cli-commands)

---

## Project Structure

Standard Go CLI project layout:

```
myapp/
├── cmd/
│   ├── root.go          # Root command definition
│   ├── version.go       # Version subcommand
│   └── subcommand.go    # Other subcommands
├── internal/
│   ├── config/          # Configuration management
│   ├── output/          # Output formatting utilities
│   └── utils/           # Internal utilities
├── main.go              # Entry point
├── go.mod
├── go.sum
└── README.md
```

---

## Root Command Template

Complete production-ready root command implementation:

### main.go

```go
package main

import (
    "os"
    "github.com/yourname/myapp/cmd"
)

func main() {
    if err := cmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

### cmd/root.go

```go
package cmd

import (
    "context"
    "encoding/json"
    "fmt"
    "os"
    "os/signal"
    "syscall"

    "github.com/fatih/color"
    "github.com/mattn/go-isatty"
    "github.com/spf13/cobra"
)

var (
    // Global flags
    jsonOutput  bool
    quietMode   bool
    noColor     bool
    debugMode   bool
    noInput     bool

    rootCmd = &cobra.Command{
        Use:   "myapp [flags] [args]",
        Short: "Brief description of what myapp does",
        Long: `A longer description that spans multiple lines
and likely contains examples and usage of using your application.`,
        Example: `  # Process a single file
  myapp input.txt

  # Output as JSON
  myapp --json input.txt > output.json

  # Quiet mode for scripts
  myapp --quiet input.txt || echo "Failed"`,
        SilenceUsage:  true,
        SilenceErrors: true,
    }
)

func Execute() error {
    return rootCmd.Execute()
}

func init() {
    // Persistent flags available to all subcommands
    rootCmd.PersistentFlags().BoolVar(&jsonOutput, "json", false, "Output in JSON format")
    rootCmd.PersistentFlags().BoolVarP(&quietMode, "quiet", "q", false, "Suppress non-essential output")
    rootCmd.PersistentFlags().BoolVar(&noColor, "no-color", false, "Disable colored output")
    rootCmd.PersistentFlags().BoolVar(&debugMode, "debug", false, "Enable debug output")
    rootCmd.PersistentFlags().BoolVar(&noInput, "no-input", false, "Disable interactive prompts")

    // Add subcommands
    rootCmd.AddCommand(versionCmd)
}

// isInteractive returns true if stdout is a TTY
func isInteractive() bool {
    return isatty.IsTerminal(os.Stdout.Fd()) || 
           isatty.IsCygwinTerminal(os.Stdout.Fd())
}

// isStdinTTY returns true if stdin is a TTY
func isStdinTTY() bool {
    return isatty.IsTerminal(os.Stdin.Fd()) || 
           isatty.IsCygwinTerminal(os.Stdin.Fd())
}

// shouldUseColor determines if colors should be used
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
    return isInteractive()
}

// printError prints an error message to stderr
func printError(msg string) {
    if shouldUseColor() {
        color.New(color.FgRed).Fprintln(os.Stderr, msg)
    } else {
        fmt.Fprintln(os.Stderr, msg)
    }
}

// printSuccess prints a success message
func printSuccess(msg string) {
    if quietMode {
        return
    }
    if shouldUseColor() {
        color.New(color.FgGreen).Fprintln(os.Stderr, msg)
    } else {
        fmt.Fprintln(os.Stderr, msg)
    }
}

// debug prints debug information if debug mode is enabled
func debug(format string, args ...interface{}) {
    if !debugMode {
        return
    }
    fmt.Fprintf(os.Stderr, "[DEBUG] "+format+"\n", args...)
}

// outputJSON outputs data as formatted JSON
func outputJSON(data interface{}) error {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    return enc.Encode(data)
}

// setupSignalHandling sets up graceful shutdown on Ctrl+C
func setupSignalHandling(ctx context.Context) (context.Context, context.CancelFunc) {
    ctx, cancel := context.WithCancel(ctx)
    
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
    
    go func() {
        <-sigCh
        fmt.Fprintln(os.Stderr, "\nInterrupt received. Shutting down...")
        cancel()
        
        // Second interrupt forces exit
        <-sigCh
        fmt.Fprintln(os.Stderr, "\nForced exit.")
        os.Exit(130) // 128 + SIGINT
    }()
    
    return ctx, cancel
}
```

---

## Subcommand Structure

### cmd/version.go

```go
package cmd

import (
    "fmt"
    "runtime"

    "github.com/spf13/cobra"
)

var (
    Version   = "dev"
    Commit    = "unknown"
    BuildDate = "unknown"
)

var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Display version information",
    Long:  `Display detailed version information including build metadata.`,
    Run: func(cmd *cobra.Command, args []string) {
        if jsonOutput {
            outputJSON(map[string]string{
                "version":    Version,
                "commit":     Commit,
                "buildDate":  BuildDate,
                "goVersion":  runtime.Version(),
                "platform":   runtime.GOOS + "/" + runtime.GOARCH,
            })
            return
        }

        fmt.Printf("Version:   %s\n", Version)
        fmt.Printf("Commit:    %s\n", Commit)
        fmt.Printf("Build Date: %s\n", BuildDate)
        fmt.Printf("Go:        %s\n", runtime.Version())
        fmt.Printf("Platform:  %s/%s\n", runtime.GOOS, runtime.GOARCH)
    },
}
```

### Noun-Verb Subcommand Pattern

```go
// cmd/resource.go - Noun (parent command)
package cmd

import "github.com/spf13/cobra"

var resourceCmd = &cobra.Command{
    Use:   "resource",
    Short: "Manage resources",
    Long:  `Create, list, and manage resources.`,
}

func init() {
    rootCmd.AddCommand(resourceCmd)
    
    // Add verb subcommands
    resourceCmd.AddCommand(resourceCreateCmd)
    resourceCmd.AddCommand(resourceListCmd)
    resourceCmd.AddCommand(resourceDeleteCmd)
}
```

```go
// cmd/resource_create.go - Verb subcommand
package cmd

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
)

var resourceCreateCmd = &cobra.Command{
    Use:   "create [name]",
    Short: "Create a new resource",
    Long: `Create a new resource with the specified name.

Examples:
    myapp resource create myresource
    myapp resource create --type=advanced myresource
    myapp resource create --dry-run myresource`,
    Args: cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        name := args[0]
        resourceType, _ := cmd.Flags().GetString("type")
        dryRun, _ := cmd.Flags().GetBool("dry-run")
        force, _ := cmd.Flags().GetBool("force")

        debug("Creating resource: name=%s, type=%s", name, resourceType)

        if dryRun {
            fmt.Fprintf(os.Stderr, "Would create resource '%s' (type: %s)\n", name, resourceType)
            return nil
        }

        // Check if already exists (idempotency)
        if exists(name) && !force {
            return fmt.Errorf("resource '%s' already exists (use --force to overwrite)", name)
        }

        // Create resource
        if err := createResource(name, resourceType); err != nil {
            return fmt.Errorf("failed to create resource: %w\n\nHint: Check permissions and try again", err)
        }

        printSuccess(fmt.Sprintf("Created resource '%s'", name))
        
        // Suggest next steps
        fmt.Fprintln(os.Stderr)
        fmt.Fprintln(os.Stderr, "Next steps:")
        fmt.Fprintf(os.Stderr, "  myapp resource show %s    # View resource details\n", name)
        fmt.Fprintf(os.Stderr, "  myapp resource list       # List all resources\n")

        return nil
    },
}

func init() {
    resourceCreateCmd.Flags().StringP("type", "t", "basic", "Resource type (basic, advanced)")
    resourceCreateCmd.Flags().BoolP("dry-run", "n", false, "Show what would be created without actually creating")
    resourceCreateCmd.Flags().BoolP("force", "f", false, "Overwrite if resource already exists")
}

func exists(name string) bool {
    // Check if resource exists
    return false
}

func createResource(name, resourceType string) error {
    // Create the resource
    return nil
}
```

---

## Progress Indication

### Simple Spinner

```go
package output

import (
    "fmt"
    "os"
    "time"

    "github.com/mattn/go-isatty"
)

// Spinner displays a simple progress spinner
func Spinner(done chan bool, message string) {
    if !isatty.IsTerminal(os.Stdout.Fd()) {
        // Non-interactive: just print start message
        fmt.Fprintf(os.Stderr, "%s...\n", message)
        <-done
        fmt.Fprintln(os.Stderr, "Done")
        return
    }

    frames := []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}
    i := 0
    
    for {
        select {
        case <-done:
            fmt.Printf("\r✓ %s\n", message)
            return
        case <-time.After(100 * time.Millisecond):
            fmt.Printf("\r%s %s", frames[i%len(frames)], message)
            i++
        }
    }
}

// Usage example
func longRunningOperation() error {
    done := make(chan bool)
    go Spinner(done, "Processing files")
    
    // Do work
    time.Sleep(3 * time.Second)
    
    done <- true
    return nil
}
```

### Progress Bar

```go
package output

import (
    "fmt"
    "os"

    "github.com/mattn/go-isatty"
    "github.com/schollz/progressbar/v3"
)

// ProgressBar displays a progress bar for operations
func ProgressBar(total int64, description string) *progressbar.ProgressBar {
    if !isatty.IsTerminal(os.Stdout.Fd()) {
        // Return a no-op progress bar for non-interactive use
        return &progressbar.ProgressBar{}
    }

    return progressbar.NewOptions64(total,
        progressbar.OptionSetDescription(description),
        progressbar.OptionSetWriter(os.Stderr),
        progressbar.OptionShowCount(),
        progressbar.OptionShowIts(),
        progressbar.OptionSetTheme(progressbar.Theme{
            Saucer:        "=",
            SaucerHead:    ">",
            SaucerPadding: " ",
            BarStart:      "[",
            BarEnd:        "]",
        }),
    )
}

// ProgressOrMessage shows progress bar in TTY, messages in non-TTY
func ProgressOrMessage(total int64, description string) (*progressbar.ProgressBar, func(string)) {
    if isatty.IsTerminal(os.Stdout.Fd()) {
        bar := ProgressBar(total, description)
        return bar, func(msg string) {
            // No-op for TTY mode
        }
    }

    // Non-TTY: print milestone messages
    fmt.Fprintf(os.Stderr, "%s...\n", description)
    return nil, func(msg string) {
        fmt.Fprintf(os.Stderr, "  %s\n", msg)
    }
}
```

---

## Interactive Prompts

### Basic Confirmation

```go
package cmd

import (
    "bufio"
    "fmt"
    "os"
    "strings"

    "github.com/mattn/go-isatty"
)

// Confirm asks for user confirmation
func Confirm(prompt string) (bool, error) {
    if !isatty.IsTerminal(os.Stdin.Fd()) {
        return false, fmt.Errorf("interactive terminal required (use --force to skip confirmation)")
    }

    reader := bufio.NewReader(os.Stdin)
    fmt.Fprintf(os.Stderr, "%s [y/N]: ", prompt)

    input, err := reader.ReadString('\n')
    if err != nil {
        return false, err
    }

    input = strings.TrimSpace(strings.ToLower(input))
    return input == "y" || input == "yes", nil
}

// ConfirmOrForce handles confirmation with --force flag support
func ConfirmOrForce(force bool, prompt string) (bool, error) {
    if force {
        return true, nil
    }

    if noInput {
        return false, fmt.Errorf("--force is required when using --no-input")
    }

    return Confirm(prompt)
}

// Usage in command
var deleteCmd = &cobra.Command{
    Use:   "delete [name]",
    Short: "Delete a resource",
    RunE: func(cmd *cobra.Command, args []string) error {
        name := args[0]
        force, _ := cmd.Flags().GetBool("force")

        confirmed, err := ConfirmOrForce(force, fmt.Sprintf("Delete '%s' permanently?", name))
        if err != nil {
            printError(err.Error())
            os.Exit(1)
        }

        if !confirmed {
            fmt.Fprintln(os.Stderr, "Aborted.")
            return nil
        }

        // Delete resource
        return nil
    },
}
```

### Password Input (No Echo)

```go
package cmd

import (
    "fmt"
    "os"

    "github.com/mattn/go-isatty"
    "golang.org/x/term"
)

// ReadPassword reads a password without echoing
func ReadPassword(prompt string) (string, error) {
    if !isatty.IsTerminal(os.Stdin.Fd()) {
        return "", fmt.Errorf("interactive terminal required (use --password-file)")
    }

    fmt.Fprint(os.Stderr, prompt)
    password, err := term.ReadPassword(int(os.Stdin.Fd()))
    fmt.Fprintln(os.Stderr) // Newline after password

    if err != nil {
        return "", fmt.Errorf("failed to read password: %w", err)
    }

    return string(password), nil
}

// ReadPasswordOrFile reads password from terminal or file
func ReadPasswordOrFile(passwordFile string) (string, error) {
    if passwordFile != "" {
        data, err := os.ReadFile(passwordFile)
        if err != nil {
            return "", fmt.Errorf("failed to read password file: %w", err)
        }
        return strings.TrimSpace(string(data)), nil
    }

    return ReadPassword("Password: ")
}
```

### Select From List

```go
package cmd

import (
    "fmt"
    "os"
    "strconv"

    "github.com/mattn/go-isatty"
)

// Select prompts user to select from a list
func Select(prompt string, options []string) (int, error) {
    if !isatty.IsTerminal(os.Stdin.Fd()) {
        return 0, fmt.Errorf("interactive terminal required")
    }

    fmt.Fprintln(os.Stderr, prompt)
    for i, opt := range options {
        fmt.Fprintf(os.Stderr, "  %d) %s\n", i+1, opt)
    }
    fmt.Fprint(os.Stderr, "Select (1-"+strconv.Itoa(len(options))+"): ")

    var choice int
    _, err := fmt.Scanln(&choice)
    if err != nil || choice < 1 || choice > len(options) {
        return 0, fmt.Errorf("invalid selection")
    }

    return choice - 1, nil
}
```

---

## Configuration Management

### Viper Configuration

```go
package config

import (
    "fmt"
    "os"
    "path/filepath"

    "github.com/spf13/viper"
)

var Config *Configuration

type Configuration struct {
    Server ServerConfig `mapstructure:"server"`
    Output OutputConfig `mapstructure:"output"`
    Log    LogConfig    `mapstructure:"log"`
}

type ServerConfig struct {
    Host string `mapstructure:"host"`
    Port int    `mapstructure:"port"`
}

type OutputConfig struct {
    Format string `mapstructure:"format"` // text, json
    Color  string `mapstructure:"color"`  // auto, always, never
}

type LogConfig struct {
    Level string `mapstructure:"level"` // debug, info, warn, error
}

func Load(cfgFile string) error {
    viper.SetConfigType("yaml")

    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        // XDG spec compliance
        configDir := getConfigDir()
        viper.AddConfigPath(configDir)
        viper.AddConfigPath(".")
        viper.SetConfigName("config")
    }

    // Environment variables
    viper.SetEnvPrefix("MYAPP")
    viper.AutomaticEnv()

    // Defaults
    viper.SetDefault("server.host", "localhost")
    viper.SetDefault("server.port", 8080)
    viper.SetDefault("output.format", "text")
    viper.SetDefault("output.color", "auto")
    viper.SetDefault("log.level", "info")

    // Read config
    if err := viper.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return fmt.Errorf("failed to read config: %w", err)
        }
    }

    Config = &Configuration{}
    if err := viper.Unmarshal(Config); err != nil {
        return fmt.Errorf("failed to unmarshal config: %w", err)
    }

    return nil
}

func getConfigDir() string {
    if dir := os.Getenv("XDG_CONFIG_HOME"); dir != "" {
        return filepath.Join(dir, "myapp")
    }
    home, _ := os.UserHomeDir()
    return filepath.Join(home, ".config", "myapp")
}

// GetConfigFile returns the path to the config file
func GetConfigFile() string {
    return viper.ConfigFileUsed()
}
```

### Environment File Loading

```go
package config

import (
    "os"
    "path/filepath"

    "github.com/joho/godotenv"
)

// LoadEnv loads .env file from project root
func LoadEnv() error {
    // Try multiple locations
    locations := []string{
        ".env",
        filepath.Join("..", ".env"),
        filepath.Join(os.Getenv("HOME"), ".myapp", ".env"),
    }

    for _, loc := range locations {
        if _, err := os.Stat(loc); err == nil {
            return godotenv.Load(loc)
        }
    }

    // .env is optional, so no error if not found
    return nil
}
```

---

## Signal Handling

### Graceful Shutdown

```go
package cmd

import (
    "context"
    "fmt"
    "os"
    "os/signal"
    "syscall"
    "time"
)

// SetupGracefulShutdown sets up graceful shutdown on signals
func SetupGracefulShutdown(parent context.Context) (context.Context, context.CancelFunc) {
    ctx, cancel := context.WithCancel(parent)

    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        sig := <-sigCh
        fmt.Fprintf(os.Stderr, "\nReceived %s, shutting down gracefully...\n", sig)
        fmt.Fprintln(os.Stderr, "(Press Ctrl+C again to force)")
        cancel()

        // Second signal forces immediate exit
        <-sigCh
        fmt.Fprintln(os.Stderr, "\nForced exit.")
        os.Exit(130)
    }()

    return ctx, cancel
}

// RunWithGracefulShutdown runs a function with graceful shutdown support
func RunWithGracefulShutdown(fn func(ctx context.Context) error) error {
    ctx, cancel := SetupGracefulShutdown(context.Background())
    defer cancel()

    if err := fn(ctx); err != nil {
        if ctx.Err() == context.Canceled {
            fmt.Fprintln(os.Stderr, "Operation was cancelled")
            return nil
        }
        return err
    }

    return nil
}

// CleanupWithTimeout runs cleanup with a timeout
func CleanupWithTimeout(timeout time.Duration, cleanup func()) {
    done := make(chan struct{})
    go func() {
        cleanup()
        close(done)
    }()

    select {
    case <-done:
        // Cleanup completed
    case <-time.After(timeout):
        fmt.Fprintln(os.Stderr, "Cleanup timed out")
    }
}
```

---

## Table Output

### Tabwriter Table

```go
package output

import (
    "encoding/json"
    "fmt"
    "os"
    "strings"
    "text/tabwriter"
)

// Table represents tabular data
type Table struct {
    Headers []string
    Rows    [][]string
}

// NewTable creates a new table
func NewTable(headers ...string) *Table {
    return &Table{
        Headers: headers,
        Rows:    [][]string{},
    }
}

// AddRow adds a row to the table
func (t *Table) AddRow(row ...string) {
    t.Rows = append(t.Rows, row)
}

// Print outputs the table
func (t *Table) Print() error {
    if jsonOutput {
        return t.printJSON()
    }

    w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)

    // Headers
    fmt.Fprintln(w, strings.Join(t.Headers, "\t"))
    fmt.Fprintln(w, strings.Repeat("-", 50))

    // Rows
    for _, row := range t.Rows {
        fmt.Fprintln(w, strings.Join(row, "\t"))
    }

    return w.Flush()
}

func (t *Table) printJSON() error {
    var data []map[string]string
    for _, row := range t.Rows {
        item := make(map[string]string)
        for i, header := range t.Headers {
            if i < len(row) {
                item[header] = row[i]
            }
        }
        data = append(data, item)
    }

    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    return enc.Encode(data)
}

// PlainOutput outputs in plain, grep-friendly format
func (t *Table) PlainOutput() error {
    for _, row := range t.Rows {
        fmt.Println(strings.Join(row, "\t"))
    }
    return nil
}
```

### Usage Example

```go
func listResources() error {
    table := output.NewTable("ID", "NAME", "STATUS", "CREATED")
    
    for _, r := range resources {
        table.AddRow(r.ID, r.Name, r.Status, r.Created.Format("2006-01-02"))
    }

    if plainOutput {
        return table.PlainOutput()
    }
    return table.Print()
}
```

---

## File I/O

### Stdin or File Input

```go
package cmd

import (
    "bufio"
    "fmt"
    "io"
    "os"

    "github.com/mattn/go-isatty"
)

// InputReader returns a reader for input (stdin or file)
func InputReader(filename string) (io.ReadCloser, error) {
    if filename == "" || filename == "-" {
        // Check if stdin is a TTY and not a pipe
        if isatty.IsTerminal(os.Stdin.Fd()) {
            return nil, fmt.Errorf("input file required, or pipe data to stdin")
        }
        return os.Stdin, nil
    }

    f, err := os.Open(filename)
    if err != nil {
        if os.IsNotExist(err) {
            return nil, fmt.Errorf("file not found: %s\n\nHint: Check the file exists and you have read permission", filename)
        }
        return nil, fmt.Errorf("failed to open file: %w", err)
    }

    return f, nil
}

// ProcessInput reads and processes input line by line
func ProcessInput(reader io.Reader, process func(string) error) error {
    scanner := bufio.NewScanner(reader)
    lineNum := 0

    for scanner.Scan() {
        lineNum++
        if err := process(scanner.Text()); err != nil {
            return fmt.Errorf("line %d: %w", lineNum, err)
        }
    }

    return scanner.Err()
}
```

### Output File or Stdout

```go
package cmd

import (
    "fmt"
    "io"
    "os"
)

// OutputWriter returns a writer for output (stdout or file)
func OutputWriter(filename string) (io.WriteCloser, func(), error) {
    if filename == "" || filename == "-" {
        return os.Stdout, func() {}, nil
    }

    f, err := os.Create(filename)
    if err != nil {
        return nil, nil, fmt.Errorf("failed to create file: %w", err)
    }

    cleanup := func() {
        if err := f.Close(); err != nil {
            fmt.Fprintf(os.Stderr, "Warning: failed to close output file: %v\n", err)
        }
    }

    return f, cleanup, nil
}

// SafeOutputWriter creates output file only after validation
func SafeOutputWriter(filename string, validate func() error) (io.WriteCloser, func(), error) {
    if filename == "" || filename == "-" {
        return os.Stdout, func() {}, nil
    }

    // Check if file exists
    if _, err := os.Stat(filename); err == nil {
        return nil, nil, fmt.Errorf("file already exists: %s (use --force to overwrite)", filename)
    }

    return OutputWriter(filename)
}
```

---

## Error Handling

### Human-Readable Errors

```go
package cmd

import (
    "fmt"
    "net"
    "os"
    "strings"
)

// ConnectionError wraps network errors with helpful messages
func ConnectionError(host string, err error) error {
    if os.IsTimeout(err) {
        return fmt.Errorf("connection timed out to %s\n\nHint: Check network connection or increase timeout with --timeout", host)
    }
    
    if strings.Contains(err.Error(), "connection refused") {
        return fmt.Errorf("connection refused by %s\n\nHint: Check if the server is running and the port is correct", host)
    }
    
    if netErr, ok := err.(net.Error); ok && netErr.Temporary() {
        return fmt.Errorf("temporary network error connecting to %s: %w\n\nHint: Retry the operation", host, err)
    }

    return fmt.Errorf("failed to connect to %s: %w", host, err)
}

// FileError wraps file errors with helpful messages
func FileError(path string, err error) error {
    if os.IsNotExist(err) {
        return fmt.Errorf("file not found: %s\n\nHint: Check the file exists and you have read permission", path)
    }
    
    if os.IsPermission(err) {
        return fmt.Errorf("permission denied: %s\n\nHint: Check file permissions or run with elevated privileges", path)
    }

    return fmt.Errorf("file error (%s): %w", path, err)
}

// ValidationError for input validation
func ValidationError(field, message string) error {
    return fmt.Errorf("invalid %s: %s", field, message)
}
```

### Grouped Errors

```go
package cmd

import (
    "fmt"
    "os"
    "strings"
)

// ErrorCollector collects multiple errors
func ErrorCollector() *errorCollector {
    return &errorCollector{}
}

type errorCollector struct {
    errors []string
}

func (e *errorCollector) Add(format string, args ...interface{}) {
    e.errors = append(e.errors, fmt.Sprintf(format, args...))
}

func (e *errorCollector) HasErrors() bool {
    return len(e.errors) > 0
}

func (e *errorCollector) Error() error {
    if !e.HasErrors() {
        return nil
    }

    var sb strings.Builder
    sb.WriteString(fmt.Sprintf("%d error(s) occurred:\n", len(e.errors)))
    for _, err := range e.errors {
        sb.WriteString(fmt.Sprintf("  • %s\n", err))
    }

    return fmt.Errorf(sb.String())
}

func (e *errorCollector) PrintAndExit() {
    if !e.HasErrors() {
        return
    }

    fmt.Fprintln(os.Stderr, e.Error())
    fmt.Fprintln(os.Stderr, "\nHint: Use --help for usage information")
    os.Exit(1)
}

// Usage
func processFiles(files []string) error {
    errs := ErrorCollector()

    for _, file := range files {
        if err := process(file); err != nil {
            errs.Add("%s: %v", file, err)
        }
    }

    return errs.Error()
}
```

---

## Secrets Management

### Secure Password Handling

```go
package cmd

import (
    "fmt"
    "os"
    "strings"

    "github.com/mattn/go-isatty"
    "golang.org/x/term"
)

// NEVER do this:
// cmd.Flags().String("password", "", "Password") // ❌ Leaks to ps, history

// Instead, use these approaches:

// Approach 1: Password from file
func GetPasswordFromFile(path string) (string, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return "", fmt.Errorf("failed to read password file: %w", err)
    }
    return strings.TrimSpace(string(data)), nil
}

// Approach 2: Password from interactive prompt
func GetPasswordInteractive(prompt string) (string, error) {
    if !isatty.IsTerminal(os.Stdin.Fd()) {
        return "", fmt.Errorf("interactive terminal required (use --password-file)")
    }

    fmt.Fprint(os.Stderr, prompt)
    password, err := term.ReadPassword(int(os.Stdin.Fd()))
    fmt.Fprintln(os.Stderr)

    if err != nil {
        return "", fmt.Errorf("failed to read password: %w", err)
    }

    return string(password), nil
}

// Approach 3: Password from environment (with caveats)
func GetPasswordFromEnv(varName string) (string, error) {
    password := os.Getenv(varName)
    if password == "" {
        return "", fmt.Errorf("environment variable %s not set", varName)
    }
    
    // Warn about security implications
    fmt.Fprintln(os.Stderr, "Warning: Reading password from environment variable is less secure")
    
    return password, nil
}

// Approach 4: Password from stdin (for piping)
func GetPasswordFromStdin() (string, error) {
    if isatty.IsTerminal(os.Stdin.Fd()) {
        return "", fmt.Errorf("expected password from pipe, not terminal")
    }

    data, err := io.ReadAll(os.Stdin)
    if err != nil {
        return "", fmt.Errorf("failed to read from stdin: %w", err)
    }

    return strings.TrimSpace(string(data)), nil
}

// Unified password getter with multiple sources
func GetPassword(filePath, envVar string) (string, error) {
    // Priority: file > environment > interactive
    
    if filePath != "" {
        return GetPasswordFromFile(filePath)
    }
    
    if envVar != "" {
        if password, err := GetPasswordFromEnv(envVar); err == nil {
            return password, nil
        }
    }
    
    return GetPasswordInteractive("Password: ")
}
```

---

## Testing CLI Commands

### Unit Testing Commands

```go
package cmd_test

import (
    "bytes"
    "testing"

    "github.com/yourname/myapp/cmd"
)

func TestRootCommand(t *testing.T) {
    tests := []struct {
        name     string
        args     []string
        wantErr  bool
        wantOut  string
        wantErrOut string
    }{
        {
            name:    "no args shows help",
            args:    []string{},
            wantErr: true,
        },
        {
            name:   "help flag",
            args:   []string{"--help"},
            wantOut: "Usage:",
        },
        {
            name:   "version flag",
            args:   []string{"--version"},
            wantOut: "1.0.0",
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Reset command state
            cmd.RootCmd.ResetFlags()
            cmd.RootCmd.SetArgs(tt.args)

            // Capture output
            outBuf := new(bytes.Buffer)
            errBuf := new(bytes.Buffer)
            cmd.RootCmd.SetOut(outBuf)
            cmd.RootCmd.SetErr(errBuf)

            // Execute
            err := cmd.RootCmd.Execute()

            if (err != nil) != tt.wantErr {
                t.Errorf("Execute() error = %v, wantErr %v", err, tt.wantErr)
            }

            if tt.wantOut != "" && !bytes.Contains(outBuf.Bytes(), []byte(tt.wantOut)) {
                t.Errorf("Expected output to contain %q, got %q", tt.wantOut, outBuf.String())
            }

            if tt.wantErrOut != "" && !bytes.Contains(errBuf.Bytes(), []byte(tt.wantErrOut)) {
                t.Errorf("Expected stderr to contain %q, got %q", tt.wantErrOut, errBuf.String())
            }
        })
    }
}

// Test with environment variables
func TestCommandWithEnv(t *testing.T) {
    // Set env var
    t.Setenv("MYAPP_API_KEY", "test-key")
    
    // Run test...
}

// Test with temp directory
func TestCommandWithConfig(t *testing.T) {
    tmpDir := t.TempDir()
    configFile := filepath.Join(tmpDir, "config.yaml")
    
    // Write test config
    os.WriteFile(configFile, []byte("server:\n  port: 9999\n"), 0644)
    
    // Set args with config file
    cmd.RootCmd.SetArgs([]string{"--config", configFile, "server", "start"})
    
    // Execute and verify...
}
```

---

## Quick Reference: Common Patterns

### Exit Codes

```go
os.Exit(0) // Success
os.Exit(1) // General error
os.Exit(2) // Invalid arguments
os.Exit(3) // Configuration error
os.Exit(4) // Network error
os.Exit(130) // Interrupted (128 + SIGINT)
```

### Color Control Checklist

```go
func shouldUseColor() bool {
    if noColor || os.Getenv("MYAPP_NO_COLOR") != "" {
        return false
    }
    if os.Getenv("NO_COLOR") != "" {
        return false  // https://no-color.org
    }
    if os.Getenv("TERM") == "dumb" {
        return false
    }
    return isInteractive()
}
```

### Required Libraries

```bash
# Core CLI
go get github.com/spf13/cobra@latest

# TTY detection
go get github.com/mattn/go-isatty

# Colors
go get github.com/fatih/color

# Progress bars
go get github.com/schollz/progressbar/v3

# Configuration
go get github.com/spf13/viper
go get github.com/joho/godotenv

# Terminal utilities
go get golang.org/x/term
```

### Standard Flag Set

```go
rootCmd.PersistentFlags().BoolP("verbose", "v", false, "Enable verbose output")
rootCmd.PersistentFlags().BoolP("quiet", "q", false, "Suppress non-essential output")
rootCmd.PersistentFlags().Bool("json", false, "Output in JSON format")
rootCmd.PersistentFlags().Bool("no-color", false, "Disable colored output")
rootCmd.PersistentFlags().Bool("debug", false, "Enable debug output")
rootCmd.PersistentFlags().Bool("no-input", false, "Disable interactive prompts")
rootCmd.PersistentFlags().StringP("config", "c", "", "Config file path")
```
