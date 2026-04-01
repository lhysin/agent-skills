# CLI Quality Checklist

A comprehensive checklist for verifying CLI quality based on [clig.dev](https://clig.dev/) guidelines.

---

## The Basics (Must Have - Get These Wrong = Broken Program)

### Exit Codes
- [ ] Return exit code 0 on success
- [ ] Return non-zero exit code on failure
- [ ] Map different failure modes to specific exit codes (recommended)

### Output Streams
- [ ] Primary output (data) goes to `stdout`
- [ ] Logs, progress, and errors go to `stderr`
- [ ] Works correctly in pipelines (`cmd1 | cmd2 | cmd3`)

### Help
- [ ] `-h` flag displays help
- [ ] `--help` flag displays help
- [ ] Running without required arguments shows concise help
- [ ] Help includes examples
- [ ] Help describes major flags
- [ ] Subcommands have individual help (`myapp subcmd --help`)

### Version
- [ ] `--version` flag displays version
- [ ] Version info includes build info (optional)

---

## Arguments and Flags (Should Have)

### Flag Design
- [ ] All flags have long versions (`-o` → `--output`)
- [ ] Only commonly used flags have short versions
- [ ] Use standard flag names (`--help`, `--version`, `--quiet`, etc.)
- [ ] Flags work regardless of order
- [ ] Prefer flags over arguments for clarity
- [ ] Support `-` for stdin/stdout

### Standard Flags to Implement
- [ ] `-h`, `--help` - Help
- [ ] `--version` - Version
- [ ] `-v`, `--verbose` - Verbose output
- [ ] `-q`, `--quiet` - Quiet mode
- [ ] `--json` - JSON output
- [ ] `--no-color` - Disable colors
- [ ] `-n`, `--dry-run` - Dry run (if applicable)
- [ ] `-f`, `--force` - Force action (if applicable)

### Arguments
- [ ] Multiple arguments only for same-type items (e.g., files)
- [ ] Avoid two different argument types unless very common (e.g., `cp`)

---

## Output (Should Have)

### Output Formats
- [ ] `--json` flag for structured JSON output
- [ ] `--quiet`/`-q` flag to suppress non-essential output
- [ ] `--plain` flag for script-friendly tabular output (if applicable)
- [ ] Notify user of state changes
- [ ] Suggest next commands in workflows (if applicable)

### TTY Detection
- [ ] Detect if `stdout` is a TTY
- [ ] Disable colors when not a TTY
- [ ] Disable animations/progress bars when not a TTY
- [ ] Skip prompts when not a TTY (fail with error instead)

### Color Usage
- [ ] Respect `NO_COLOR` environment variable
- [ ] Respect `TERM=dumb` environment variable
- [ ] Provide `--no-color` flag
- [ ] Use colors intentionally (red=error, green=success, etc.)
- [ ] Don't rely solely on color (consider colorblind users)
- [ ] Disable color when piping output

### Progress Indication
- [ ] Print something within 100ms of start
- [ ] Show progress for operations >100ms
- [ ] Show progress bars only in interactive TTY mode
- [ ] Show textual progress in non-TTY mode

---

## Error Handling (Should Have)

### Error Messages
- [ ] Human-readable error messages (not stack traces by default)
- [ ] Suggest solutions to errors
- [ ] Place important information at the end of output
- [ ] Hide stack traces by default (show with `--debug`)
- [ ] Group similar errors instead of spamming multiple lines

### Input Validation
- [ ] Validate all user input
- [ ] Provide clear feedback on validation failures
- [ ] Suggest corrections for typos (optional)

### Debug Mode
- [ ] `--debug` flag shows debug information
- [ ] Write debug logs to file instead of terminal (optional)

---

## Interactivity (Should Have)

### Prompts
- [ ] Don't prompt if `stdin` is not a TTY
- [ ] `--no-input` flag disables all prompts
- [ ] Disable echo for password input
- [ ] Required inputs can also be passed via flags
- [ ] Skip prompts in non-interactive environments (fail with clear error)

### Dangerous Operations
- [ ] Confirm before destructive actions
- [ ] `--force`/`-f` flag skips confirmation
- [ ] `--dry-run`/`-n` flag shows what would happen (if applicable)
- [ ] Require typing name for severe deletions

---

## Robustness (Should Have)

### Signal Handling
- [ ] Handle Ctrl+C (SIGINT) immediately
- [ ] Allow second Ctrl+C to force exit during cleanup
- [ ] Set timeout on cleanup operations
- [ ] Print message when interrupted

Example behavior:
```
^CGracefully stopping... (press Ctrl+C again to force)
```

### Network Operations
- [ ] Set network timeouts
- [ ] Design for retryability
- [ ] Notify user before network operations
- [ ] Handle network failures gracefully

### Long-Running Operations
- [ ] Print something within 100ms
- [ ] Show progress (bar or messages)
- [ ] Show estimated time if possible
- [ ] Allow cancellation

### Idempotency
- [ ] Same command can be run multiple times safely
- [ ] Check if work is already done before doing it
- [ ] Handle partial failures gracefully

---

## Configuration (Should Have)

### Configuration Priority (High to Low)
- [ ] Flags
- [ ] Shell environment variables
- [ ] Project-level config (`.myapprc`, `.env`)
- [ ] User-level config (`~/.config/myapp/`)
- [ ] System-wide config (`/etc/myapp/`)

### Environment Variables
- [ ] Use UPPERCASE_WITH_UNDERSCORES for env var names
- [ ] Use prefix for app-specific vars (`MYAPP_`)
- [ ] Respect common env vars (`HOME`, `EDITOR`, `PAGER`, `NO_COLOR`, etc.)

### Standard Environment Variables to Check
- [ ] `NO_COLOR` / `FORCE_COLOR` - Color control
- [ ] `DEBUG` - Debug output
- [ ] `EDITOR` - Text editor
- [ ] `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY` - Network proxy
- [ ] `PAGER` - Output pager (e.g., `less`)
- [ ] `HOME` - Home directory
- [ ] `TMPDIR` - Temporary files
- [ ] `TERM` - Terminal type

### XDG Specification
- [ ] Respect `XDG_CONFIG_HOME` (default: `~/.config`)
- [ ] Respect `XDG_DATA_HOME` (default: `~/.local/share`)
- [ ] Respect `XDG_CACHE_HOME` (default: `~/.cache`)

### .env Files
- [ ] Read `.env` for project-specific settings (optional)
- [ ] Don't use .env as substitute for proper config files

---

## Security (Must Have)

### Secrets Handling
- [ ] Never accept secrets via flags (leaks to `ps`, shell history)
- [ ] Provide `--password-file` or similar for secrets
- [ ] Accept secrets via `stdin` or environment variables (with caveats)
- [ ] Don't log secrets
- [ ] Don't include secrets in error messages
- [ ] Don't store secrets in environment variables long-term

### Environment Variable Security
- [ ] Don't rely on env vars for secrets (visible to all processes, logs)
- [ ] Prefer files, pipes, sockets, or secret management services

---

## Future-Proofing (Should Have)

### Compatibility
- [ ] Warn before breaking changes
- [ ] Make changes additive where possible
- [ ] Don't use catch-all subcommands (blocks adding new ones)
- [ ] Don't auto-expand subcommand abbreviations (blocks adding new ones)

### Output Stability
- [ ] Changing human output is usually OK
- [ ] Encourage `--plain` or `--json` for script stability
- [ ] Document which output is stable for scripting

---

## Documentation (Should Have)

### Help Text
- [ ] Concise one-sentence description
- [ ] 1-3 usage examples
- [ ] Flag descriptions
- [ ] Web documentation link (if available)
- [ ] Support path (GitHub issues, email, etc.)

### Additional Documentation
- [ ] README.md with installation and usage
- [ ] man pages (optional)
- [ ] Web documentation (optional)
- [ ] Link to web docs from help text

---

## Distribution (Should Have)

- [ ] Distribute as single binary (Go's strength)
- [ ] Document uninstallation method
- [ ] Support major platforms (Linux, macOS, Windows)
- [ ] Consider package managers (brew, apt, etc.)

---

## Naming (Should Have)

### Program Name
- [ ] Simple, memorable word
- [ ] Lowercase letters, dashes if needed
- [ ] Not too generic
- [ ] Not too short (avoid 2-letter names unless common utility)
- [ ] Easy to type

### Subcommand Naming
- [ ] Use `noun verb` pattern consistently (e.g., `docker container create`)
- [ ] Avoid ambiguous/similar names (e.g., "update" vs "upgrade")
- [ ] Same verb means same action across nouns

---

## Analytics (Must Have Ethics)

- [ ] **Do not phone home without explicit consent**
- [ ] Be explicit about what data is collected
- [ ] Be explicit about why data is collected
- [ ] Be explicit about anonymity
- [ ] Be explicit about data retention
- [ ] Opt-in preferred over opt-out
- [ ] If opt-out, clearly disclose and make easy to disable

Alternatives to consider:
- Instrument web docs
- Instrument downloads
- Talk to users directly

---

## Scoring

Calculate your CLI's quality score:

### Section Weights

| Section | Weight | Items |
|---------|--------|-------|
| The Basics | Critical | Must be 100% |
| Security | Critical | Must be 100% |
| Arguments and Flags | High | Target 80%+ |
| Output | High | Target 80%+ |
| Error Handling | High | Target 80%+ |
| Robustness | Medium | Target 70%+ |
| Interactivity | Medium | Target 70%+ |
| Configuration | Medium | Target 60%+ |
| Documentation | Medium | Target 70%+ |
| Future-Proofing | Low | Nice to have |
| Distribution | Low | Nice to have |

### Score Calculation

```
Basics:      ____ / ____ (checked / total) = ____%
Security:    ____ / ____ (checked / total) = ____%
Flags:       ____ / ____ (checked / total) = ____%
Output:      ____ / ____ (checked / total) = ____%
Errors:      ____ / ____ (checked / total) = ____%
Robustness:  ____ / ____ (checked / total) = ____%
Interactivity: ____ / ____ (checked / total) = ____%
Config:      ____ / ____ (checked / total) = ____%
Docs:        ____ / ____ (checked / total) = ____%
Future:      ____ / ____ (checked / total) = ____%
Distribution: ____ / ____ (checked / total) = ____%

Overall Quality Score: ____%
```

### Quality Levels

- **90-100%**: Excellent - Production-ready, delightful to use
- **80-89%**: Good - Solid implementation with minor gaps
- **70-79%**: Acceptable - Functional but has room for improvement
- **60-69%**: Needs Work - Missing important features
- **<60%**: Major Issues - Not ready for production

---

## Quick Reference: Go Libraries

| Purpose | Recommended Library |
|---------|-------------------|
| CLI Framework | [Cobra](https://github.com/spf13/cobra) - Powerful, widely used |
| CLI Framework | [urfave/cli](https://github.com/urfave/cli) - Simple, idiomatic |
| TTY Detection | [mattn/go-isatty](https://github.com/mattn/go-isatty) |
| Progress Bars | [schollz/progressbar](https://github.com/schollz/progressbar) |
| Colors | [fatih/color](https://github.com/fatih/color) |
| Config Files | [spf13/viper](https://github.com/spf13/viper) |
| .env Files | [joho/godotenv](https://github.com/joho/godotenv) |
| Password Input | [golang.org/x/term](https://pkg.go.dev/golang.org/x/term) |

---

## Review Workflow

When reviewing existing CLI code:

1. **Check The Basics first** - Exit codes, stdout/stderr, help
2. **Check Security** - Secrets handling, env var usage
3. **Review Output** - TTY detection, color control, JSON support
4. **Review Errors** - Human-readable messages, suggestions
5. **Test Interactivity** - Prompts, dangerous operations
6. **Check Robustness** - Signals, timeouts, idempotency
7. **Review Config** - XDG compliance, env vars
8. **Check Documentation** - Help text, examples

Document findings and provide specific recommendations with code examples.
