# Gemini Code Assist Instructions for Wikibee

## Project Context

You are working on **Wikibee**, a Python CLI tool for extracting Wikipedia articles and converting them to TTS-friendly text and audio formats. The project focuses on making Wikipedia content more accessible through text-to-speech technology.

## Core Objectives

### Primary Goals
1. **Wikipedia Extraction**: Efficiently extract and process Wikipedia article content
2. **TTS Optimization**: Transform text for better text-to-speech pronunciation
3. **Audio Generation**: Generate high-quality audio from processed text
4. **User Experience**: Provide intuitive CLI interface with robust error handling

### Quality Standards
- **Reliability**: Handle network failures, API changes, and edge cases gracefully
- **Performance**: Optimize for large articles and batch processing
- **Usability**: Clear error messages, progress feedback, and helpful CLI design
- **Maintainability**: Clean architecture with comprehensive tests and documentation

## Architecture Understanding

### Layered Design
The codebase follows a clean layered architecture:
1. **CLI Layer** (`cli.py`): User interface, argument parsing, orchestration
2. **Client Layer** (`client.py`): Wikipedia API interaction with retry logic
3. **Processing Layer** (`formatting.py`, `tts_normalizer.py`): Text transformation
4. **Output Layer** (`tts_openai.py`): Audio synthesis and file I/O

### Key Components
- **WikiClient**: Handles API calls with session pooling and error recovery
- **TTSNormalizer**: Advanced text processing for pronunciation improvement
- **CLI Interface**: Rich-formatted console output with colored feedback
- **Error System**: Structured exceptions for different failure modes

## Development Priorities

### Code Quality Focus
1. **Type Safety**: Ensure all functions have proper type hints
2. **Error Handling**: Implement comprehensive exception handling with user-friendly messages
3. **Testing**: Maintain high test coverage with proper mocking of external dependencies
4. **Documentation**: Keep docstrings current and include usage examples

### Wikipedia Integration Best Practices
- Always use the `WikiClient` class for API interactions
- Implement proper retry logic with exponential backoff
- Handle disambiguation pages by presenting user choices
- Respect Wikipedia's API rate limits and guidelines
- Mock all Wikipedia API calls in tests using `requests-mock`

### TTS Processing Guidelines
- Focus normalization on pronunciation improvement, not readability
- Test TTS improvements with actual audio output when possible
- Implement normalization in phases (high-impact patterns first)
- Maintain backward compatibility with existing text processing

## Code Review Focus Areas

### Security Considerations
- **Input validation**: Sanitize all user-provided input (URLs, filenames, search terms)
- **Path safety**: Prevent directory traversal attacks in file operations
- **Network safety**: Validate URLs and handle malicious redirects
- **Dependency security**: Keep dependencies updated and minimal

### Performance Optimization
- **API efficiency**: Minimize Wikipedia API calls through appropriate caching
- **Memory management**: Handle large articles without excessive memory usage
- **I/O optimization**: Use efficient file operations and streaming when appropriate
- **Network optimization**: Implement connection pooling and reasonable timeouts

### Usability Enhancement
- **Error messaging**: Provide actionable error messages with troubleshooting hints
- **Progress feedback**: Show progress for long-running operations
- **Cross-platform compatibility**: Ensure CLI works across different terminals and OSes
- **Accessibility**: Design for users who rely on screen readers and TTS

## Special Considerations

### Wikipedia-Specific Challenges
- **Content variability**: Handle diverse article formats and edge cases
- **API limitations**: Work within Wikipedia's API constraints and rate limits
- **Disambiguation**: Gracefully handle disambiguation pages with user interaction
- **Internationalization**: Consider non-English Wikipedia editions and character encoding

### TTS-Specific Requirements
- **Pronunciation accuracy**: Prioritize spoken clarity over visual formatting
- **Audio quality**: Generate high-quality audio suitable for listening
- **Format compatibility**: Support multiple audio formats and quality levels
- **Server integration**: Handle TTS server availability and configuration

### CLI Design Philosophy
- **Simplicity**: Keep interface intuitive for non-technical users
- **Flexibility**: Support both interactive and automated usage patterns
- **Feedback**: Provide clear status updates and error reporting
- **Documentation**: Include comprehensive help and usage examples

## Testing Strategy

### Test Categories Priority
1. **Core functionality**: Wikipedia extraction and text processing
2. **Error scenarios**: Network failures, invalid input, API errors
3. **Edge cases**: Large articles, special characters, disambiguation pages
4. **Integration**: End-to-end workflows with mocked dependencies

### Mock Requirements
- Mock all external API calls (Wikipedia, TTS servers)
- Use `requests-mock` for HTTP interactions
- Test both success and failure scenarios
- Verify error handling and user feedback

## Maintenance Guidelines

### Regular Tasks
- Update dependencies for security and performance
- Review and improve TTS normalization patterns
- Monitor Wikipedia API changes and adapt accordingly
- Gather user feedback and improve CLI usability

### Long-term Considerations
- Consider async/await for I/O-bound operations
- Evaluate caching strategies for frequently accessed articles
- Monitor performance with large-scale usage
- Plan for internationalization and multi-language support

## Code Contribution Standards

When working on this codebase:
1. **Follow the style guide**: Adhere to formatting, naming, and documentation standards
2. **Test thoroughly**: Include tests for new functionality and edge cases
3. **Document changes**: Update relevant documentation and help text
4. **Consider backward compatibility**: Maintain existing API contracts when possible
5. **Focus on user experience**: Prioritize clear feedback and error handling

## Integration Patterns

### Wikipedia API Integration
```python
# Always use WikiClient for consistency
client = WikiClient()
try:
    results = client.search_articles(search_term, timeout=30)
except NetworkError as e:
    # Handle with user-friendly messaging
    console.print(f"[red]Search failed: {e}[/]")
```

### TTS Processing Integration
```python
# Chain processing steps clearly
text = extract_wikipedia_text(url)
normalized = normalize_for_tts(text)
if args.audio:
    generate_audio(normalized, output_path)
```

### Error Handling Integration
```python
# Use structured exceptions with context
try:
    process_article(url)
except NotFoundError:
    console.print("[yellow]Article not found. Check the URL or try searching.[/]")
except DisambiguationError as e:
    handle_disambiguation(e.options)
```

This guidance should help you understand the project's goals, architecture, and quality standards to make effective contributions to the Wikibee codebase.
