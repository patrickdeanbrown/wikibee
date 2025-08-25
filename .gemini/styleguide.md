# Python Style Guide for Wikibee

## Naming Conventions

### Variables and Functions
- **Variables**: Use snake_case: `search_term`, `article_text`, `timeout_value`
- **Functions**: Use snake_case with descriptive verbs: `extract_wikipedia_text()`, `sanitize_filename()`, `normalize_for_tts()`
- **Private functions**: Prefix with underscore: `_handle_search()`, `_make_session()`
- **Constants**: Use UPPER_CASE: `INFLECT_AVAILABLE`, `MAX_SEARCH_RESULTS`

### Classes and Exceptions
- **Classes**: Use PascalCase: `WikiClient`, `TTSNormalizer`, `TTSOpenAIClient`
- **Exceptions**: End with "Error": `NetworkError`, `APIError`, `TTSClientError`
- **Private methods**: Prefix with underscore: `_normalize_royal_names()`, `_retry_request()`

## Code Standards

### Type Hints
- **Required**: All function parameters and return values must have type hints
- **Optional types**: Use `Optional[Type]` or `Type | None` for nullable values
- **Complex types**: Import from `typing` module when needed
```python
from typing import Optional, Dict, List, Tuple

def extract_wikipedia_text(
    article_url: str, 
    timeout: int = 30
) -> Optional[str]:
    """Extract text from Wikipedia article."""
```

### Docstrings
- **Style**: Use Google docstring format
- **Required**: All public functions, classes, and modules
- **Content**: Brief description, parameters, return values, exceptions
```python
def sanitize_filename(name: str, max_len: int = 100) -> str:
    """Sanitize a string to be safe for use as a filename.
    
    Args:
        name: The original filename string
        max_len: Maximum allowed filename length
        
    Returns:
        A sanitized filename string safe for filesystem use
        
    Raises:
        ValueError: If name is empty after sanitization
    """
```

### Error Handling
- **Specific exceptions**: Use specific exception types, never bare `except:`
- **Context**: Include meaningful error messages with context
- **Hierarchy**: All custom exceptions inherit from `RuntimeError`
- **Logging**: Use structured logging for debugging information
```python
try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
except requests.exceptions.Timeout:
    raise NetworkError(f"Request timed out after {timeout}s: {url}")
except requests.exceptions.RequestException as e:
    raise NetworkError(f"Request failed: {e}")
```

### Code Organization
- **Imports**: Group in order: standard library, third-party, local imports
- **Line length**: Maximum 88 characters (strictly enforced by ruff)
- **Blank lines**: Two blank lines between classes, one between methods
- **String formatting**: Prefer f-strings over .format() or % formatting

## Wikipedia-Specific Patterns

### API Client Usage
- **Session management**: Always use `WikiClient` class with session pooling
- **Retry logic**: Implement exponential backoff for transient failures
- **Rate limiting**: Respect Wikipedia API guidelines and rate limits
- **User agent**: Always include descriptive user agent string

```python
client = WikiClient()
try:
    results = client.search_articles(search_term, limit=10, timeout=30)
except NetworkError as e:
    console.print(f"[red]Search failed: {e}[/]")
    return None
```

### URL Handling
- **Validation**: Always validate Wikipedia URLs before processing
- **Normalization**: Handle both desktop and mobile Wikipedia URLs
- **Encoding**: Properly decode URL-encoded article titles
```python
def is_wikipedia_url(url: str) -> bool:
    """Check if URL is a valid Wikipedia article URL."""
    parsed = urlparse(url.lower())
    return (
        parsed.netloc.endswith('.wikipedia.org') and
        '/wiki/' in parsed.path and
        ':' not in parsed.path.split('/wiki/')[-1]
    )
```

## TTS-Specific Guidelines

### Text Normalization
- **Pronunciation**: Focus on improving TTS pronunciation, not readability
- **Patterns**: Use regex patterns with clear documentation
- **Testing**: Test normalization rules with actual TTS output when possible
- **Phases**: Implement high-impact patterns first, then refinements

