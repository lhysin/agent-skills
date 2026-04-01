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

// Version info (injected at build time with -ldflags)
var (
	version = "dev"
	commit  = "none"
	date    = "unknown"
)

// Global flags
var (
	jsonOutput bool
	quietMode  bool
	debugMode  bool
	noColor    bool
	noInput    bool
	configFile string
)

// rootCmd represents the base command
var rootCmd = &cobra.Command{
	Use:   "myapp",
	Short: "Analyze files and generate reports",
	Long: `myapp is a CLI tool that analyzes files in various formats
and generates statistical reports.

Examples:
    myapp analyze report.txt           # Analyze a file
    myapp analyze --json *.log         # Analyze multiple files with JSON output
    myapp stats --output=result.csv    # Save statistics to CSV`,

	// Show help when run without arguments
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			cmd.Help()
			os.Exit(0)
		}
		// Process arguments...
	},

	SilenceUsage:  true,
	SilenceErrors: true,
}

// Execute runs the root command
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		PrintError("%v", err)
		os.Exit(1)
	}
}

func init() {
	cobra.OnInitialize(initConfig)

	// Global flags
	rootCmd.PersistentFlags().BoolVar(&jsonOutput, "json", false, "Output in JSON format")
	rootCmd.PersistentFlags().BoolVarP(&quietMode, "quiet", "q", false, "Suppress non-essential output")
	rootCmd.PersistentFlags().BoolVarP(&debugMode, "debug", "d", false, "Enable debug output")
	rootCmd.PersistentFlags().BoolVar(&noColor, "no-color", false, "Disable colored output")
	rootCmd.PersistentFlags().BoolVar(&noInput, "no-input", false, "Disable interactive prompts")
	rootCmd.PersistentFlags().StringVarP(&configFile, "config", "c", "", "Config file path")

	// Version flag
	rootCmd.Version = version
	rootCmd.SetVersionTemplate(`{{.Name}} version {{.Version}}
Commit:  ` + commit + `
Date:    ` + date + `
`)

	// Disable completion command (optional)
	rootCmd.CompletionOptions.DisableDefaultCmd = true
}

// initConfig initializes configuration
func initConfig() {
	initColorSettings()
}

// initColorSettings determines whether to use colors
func initColorSettings() {
	// Check explicit --no-color flag
	if noColor {
		disableColor()
		return
	}

	// Check NO_COLOR environment variable (https://no-color.org/)
	if os.Getenv("NO_COLOR") != "" {
		disableColor()
		return
	}

	// Check MYAPP_NO_COLOR environment variable
	if os.Getenv("MYAPP_NO_COLOR") != "" {
		disableColor()
		return
	}

	// Check TERM=dumb
	if os.Getenv("TERM") == "dumb" {
		disableColor()
		return
	}

	// Disable color if stdout is not a TTY
	if !IsOutputInteractive() {
		disableColor()
		return
	}
}

func disableColor() {
	noColor = true
	color.NoColor = true // Disable fatih/color
}

// IsInteractive returns true if stdin is a TTY
func IsInteractive() bool {
	return isatty.IsTerminal(os.Stdin.Fd()) ||
		isatty.IsCygwinTerminal(os.Stdin.Fd())
}

// IsOutputInteractive returns true if stdout is a TTY
func IsOutputInteractive() bool {
	return isatty.IsTerminal(os.Stdout.Fd()) ||
		isatty.IsCygwinTerminal(os.Stdout.Fd())
}

// IsStderrInteractive returns true if stderr is a TTY
func IsStderrInteractive() bool {
	return isatty.IsTerminal(os.Stderr.Fd()) ||
		isatty.IsCygwinTerminal(os.Stderr.Fd())
}

// ShouldUseColor returns true if colors should be used
func ShouldUseColor() bool {
	return !noColor
}

// PrintJSON outputs a value as formatted JSON
func PrintJSON(v interface{}) error {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

// PrintError prints an error message to stderr
func PrintError(format string, args ...interface{}) {
	if ShouldUseColor() {
		color.New(color.FgRed).Fprintf(os.Stderr, "Error: "+format+"\n", args...)
	} else {
		fmt.Fprintf(os.Stderr, "Error: "+format+"\n", args...)
	}
}

// PrintWarning prints a warning message to stderr
func PrintWarning(format string, args ...interface{}) {
	if quietMode {
		return
	}
	if ShouldUseColor() {
		color.New(color.FgYellow).Fprintf(os.Stderr, "Warning: "+format+"\n", args...)
	} else {
		fmt.Fprintf(os.Stderr, "Warning: "+format+"\n", args...)
	}
}

// PrintSuccess prints a success message to stderr
func PrintSuccess(format string, args ...interface{}) {
	if quietMode {
		return
	}
	if ShouldUseColor() {
		color.New(color.FgGreen).Fprintf(os.Stderr, format+"\n", args...)
	} else {
		fmt.Fprintf(os.Stderr, format+"\n", args...)
	}
}

// PrintHint prints a hint message to stderr
func PrintHint(format string, args ...interface{}) {
	if quietMode {
		return
	}
	fmt.Fprintf(os.Stderr, "Hint: "+format+"\n", args...)
}

// PrintDebug prints a debug message (only if --debug is enabled)
func PrintDebug(format string, args ...interface{}) {
	if !debugMode {
		return
	}
	fmt.Fprintf(os.Stderr, "[DEBUG] "+format+"\n", args...)
}

// PrintProgress prints a progress message (only if not --quiet and interactive)
func PrintProgress(format string, args ...interface{}) {
	if quietMode || !IsOutputInteractive() {
		return
	}
	fmt.Fprintf(os.Stderr, format+"\n", args...)
}

// SetupSignalHandling sets up graceful shutdown on Ctrl+C
func SetupSignalHandling(ctx context.Context) (context.Context, context.CancelFunc) {
	ctx, cancel := context.WithCancel(ctx)

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		sig := <-sigCh
		PrintProgress("\nReceived %s, shutting down gracefully...", sig)
		PrintProgress("(Press Ctrl+C again to force)")
		cancel()

		// Second signal forces immediate exit
		<-sigCh
		fmt.Fprintln(os.Stderr, "\nForced exit.")
		os.Exit(130) // 128 + SIGINT
	}()

	return ctx, cancel
}

// CheckArgs validates the number of arguments
func CheckArgs(min, max int) cobra.PositionalArgs {
	return func(cmd *cobra.Command, args []string) error {
		if len(args) < min {
			return fmt.Errorf("requires at least %d argument(s), received %d\n\nUse '%s --help' for usage", min, len(args), cmd.CommandPath())
		}
		if len(args) > max {
			return fmt.Errorf("accepts at most %d argument(s), received %d\n\nUse '%s --help' for usage", max, len(args), cmd.CommandPath())
		}
		return nil
	}
}
