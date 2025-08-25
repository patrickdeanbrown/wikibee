# Troubleshooting Guide

This guide covers common issues when using wikibee and provides solutions for typical problems.

## Installation Issues

### Command Not Found

**Problem**: `wikibee: command not found` after installation.

**Solutions**:

1. **pipx installation** (recommended):
   ```bash
   pipx install wikibee
   pipx ensurepath
   # Restart your terminal
   ```

2. **Check PATH**:
   ```bash
   # Verify pipx binaries are in PATH
   echo $PATH | grep -E "(\.local/bin|pipx)"
   
   # If not found, add to your shell profile
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **pip installation fallback**:
   ```bash
   pip install wikibee
   python -m wikibee --help  # Test module access
   ```

4. **Virtual environment issues**:
   ```bash
   # If installed in a venv, activate it
   source venv/bin/activate
   wikibee --help
   ```

### Permission Errors

**Problem**: Permission denied when installing or running.

**Solutions**:

```bash
# Use pipx (isolated installation)
pipx install wikibee

# Or install for current user only
pip install --user wikibee

# Fix permissions if needed
chmod +x ~/.local/bin/wikibee
```

### Python Version Issues

**Problem**: Incompatible Python version.

**Requirements**: Python 3.8 or higher

**Solutions**:

```bash
# Check Python version
python --version
python3 --version

# Use specific Python version
python3.9 -m pip install wikibee
python3.9 -m wikibee --help

# With pipx, specify Python version
pipx install --python python3.9 wikibee
```

## Search and Extraction Issues

### No Search Results

**Problem**: "No articles found for 'search term'"

**Causes**:
- Misspelled search terms
- Very specific or uncommon topics
- Network connectivity issues

**Solutions**:

```bash
# Try broader search terms
wikibee "einstein" instead of "albert einstein theory"

# Check spelling and try variations
wikibee "artificial intelligence"  # instead of "artifical inteligence"

# Use different search strategies
wikibee "AI" --yolo  # Simpler terms
wikibee "machine learning basics"  # Add context
```

### Disambiguation Pages

**Problem**: wikibee finds a disambiguation page instead of the article.

**Example**: Searching "Mercury" returns disambiguation page.

**Solutions**:

```bash
# Be more specific in search
wikibee "Mercury planet"
wikibee "Mercury chemical element" 
wikibee "Mercury mythology"

# Use direct Wikipedia URLs
wikibee "https://en.wikipedia.org/wiki/Mercury_(planet)"

# Let wikibee show options and choose
wikibee "Mercury"  # Select from the menu
```

### Article Not Found

**Problem**: Specific Wikipedia page doesn't exist.

**Solutions**:

```bash
# Verify the URL exists
curl -I "https://en.wikipedia.org/wiki/Page_Name"

# Try search instead of direct URL
wikibee "Page Name" instead of URL

# Check for redirects or moved pages
wikibee "Alternative Page Name"
```

## Network and Performance Issues

### Connection Timeouts

**Problem**: "Connection timeout" or "Network error"

**Causes**:
- Slow internet connection
- Large Wikipedia articles
- Server overload
- Firewall restrictions

**Solutions**:

```bash
# Increase timeout
wikibee "Large Article" --timeout 30

# Add retries
wikibee "Article" --timeout 30 --retries 5

# Try lead section only (faster)
wikibee "Article" --lead-only

# Test connectivity
ping wikipedia.org
curl -I https://en.wikipedia.org/api/rest_v1/
```

### Slow Performance

**Problem**: wikibee takes too long to process articles.

**Solutions**:

```bash
# Use lead-only for faster processing
wikibee "Topic" --lead-only

# Skip interactive selection
wikibee "Topic" --yolo

# Process smaller articles first
wikibee "Short Topic" --timeout 15

# Check network speed
wikibee "Test" --verbose  # Shows timing information
```

### SSL/TLS Errors

**Problem**: SSL certificate verification errors.

**Solutions**:

```bash
# Update certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Update certificates (Linux)
sudo apt-get update && sudo apt-get install ca-certificates

# Verify Python SSL
python -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

## File and Output Issues

### Permission Denied Writing Files

**Problem**: Can't write to output directory.

**Solutions**:

```bash
# Check directory permissions
ls -la output/

# Create directory with proper permissions
mkdir -p ~/wikibee_output
wikibee "Topic" --output ~/wikibee_output/

# Use current directory
wikibee "Topic"  # Saves to current directory

# Fix permissions
chmod 755 output_directory/
```

### File Already Exists

**Problem**: Files being overwritten unintentionally.

**Solutions**:

```bash
# Use custom filenames
wikibee "Topic" --filename topic_v2

# Check before running
ls topic.md && echo "File exists!" || wikibee "Topic"

# Use dated filenames in scripts
DATE=$(date +%Y%m%d)
wikibee "Topic" --filename "topic_$DATE"
```

