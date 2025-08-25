# Quick Start Guide

Get up and running with wikibee in under 5 minutes! This guide will take you from installation to creating your first TTS-ready content.

## Step 1: Install wikibee

The easiest way to install wikibee is with pipx:

```bash
pipx install wikibee
```

Alternative installations:
```bash
# Using pip
pip install wikibee

# Verify installation
wikibee --help
```

## Step 2: Your First Article

Let's extract a Wikipedia article about Albert Einstein:

```bash
wikibee "Albert Einstein"
```

This will:
1. Search Wikipedia for "Albert Einstein"  
2. Show you search results if there are multiple matches
3. Download and clean the article
4. Save it as `albert_einstein.md` in the current directory

## Step 3: Generate TTS-Ready Text

Now let's create text optimized for text-to-speech:

```bash
wikibee "Albert Einstein" --tts
```

This creates two files:
- `albert_einstein.md` - Clean markdown for reading
- `albert_einstein.txt` - TTS-optimized text without formatting markers

## Step 4: Organize Your Output

Save files to a specific directory:

```bash
wikibee "Marie Curie" --tts --output biographies/
```

This creates the `biographies/` directory and saves files there.

## Step 5: Try Different Search Methods

### Search by Keywords
```bash
# Fuzzy search handles typos and partial matches
wikibee "war fo the roses"  # Still finds "Wars of the Roses"

# Auto-select the first result (no interactive menu)
wikibee "quantum physics" --yolo
```

### Use Direct URLs
```bash
# Extract a specific Wikipedia page
wikibee "https://en.wikipedia.org/wiki/Machine_learning" --tts
```

### Get Just the Introduction
```bash
# Extract only the lead section for quick summaries
wikibee "artificial intelligence" --lead-only --output summaries/
```

## Common Use Cases

### For Accessibility
Create clean text files perfect for screen readers:
```bash
wikibee "Python programming language" --tts --output accessibility/
```

### For Research
Quickly gather information on multiple topics:
```bash
wikibee "photosynthesis" --output biology/ --filename plants_photosynthesis
wikibee "mitosis" --output biology/ --filename cell_division
```

### For Audio Content Creation
Generate TTS-ready text with custom formatting:
```bash
wikibee "Mozart" --tts --heading-prefix "Section:" --output audio-prep/
```

## Troubleshooting

### Common Issues

**Command not found**
```bash
# If wikibee command isn't found after installation:
pipx ensurepath
# Then restart your terminal
```

**Search returns no results**
```bash
# Try broader search terms or check spelling
wikibee "einstein" --yolo  # Simpler search
```

**Network errors**
```bash
# Add timeout for slow connections
wikibee "topic" --timeout 30
```

### Getting Help

- Run `wikibee --help` for command options
- See [Troubleshooting Guide](reference/troubleshooting.md) for detailed solutions
- Check [CLI Reference](reference/cli-reference.md) for all available options

## What's Next?

- **Learn more features**: [Basic Usage Tutorial](tutorial/basic-usage.md)
- **Python integration**: [API Tutorial](tutorial/api-usage.md)
- **Audio setup**: [TTS Server Setup](tutorial/tts-setup.md)
- **Advanced techniques**: [Advanced CLI Tutorial](tutorial/advanced-cli.md)

## Quick Reference

```bash
# Basic usage
wikibee "topic"                    # Search and download
wikibee "topic" --tts              # Include TTS-ready text  
wikibee "topic" --output dir/      # Save to directory
wikibee "topic" --lead-only        # Just introduction
wikibee "topic" --yolo             # Auto-select first result

# Direct URL
wikibee "https://en.wikipedia.org/wiki/Page_Name"

# Custom options
wikibee "topic" --heading-prefix "Section:" --timeout 30
```

You're now ready to start extracting Wikipedia content with wikibee! Explore the other documentation sections to learn about advanced features and integration options.

---

**Navigation**: [Documentation Home](README.md) | [Basic Tutorial](tutorial/basic-usage.md) | [CLI Reference](reference/cli-reference.md)
