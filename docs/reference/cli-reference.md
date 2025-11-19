# CLI Reference

Complete command-line interface documentation for wikibee. This reference covers all available commands, options, and usage patterns.

## Basic Syntax

```bash
wikibee [ARTICLE] [OPTIONS]
```

## Positional Arguments

### ARTICLE
The Wikipedia article to extract. Can be:
- **Search term**: `"Albert Einstein"`
- **Wikipedia URL**: `"https://en.wikipedia.org/wiki/Quantum_mechanics"`
- **Page title**: `"Machine_learning"`

```bash
# Search term examples
wikibee "artificial intelligence"
wikibee "war of the roses"

# URL examples  
wikibee "https://en.wikipedia.org/wiki/Python_(programming_language)"

# Exact page title
wikibee "Machine_learning"
```

## Global Options

### --help, -h
Show help message and exit.

```bash
wikibee --help
wikibee -h
```

### --version
Show program version and exit.

```bash
wikibee --version
```

### --verbose, -v
Enable verbose output for debugging.

```bash
wikibee "topic" --verbose
```

## Search and Selection Options

### --yolo, -y
Auto-select the first search result without showing the interactive menu.

```bash
wikibee "quantum physics" --yolo
```

**Use when:**
- You're confident about the search term
- Running automated scripts  
- The first result is usually correct

### --search-limit N
Control how many search results to show (default: 10).

```bash
# Show more options
wikibee "Paris" --search-limit 15

# Show fewer for faster selection
wikibee "Paris" --search-limit 3
```

## Output Control Options

### --output DIR, -o DIR
Specify output directory. Creates the directory if it doesn't exist.

```bash
# Save to specific directory
wikibee "Marie Curie" --output biographies/

# Save to nested directory
wikibee "Photosynthesis" --output science/biology/
```

### --filename NAME, -f NAME
Custom filename (without extension).

```bash
wikibee "Leonardo da Vinci" --filename leonardo
# Creates: leonardo.md (and leonardo.txt if --tts used)

wikibee "C++ programming" --filename cpp_guide --output programming/
# Creates: programming/cpp_guide.md
```

### --no-save, -n
Process the article but don't save files (useful for testing).

```bash
wikibee "Test Article" --no-save --verbose
```

## Content Options

### --lead-only, -l
Extract only the lead section (introduction). Much faster for summaries.

```bash
# Quick summary
wikibee "Machine Learning" --lead-only

# Save summary to directory
wikibee "Artificial Intelligence" --lead-only --output summaries/
```

**Benefits:**
- Faster extraction
- Smaller files
- Good for overviews and research

### --tts
Generate TTS-optimized text file alongside the markdown file.

```bash
wikibee "Shakespeare" --tts
# Creates: shakespeare.md AND shakespeare.txt
```

**TTS file features:**
- Removes markdown formatting
- Converts numbers to words (if inflect available)
- Strips Wikipedia markup
- Optimized for text-to-speech engines

### --heading-prefix PREFIX
Add prefix to headings in TTS file for clearer audio navigation.

```bash
wikibee "World War II" --tts --heading-prefix "Section:"

# In TTS file:
# "Section: Background"
# "Section: Course of the war"
```

**Common prefixes:**
- `"Section:"` - General use
- `"Chapter:"` - Book-like content
- `"Part:"` - Long articles
- `""` - No prefix (empty string)

## Network Options

### --timeout SECONDS, -t SECONDS
HTTP request timeout in seconds (default: 15).

```bash
# Longer timeout for large articles or slow connections
wikibee "Very Long Article" --timeout 30

# Shorter timeout for quick failures
wikibee "Quick Test" --timeout 5
```

## Audio Generation Options

### --audio
Generate audio file using TTS server (requires TTS server setup).

```bash
wikibee "Short Article" --audio
# Creates: .md, .txt, and .mp3 files
```

**Prerequisites:**
- TTS server running (e.g., Kokoro TTS)
- Server accessible at localhost:8880 (default)
- Article should be reasonably short for audio

### --tts-voice VOICE
Specify TTS voice (server-dependent).

```bash
wikibee "Article" --audio --tts-voice "af_sky+af_bella"
```

### --tts-format FORMAT
Specify audio output format (default: mp3).
Supported formats: `mp3`, `wav`, `m4b`, etc.

**Special Feature**: When using `m4b`, wikibee automatically creates chapters from Wikipedia section headers.

```bash
wikibee "Long Article" --audio --tts-format m4b
```

### --tts-normalize
Apply advanced text normalization to improve pronunciation (e.g., expanding abbreviations, fixing spacing).

