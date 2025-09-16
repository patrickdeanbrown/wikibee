# Wikibee Configuration

The wikibee CLI reads optional user settings from
`~/.config/wikibee/config.toml`. Settings in this file override the built-in
defaults and provide baseline values for each run. CLI flags always take
precedence over the config file, so ad-hoc changes still work as expected.

## Creating the config file

- Run `wikibee config init` to generate a starter file (use `--force` to
  overwrite an existing file).
- Or create the directory `~/.config/wikibee/` and add a file named
  `config.toml` manually.

The generated template contains sensible defaults that you can customize. The
example below highlights the available sections and keys.

```toml
[general]
output_dir = "/home/user/wikipedia"
default_timeout = 30
lead_only = false
verbose = false

[tts]
server_url = "http://localhost:8880/v1"
default_voice = "af_sky+af_bella"
format = "mp3"
normalize = false
heading_prefix = "Section:"

[search]
auto_select = false
search_limit = 10
```

## Settings reference

### `[general]`

- `output_dir`: Default directory where markdown files are written. Supports
  `~` expansion.
- `default_timeout`: Timeout (seconds) for Wikipedia API calls when no CLI
  value is provided.
- `lead_only`: Whether to fetch only the article introduction by default.
- `verbose`: Enables debug logging without requiring `--verbose` each run.

### `[tts]`

- `server_url`: Base URL for the OpenAI-compatible TTS server.
- `default_voice`: Voice identifier passed to the TTS service.
- `format`: Audio format for synthesized files (for example `mp3` or `wav`).
- `normalize`: Toggle the extra text normalization step used for TTS output.
- `heading_prefix`: Optional prefix prepended to headings in TTS text files.

### `[search]`

- `auto_select`: When true, behaves like the `--yolo` flag and picks the first
  search result automatically.
- `search_limit`: How many search results to fetch when resolving article
  titles (matches the `--search-limit` option).

## Precedence

Configuration values are merged with the following priority:

1. Built-in defaults
2. Values in `config.toml`
3. CLI flags and environment overrides

This means the config file defines new defaults, while explicit CLI flags still
win when present.
