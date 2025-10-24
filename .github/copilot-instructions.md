# Copilot Instructions

## System Environment
- **Operating System**: Ubuntu Linux 5.15.148-tegra (Jetson Orin Nano Super)
- **Python Version**: Python 3.11+ (managed via pyenv)
- **Python Environment Manager**: pyenv
- **Shell**: zsh

## Code Style Guidelines

### General Principles
- Write clean, modular, and maintainable code
- Follow Python PEP 8 style guidelines
- Use minimal comments - only when necessary for complex logic or business rules
- Prioritize self-documenting code with clear variable and function names
- Implement proper error handling and logging where appropriate
- Use English only for code, comments, and documentation

### Code Structure
- Use modular design patterns
- Separate concerns into distinct modules and classes
- Follow SOLID principles
- Implement dependency injection where beneficial
- Use type hints for better code documentation and IDE support

### Best Practices
- Prefer composition over inheritance
- Use context managers for resource management
- Implement proper exception handling
- Follow the DRY (Don't Repeat Yourself) principle
- Use meaningful names for variables, functions, and classes
- Keep functions small and focused on a single responsibility

## Code Review Process

### Pre-commit Checks
Before finalizing any code implementation:

1. **Redundancy Review**: Scan for duplicate code blocks or similar functionality
2. **Code Clarity**: Ensure code is self-explanatory and logical flow is clear
3. **Refactoring**: Identify opportunities to consolidate similar functions or classes
4. **Performance**: Review for obvious performance improvements
5. **Security**: Check for potential security vulnerabilities

### Code Quality Checklist
- [ ] No duplicate code or redundant implementations
- [ ] Functions have single responsibility
- [ ] Clear separation of concerns
- [ ] Proper error handling
- [ ] Type hints are used appropriately
- [ ] Code is self-documenting with minimal comments

## Testing Requirements

### Test Framework
- **Primary Framework**: pytest
- **Test Directory**: `tests/`
- **Test Structure**: Mirror the source code structure in the tests directory

### Testing Standards
- Write comprehensive unit tests for all new functionality
- Achieve high test coverage (aim for >90%)
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies appropriately
- Include both positive and negative test cases
- Test edge cases and error conditions

### Test Organization
```
tests/
├── test_module_name.py
├── conftest.py
├── fixtures/
└── integration/
```

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>_<expected_outcome>`
- Test classes: `Test<ClassName>`

## Project Structure Expectations
- Follow standard Python project layout
- Use proper package initialization with `__init__.py`
- Maintain clean import statements
- Organize related functionality into appropriate modules
- Keep configuration separate from business logic

## Dependencies Management
- Use `pyproject.toml` for project configuration and dependencies
- Pin dependency versions for production stability
- Keep dependencies minimal and well-justified
- Regularly update dependencies for security patches

## Documentation
- Write clear docstrings for public APIs
- Use type hints consistently
- Maintain README.md with setup and usage instructions
- Document complex algorithms or business logic when necessary
- Don't create documentation files if is not explicitly required

## Error Handling
- Use specific exception types rather than generic Exception
- Provide meaningful error messages
- Implement proper logging at appropriate levels
- Handle edge cases gracefully
- Validate input parameters when necessary

Remember: Code should be written once and read many times. Prioritize clarity and maintainability over cleverness.