```python
def _normalize_royal_names(self, text: str) -> str:
    """Convert royal names to more natural TTS pronunciation.
    
    Examples: 'Henry VIII' → 'Henry the Eighth'
    """
    # Implementation with clear pattern documentation
```

### Audio Processing
- **Formats**: Support common audio formats (MP3, WAV, FLAC)
- **Quality**: Use appropriate bitrate and sample rate for voice content
- **Error handling**: Gracefully handle TTS server unavailability
- **Configuration**: Make TTS settings configurable via CLI arguments

## CLI Design Standards

### User Interface
- **Colors**: Use Rich library color codes consistently
  - `[red]` for errors and critical issues
  - `[yellow]` for warnings and cautions
  - `[green]` for success messages and confirmations
  - `[cyan]` for informational messages and progress
- **Menus**: Use numbered selection (1-10) for cross-platform compatibility
- **Progress**: Show clear progress indicators for long operations
- **Feedback**: Provide immediate feedback for user actions

### Argument Processing
- **Typer**: Use Typer framework for CLI argument parsing
- **Validation**: Validate arguments early with clear error messages
- **Defaults**: Provide sensible defaults for all optional arguments
- **Help**: Include descriptive help text for all commands and options

```python
@app.command()
def main(
    article: str = typer.Argument(..., help="Wikipedia article URL or search term"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
    yolo: bool = typer.Option(False, "--yolo", "-y", help="Auto-select first search result"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Extract and process Wikipedia articles for TTS."""
```

## Testing Standards

### Test Organization
- **File naming**: Match module names: `test_cli.py`, `test_client.py`
- **Function naming**: Use descriptive test names: `test_search_returns_multiple_results()`
- **Grouping**: Group related tests in classes when appropriate
- **Fixtures**: Use pytest fixtures for common test setup

### Mocking Patterns
- **External APIs**: Always mock Wikipedia API calls using `requests-mock`
- **File system**: Mock file operations for unit tests
- **Network**: Mock all network operations to ensure tests are deterministic
```python
@requests_mock.Mocker()
def test_search_articles_success(m):
    m.get(
        'https://en.wikipedia.org/api/rest_v1/page/search',
        json={'pages': [{'title': 'Test Article', 'extract': 'Test content'}]}
    )
    client = WikiClient()
    results = client.search_articles('test')
    assert len(results) == 1
```

### Coverage Requirements
- **Minimum**: 80% line coverage for all modules
- **Error paths**: Test all exception handling paths
- **Edge cases**: Include tests for boundary conditions and edge cases
- **Integration**: Test CLI commands end-to-end with mocked dependencies

## Performance Considerations

### Efficient Processing
- **Streaming**: Use streaming for large article processing when possible
- **Caching**: Implement appropriate caching for repeated API calls
- **Memory**: Monitor memory usage for large articles and long-running operations
- **Concurrency**: Consider async/await for I/O-bound operations

### Resource Management
- **Connections**: Use session pooling for HTTP requests
- **Files**: Always use context managers for file operations
- **Cleanup**: Ensure proper cleanup of temporary resources
```python
def write_text_file(content: str, filepath: Path) -> None:
    """Write content to file with proper resource management."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
```

## Security Guidelines

### Input Validation
- **URL validation**: Validate all URLs before making requests
- **Filename sanitization**: Always sanitize user-provided filenames
- **Path traversal**: Prevent directory traversal attacks in file operations
- **Input limits**: Enforce reasonable limits on input sizes

### Dependencies
- **Pinning**: Pin dependency versions in production deployments
- **Security updates**: Regularly update dependencies for security fixes
- **Minimal dependencies**: Keep dependency count minimal and well-justified
- **Audit**: Regularly audit dependencies for known vulnerabilities

## Documentation Requirements

### Code Documentation
- **Module docstrings**: Every module needs a descriptive docstring
- **API documentation**: Document all public functions and classes
- **Examples**: Include usage examples for complex functions
- **Changelog**: Update CHANGELOG.md for user-facing changes

### User Documentation
- **README**: Keep README current with latest features and installation
- **CLI help**: Ensure CLI help text is comprehensive and accurate
- **Error messages**: Provide actionable error messages with troubleshooting hints
- **Examples**: Include real-world usage examples in documentation
