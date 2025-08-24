# Contributing to wikibee

We welcome contributions to wikibee! This guide will help you get started with contributing to the project.

## Getting Started

### Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/your-username/wikibee.git
   cd wikibee
   ```

2. Set up your development environment:
   ```bash
   uv venv --python 3.12
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   pre-commit install
   ```

3. Verify your setup:
   ```bash
   pytest -q
   ruff check .
   wikibee --help
   ```

## Development Workflow

### Making Changes

1. Create a branch from main:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with appropriate tests
3. Run the test suite: `pytest -q`
4. Ensure code style compliance: `ruff check .`
5. Commit your changes with clear messages

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to new functions
- Include docstrings for public APIs
- Write tests for new functionality
- Keep line length under 88 characters

### Testing

Run tests before submitting:
```bash
pytest -q              # Quick test run
pytest -v              # Verbose output
pytest tests/specific/  # Test specific area
```

## Submitting Changes

### Pull Request Process

1. Push your branch to your fork
2. Create a pull request against the main branch
3. Describe your changes clearly in the PR description
4. Wait for review and address any feedback

### What Makes a Good PR

- Clear description of the problem and solution
- Appropriate test coverage
- Updated documentation if needed
- Follows existing code patterns
- Includes relevant issue references

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- Operating system and Python version
- wikibee version
- Steps to reproduce the issue
- Expected vs actual behavior
- Full error messages or stack traces

### Feature Requests

For new features:
- Describe the use case and benefit
- Provide examples of how it would work
- Consider backward compatibility
- Discuss implementation approach if you have ideas

### Documentation

Documentation improvements are always welcome:
- Fix typos and clarify confusing sections
- Add examples and use cases
- Improve API documentation
- Create tutorials for common workflows

## Code Review

### Review Criteria

We review pull requests for:
- Functionality and correctness
- Test coverage
- Code quality and maintainability
- Documentation completeness
- Backward compatibility

### Response Time

- Small changes: 1-2 days
- Medium changes: 3-5 days
- Large changes: 1-2 weeks

## Getting Help

- Check existing documentation in the docs/ directory
- Search existing issues before creating new ones
- Ask questions in GitHub issues or discussions
- Review the codebase for examples and patterns

## License

By contributing to wikibee, you agree that your contributions will be licensed under the MIT License.

Thank you for helping improve wikibee!