### Encoding Issues

**Problem**: Strange characters in output files.

**Solutions**:

```bash
# Check file encoding
file output.md
head -n 5 output.md

# Verify locale settings
locale

# Set UTF-8 encoding
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

## TTS and Audio Issues

### TTS Server Connection Failed

**Problem**: Can't connect to TTS server for audio generation.

**Solutions**:

```bash
# Check if TTS server is running
curl http://localhost:8880/health

# Start TTS server (if you have one installed)
# This depends on your TTS setup

# Use TTS text without audio generation
wikibee "Topic" --tts  # Skip --audio flag

# Configure TTS server URL
export WIKIBEE_TTS_SERVER="http://your-server:port"
```

### Audio Generation Fails

**Problem**: TTS text created but audio generation fails.

**Solutions**:

```bash
# Check TTS server logs
# (Server-specific)

# Try shorter articles
wikibee "Short Topic" --lead-only --audio

# Test TTS server directly
curl -X POST http://localhost:8880/tts -d '{"text": "test"}'

# Use different voice
wikibee "Topic" --audio --tts-voice "alternative_voice"
```

### Poor TTS Quality

**Problem**: Generated text doesn't work well with TTS.

**Solutions**:

```bash
# Use custom heading prefix
wikibee "Topic" --tts --heading-prefix "Section:"

# Install inflect for number conversion
pip install inflect
wikibee "Topic" --tts  # Numbers will be converted to words

# Try lead-only for cleaner content
wikibee "Topic" --lead-only --tts
```

## Advanced Troubleshooting

### Debug Mode

Enable verbose output to diagnose issues:

```bash
wikibee "Topic" --verbose
```

This shows:
- Network request details
- Processing steps
- Timing information
- Error details

### Test Installation

Verify wikibee is working correctly:

```bash
# Basic functionality test
wikibee "Python programming language" --lead-only --no-save --verbose

# Network test
wikibee "Test" --timeout 5 --no-save

# File system test
wikibee "Test" --output /tmp/ --filename test_output
```

### Check Dependencies

Verify required packages are installed:

```bash
# Python packages
python -c "import requests, typer, rich; print('Dependencies OK')"

# Check versions
wikibee --version
python --version
pip list | grep -E "(requests|typer|rich)"
```

### System Information

Gather system info for bug reports:

```bash
# System details
uname -a
python --version
pip list | grep wikibee

# Network test
curl -I https://en.wikipedia.org/

# Disk space
df -h .

# Permissions test
touch test_file && rm test_file && echo "Write permissions OK"
```

## Common Error Messages

### "ModuleNotFoundError: No module named 'wikibee'"

**Cause**: wikibee not installed or not in Python path.

**Solution**:
```bash
pip install wikibee
# or
pipx install wikibee
```

### "requests.exceptions.ConnectTimeout"

**Cause**: Network timeout or connectivity issues.

**Solution**:
```bash
wikibee "Topic" --timeout 30 --retries 3
```

### "json.decoder.JSONDecodeError"

**Cause**: Invalid response from Wikipedia API.

**Solution**:
```bash
# Try again (temporary API issue)
wikibee "Topic" --retries 3

# Try different search term
wikibee "Alternative Topic"
```

### "UnicodeEncodeError"

**Cause**: Character encoding issues.

**Solution**:
```bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
wikibee "Topic"
```

## Getting Help

### Documentation Resources

- **[Quick Start](../quickstart.md)** - Basic usage
- **[CLI Reference](cli-reference.md)** - Complete command documentation
- **[API Reference](api-reference.md)** - Python API documentation

### Community Support

- **GitHub Issues**: [Report bugs](https://github.com/patrickdeanbrown/wikibee/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/patrickdeanbrown/wikibee/discussions)
- **Documentation**: Check all docs in the `docs/` directory

### Bug Reports

When reporting bugs, include:

1. **Command used**: Full wikibee command
2. **Error message**: Complete error output
3. **Environment**: OS, Python version, wikibee version
4. **Expected vs actual behavior**
5. **Steps to reproduce**

**Example bug report**:
```
Command: wikibee "Machine Learning" --tts --output research/
Error: UnicodeEncodeError: 'ascii' codec can't encode character...
Environment: Ubuntu 20.04, Python 3.8.10, wikibee 0.1.0
Expected: Should create TTS file
Actual: Crashes with encoding error
```

### Feature Requests

For new features:
1. Describe the use case
2. Explain the benefit
3. Provide examples of how it would work
4. Consider backward compatibility

---

**Navigation**: [Documentation Home](../README.md) | [CLI Reference](cli-reference.md) | [API Reference](api-reference.md) | [Quick Start](../quickstart.md)
