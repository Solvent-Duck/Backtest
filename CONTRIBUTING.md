# Contributing to Backtest

Thank you for your interest in contributing to Backtest! This document provides guidelines and instructions for contributing.

## Development Setup

Please see [docs/SETUP.md](docs/SETUP.md) for detailed setup instructions.

## Code Style

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use `black` for code formatting (when configured)
- Use descriptive variable and function names

### Frontend (TypeScript/React)

- Follow Next.js conventions
- Use TypeScript for all new code
- Use functional components with hooks
- Follow React best practices
- Use Tailwind CSS for styling

## Git Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests if applicable
4. Commit with clear, descriptive messages
5. Push and create a pull request

### Commit Message Format

```
type: short description

Longer description if needed
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add description of changes
4. Reference any related issues
5. Request review from maintainers

## Areas for Contribution

- Bug fixes
- New features (see roadmap)
- Documentation improvements
- Performance optimizations
- Test coverage
- UI/UX improvements

## Questions?

Open an issue or start a discussion for any questions about contributing.
