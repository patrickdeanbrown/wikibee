# Basic Usage Tutorial

This tutorial covers the fundamental features of wikibee. After completing this guide, you'll understand how to effectively search, extract, and process Wikipedia articles.

## Table of Contents
- [Installation and Setup](#installation-and-setup)
- [Basic Article Extraction](#basic-article-extraction)
- [Search Methods](#search-methods)
- [Output Options](#output-options)
- [TTS-Ready Text Generation](#tts-ready-text-generation)
- [File Management](#file-management)
- [Error Handling](#error-handling)

## Installation and Setup

### Installing wikibee

```bash
# Recommended: Use pipx for isolated installation
pipx install wikibee

# Alternative: Use pip  
pip install wikibee

# Verify installation
wikibee --version
wikibee --help
```

### First Test

```bash
# Simple test to ensure everything works
wikibee "Python" --lead-only
```

This should create a `python.md` file with the introduction section of the Python Wikipedia article.

## Basic Article Extraction

### Simple Article Download

The most basic usage is to download an article by search term:

```bash
wikibee "Albert Einstein"
```

What happens:
1. wikibee searches Wikipedia for "Albert Einstein"
2. If multiple results exist, shows an interactive menu
3. Downloads the selected article
4. Saves as `albert_einstein.md` in the current directory

### Direct URL Usage

If you know the exact Wikipedia URL:

```bash
wikibee "https://en.wikipedia.org/wiki/Quantum_mechanics"
```

This bypasses search and downloads the article directly.

## Search Methods

### Fuzzy Search

wikibee uses Wikipedia's search API with fuzzy matching:

```bash
# These all work despite typos/variations:
wikibee "einstien"           # Finds "Einstein"
wikibee "war fo the roses"   # Finds "Wars of the Roses"  
wikibee "quantm physics"     # Finds "Quantum physics"
```

### Interactive Selection

When multiple results exist, wikibee shows a numbered menu:

```bash
wikibee "Paris"
```

Output:
```
Multiple articles found for "Paris":

1. Paris
2. Paris, France  
3. Paris, Texas
4. Paris Hilton
5. Paris Saint-Germain F.C.

Select an article (1-5): 1
```

### Auto-Selection with --yolo

Skip the interactive menu and select the first result:

```bash
wikibee "Paris" --yolo
```

This automatically selects the most relevant match.

### Search Result Limits

Control how many search results to show:

```bash
# Show more options (default is 10)
wikibee "Paris" --search-limit 15

# Show fewer options for faster selection
wikibee "Paris" --search-limit 3
```

## Output Options

### Custom Output Directory

Save files to a specific directory:

```bash
# Create directory and save there
wikibee "Marie Curie" --output biographies/

# Use existing directory
wikibee "Tesla" --output scientists/
```

### Custom Filenames

Override the default filename:

```bash
wikibee "Leonardo da Vinci" --filename leonardo --output artists/
# Creates: artists/leonardo.md
```

### Lead Section Only

Get just the introduction/summary:

```bash
wikibee "Machine Learning" --lead-only
# Much faster, smaller files, good for summaries
```

## TTS-Ready Text Generation

### Basic TTS Text

Generate text optimized for text-to-speech engines:

```bash
wikibee "Shakespeare" --tts
```

This creates two files:
- `shakespeare.md` - Original markdown with formatting
- `shakespeare.txt` - TTS-optimized text without markdown markers

### TTS Text Features

The TTS-optimized text:
- Removes markdown formatting (`#`, `*`, `**`, etc.)
- Converts numbers to words (optional, requires `inflect` package)
- Adds custom heading prefixes
- Removes Wikipedia-specific markup

### Custom Heading Prefixes

Add prefixes to make headings clearer in audio:

```bash
wikibee "World War II" --tts --heading-prefix "Section:"
```

In the TTS file:
```
Section: Background
Section: Course of the war  
Section: Aftermath
```

### Number-to-Word Conversion

If you have the `inflect` package installed:

```bash
pip install inflect

wikibee "Mathematics" --tts
# "21st century" becomes "twenty-first century"
# "1969" becomes "nineteen sixty-nine"
```

## File Management

### Understanding Output Files

Standard extraction:
```bash
wikibee "Photosynthesis"
# Creates: photosynthesis.md
```

With TTS option:
```bash
wikibee "Photosynthesis" --tts
# Creates: photosynthesis.md AND photosynthesis.txt
```

### File Naming Rules

wikibee automatically sanitizes filenames:
- Removes special characters: `/, \, :, *, ?, ", <, >, |`
- Replaces spaces with underscores
- Converts to lowercase
- Removes Wikipedia disambiguation suffixes

Examples:
- "Leonardo da Vinci" → `leonardo_da_vinci.md`
- "Paris, France" → `paris_france.md`
- "C++ (programming language)" → `c_programming_language.md`

### Preventing Overwrites

By default, wikibee overwrites existing files. To prevent this:

```bash
# Check if file exists first
ls photosynthesis.md && echo "File exists!" || wikibee "Photosynthesis"

# Use custom filename to avoid conflicts
wikibee "Photosynthesis" --filename photosynthesis_v2
```

## Error Handling

### Network Issues

Handle slow or unreliable connections:

```bash
# Increase timeout (default: 15 seconds)
wikibee "Large Article" --timeout 30

# Retry after a short pause if the API was busy
sleep 5 && wikibee "Topic"
```

### No Search Results

When searches return no results:

```bash
wikibee "nonexistent topic xyz123"
# Output: No articles found for "nonexistent topic xyz123"
```

Try:
- Broader search terms
- Check spelling
- Use alternative terms

### Disambiguation Pages

Sometimes wikibee finds disambiguation pages:

```bash
wikibee "Mercury"  # Might find disambiguation page
```

The tool will:
1. Detect disambiguation pages
2. Show available options
3. Let you select the specific article you want

### Common Error Messages

**"Article not found"**
- The Wikipedia page doesn't exist
- Try alternative search terms

**"Connection timeout"**
- Network is slow or unavailable  
- Increase timeout or try later

**"Invalid URL"**
- URL format is incorrect
- Ensure it's a valid Wikipedia URL

**"Access denied"**
- Wikipedia is blocking requests (rare)
- Wait a few minutes and try again

## Best Practices

### Efficient Workflows

1. **Use --lead-only for quick research**:
   ```bash
   wikibee "Topic" --lead-only  # Fast overview
   ```

2. **Organize with directories**:
   ```bash
   wikibee "Photosynthesis" --output biology/
   wikibee "Mitosis" --output biology/
   wikibee "Evolution" --output biology/
   ```

3. **Batch similar content**:
   ```bash
   # Research multiple related topics
   for topic in "Newton" "Galileo" "Kepler"; do
     wikibee "$topic" --output scientists/ --tts
   done
   ```

### Performance Tips

- Use `--lead-only` for faster downloads
- Use `--yolo` to skip interactive selection
- Increase `--timeout` for large articles
- Process articles individually rather than in large batches

### Content Quality

- Search with specific terms for better results
- Use direct URLs when you know the exact page
- Check the generated files for accuracy
- Some Wikipedia articles may have formatting issues

## Next Steps

Now that you understand basic usage, explore these next steps:

- **[Python API Usage](api-usage.md)** - Programmatic access  
- **[CLI Reference](../reference/cli-reference.md)** - Complete command documentation
- **[Configuration Guide](../reference/configuration.md)** - Customize defaults
- **[Examples Guide](../guides/examples.md)** - Real-world workflows

## Quick Reference

```bash
# Basic usage
wikibee "search term"                    # Interactive search
wikibee "search term" --yolo             # Auto-select first result
wikibee "URL"                            # Direct URL

# Output control  
wikibee "term" --output directory/       # Save to directory
wikibee "term" --filename custom         # Custom filename
wikibee "term" --lead-only              # Just introduction

# TTS generation
wikibee "term" --tts                     # Create TTS-ready text
wikibee "term" --tts --heading-prefix "Section:"  # Custom headings

# Network options
wikibee "term" --timeout 30              # Increase timeout
sleep 5 && wikibee "term"               # Retry after a short pause
```

---

**Navigation**: [Documentation Home](../README.md) | [Quick Start](../quickstart.md) | [API Usage](api-usage.md)