```bash
wikibee "Technical Article" --audio --tts-normalize
```

## Configuration Management

### config init
Initialize a default configuration file at `~/.config/wikibee/config.toml`.

```bash
wikibee config init
wikibee config init --force  # Overwrite existing config
```

## Example Commands

### Basic Usage
```bash
# Simple extraction
wikibee "Albert Einstein"

# Extract with TTS optimization
wikibee "Marie Curie" --tts

# Quick summary
wikibee "Quantum Mechanics" --lead-only
```

### Organization
```bash
# Organize by topic
wikibee "Photosynthesis" --output biology/ --tts
wikibee "Mitosis" --output biology/ --tts  
wikibee "Evolution" --output biology/ --tts

# Custom filenames
wikibee "C++ (programming language)" --filename cpp_basics --output programming/
```

### Automation-Friendly
```bash
# Non-interactive processing
wikibee "Machine Learning" --yolo --output research/ --tts --timeout 30

# Batch processing (shell script)
for topic in "Newton" "Einstein" "Curie"; do
  wikibee "$topic" --yolo --output scientists/ --tts
done
```

### Research Workflow
```bash
# Quick research summaries
wikibee "Artificial Intelligence" --lead-only --output summaries/
wikibee "Machine Learning" --lead-only --output summaries/  
wikibee "Neural Networks" --lead-only --output summaries/

# Detailed research with audio
wikibee "Deep Learning" --tts --audio --output research/detailed/
```

## Exit Codes

wikibee returns standard exit codes:

- **0**: Success
- **1**: General error (network, processing, etc.)
- **2**: Article not found or no search results
- **3**: User cancelled operation
- **4**: Invalid arguments or configuration

```bash
# Check exit code in scripts
wikibee "Valid Article" && echo "Success" || echo "Failed"

# Conditional processing
if wikibee "Test Topic" --yolo; then
    echo "Article extracted successfully"
else
    echo "Extraction failed with code $?"
fi
```

## Configuration File

wikibee looks for configuration in `~/.config/wikibee/config.toml`:

```toml
[general]
output_dir = "/home/user/wikipedia"
default_timeout = 30
lead_only = false
no_save = false
verbose = false

[tts]
server_url = "http://localhost:8880/v1"
default_voice = "af_sky+af_bella"
format = "mp3"
normalize = true
file = true
audio = false
heading_prefix = "Section:"

[search]  
auto_select = false
search_limit = 10
```

## Advanced Examples

### Content Pipeline
```bash
# Research pipeline: summary → full article → audio
wikibee "Topic" --lead-only --output research/summaries/
wikibee "Topic" --tts --output research/full/ --timeout 30
wikibee "Topic" --audio --output research/audio/ --tts-voice custom
```

### Quality Control
```bash
# Test extraction without saving
wikibee "Test Topic" --no-save --verbose

# Quick validation
wikibee "Known Good Article" --lead-only --timeout 5
```

### Batch Research
```bash
#!/bin/bash
# Batch research script

TOPICS=("Machine Learning" "Artificial Intelligence" "Deep Learning")
OUTPUT_DIR="ai_research"

for topic in "${TOPICS[@]}"; do
    echo "Processing: $topic"
    
    # Summary
    wikibee "$topic" --lead-only --output "$OUTPUT_DIR/summaries/" --yolo
    
    # Full article with TTS
    wikibee "$topic" --tts --output "$OUTPUT_DIR/full/" --yolo --timeout 30
    
    echo "Completed: $topic"
done
```

## Performance Tips

### Speed Optimization
- Use `--lead-only` for faster extraction
- Use `--yolo` to skip interactive selection
- Set appropriate `--timeout` values
- Process articles sequentially rather than in parallel

### Network Efficiency
- Retry the command after a short pause on flaky connections
- Use longer `--timeout` for large articles
- Test with `--no-save --verbose` before bulk operations

### File Management
- Use `--output` to organize files
- Use `--filename` to avoid naming conflicts
- Check disk space before large batch operations

## Troubleshooting

### Common Issues

**Command not found**
```bash
# Ensure wikibee is properly installed
pipx install wikibee
pipx ensurepath
```

**Network timeouts**
```bash
# Increase timeout
wikibee "Topic" --timeout 30
```

**No search results**
```bash
# Try broader terms or check spelling
wikibee "einstein" --yolo  # Simpler search
```

**Permission errors**
```bash
# Check directory permissions
wikibee "Topic" --output ~/Documents/wikipedia/
```

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).

---

**Navigation**: [Documentation Home](../README.md) | [Quick Start](../quickstart.md) | [Configuration](configuration.md) | [Troubleshooting](troubleshooting.md)
