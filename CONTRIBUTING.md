# Contributing to TARS CLI

Thank you for your interest in contributing to TARS CLI! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, professional, and inclusive. We're all here to build great tools.

## How to Contribute

### Reporting Bugs

1. Check if the bug already exists in [Issues](https://github.com/orathore93-hue/tars-cli/issues)
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - TARS version (`tars version`)
   - Kubernetes version
   - Environment details

### Suggesting Features

1. Check existing feature requests
2. Create an issue with:
   - Clear use case
   - Expected behavior
   - Why it's useful

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation
   - Keep commits atomic and well-described

4. **Test your changes**
   ```bash
   pytest tests/
   black src/tars
   flake8 src/tars
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Development Setup

```bash
# Clone repository
git clone https://github.com/orathore93-hue/tars-cli.git
cd tars-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install pytest black flake8 mypy

# Run tests
pytest tests/

# Format code
black src/tars

# Lint
flake8 src/tars
```

## Code Style

- **Python**: Follow PEP 8
- **Line length**: 127 characters max
- **Formatting**: Use `black`
- **Type hints**: Use where appropriate
- **Docstrings**: Required for public functions

## Testing

- Write tests for new features
- Maintain or improve code coverage
- Test with multiple Python versions (3.9+)
- Test with different Kubernetes versions

## Documentation

- Update README.md for user-facing changes
- Update COMMANDS.md for new commands
- Update CHANGELOG.md
- Add docstrings to code
- Update SECURITY.md for security changes

## Security

- Never commit secrets or credentials
- Follow security best practices
- Report security issues privately to: orathore93@gmail.com
- See SECURITY.md for details

## Commit Message Guidelines

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

**Example:**
```
feat: Add support for multi-cluster operations

- Add multi-cluster command
- Support context switching
- Update documentation

Closes #123
```

## Review Process

1. Automated tests must pass
2. Code review by maintainer
3. Security scan must pass
4. Documentation must be updated
5. CHANGELOG.md must be updated

## Release Process

1. Update version in `src/tars/__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v4.x.x`
4. Push tag: `git push --tags`
5. GitHub Actions creates release automatically

## Questions?

- Open an issue for questions
- Email: orathore93@gmail.com
- Be patient, this is maintained by volunteers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to TARS CLI! 🚀
