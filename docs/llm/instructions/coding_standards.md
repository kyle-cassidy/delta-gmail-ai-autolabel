# Coding Standards

## Python Guidelines
1. Type Hints
   - All function parameters and return types
   - Use Optional[] for nullable types
   - Complex types in type aliases

2. Documentation
   - Docstrings for all public functions
   - Example usage in docstrings
   - Clear parameter descriptions
   - Comments are encouraged. Non-coders must be able to understand the code.

3. Error Handling
   - Custom exception classes
   - Meaningful error messages
   - Proper exception hierarchy

4. Testing
   - Unit tests for all functions
   - Integration tests for flows
   - 80%+ coverage target

## Project Structure
1. Service Layer Pattern
   - Business logic in services
   - Clean interface separation
   - Dependency injection

2. Configuration
   - Environment variables
   - Configuration objects
   - No hardcoded values

3. Logging
   - Structured logging
   - Appropriate log levels
   - Context preservation

## Security Practices
1. Data Handling
   - No sensitive data logging
   - Proper secret management
   - Data minimization

2. Authentication
   - OAuth best practices
   - Token refresh handling
   - Scope validation 