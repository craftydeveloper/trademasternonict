# Contributing to TradePro

Thank you for your interest in contributing to TradePro! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
git clone https://github.com/yourusername/tradepro-bot.git
cd tradepro-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### JavaScript Code
- Use consistent indentation (2 spaces)
- Prefer `const` and `let` over `var`
- Use descriptive variable names
- Add comments for complex logic

### HTML/CSS
- Use semantic HTML elements
- Follow Bootstrap conventions
- Maintain responsive design principles
- Keep CSS organized and commented

## Testing

### Before Submitting
- Test all new features manually
- Verify existing functionality still works
- Check for console errors
- Test on mobile devices
- Validate with different account balances

### Test Cases to Cover
- Signal generation accuracy
- Risk management calculations
- Telegram alert functionality
- Database operations
- API error handling

## Pull Request Process

1. **Create a descriptive title**
   - Use format: `feat: add new feature` or `fix: resolve issue`

2. **Provide detailed description**
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Any breaking changes

3. **Update documentation**
   - Update README.md if needed
   - Add/update comments in code
   - Update SETUP.md for configuration changes

4. **Follow the checklist**
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Changes tested thoroughly
   - [ ] Documentation updated
   - [ ] No breaking changes (or clearly marked)

## Types of Contributions

### Bug Fixes
- Fix calculation errors
- Resolve API connectivity issues
- Correct UI/UX problems
- Database query optimizations

### New Features
- Additional technical indicators
- New exchange integrations
- Enhanced alert systems
- Improved risk management

### Documentation
- Code comments and docstrings
- Setup and configuration guides
- API documentation
- User tutorials

### Performance Improvements
- Optimize database queries
- Reduce API call frequency
- Improve frontend loading times
- Memory usage optimizations

## Reporting Issues

When reporting bugs or requesting features:

1. **Use descriptive titles**
2. **Provide reproduction steps**
3. **Include relevant logs**
4. **Specify environment details**
5. **Add screenshots if applicable**

### Bug Report Template
```
**Bug Description**
Clear description of what's wrong

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10, macOS, Linux]
- Python version: [e.g., 3.11]
- Browser: [e.g., Chrome 91]

**Additional Context**
Logs, screenshots, etc.
```

## Feature Requests

Before requesting a feature:
1. Check if it already exists
2. Search existing issues
3. Consider if it fits the project scope
4. Think about implementation complexity

### Feature Request Template
```
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other ways to achieve the same goal

**Additional Context**
Mockups, examples, etc.
```

## Code Review Guidelines

### For Contributors
- Respond to feedback promptly
- Be open to suggestions
- Explain your design decisions
- Update based on review comments

### For Reviewers
- Be constructive and helpful
- Focus on code quality and maintainability
- Check for security implications
- Verify testing coverage

## Security

### Reporting Security Issues
- Email security issues privately
- Do not create public issues for vulnerabilities
- Allow time for fixes before disclosure

### Security Considerations
- Never commit API keys or secrets
- Validate all user inputs
- Use secure communication protocols
- Implement proper error handling

## Community Guidelines

### Be Respectful
- Use welcoming and inclusive language
- Respect different viewpoints
- Provide constructive feedback
- Help others learn and grow

### Stay Focused
- Keep discussions on-topic
- Use appropriate channels for different types of communication
- Avoid bikeshedding on minor details

## Getting Help

If you need help contributing:
1. Check existing documentation
2. Search previous issues and PRs
3. Ask questions in GitHub discussions
4. Join the community Telegram group

## Recognition

Contributors will be:
- Listed in the project contributors
- Mentioned in release notes for significant contributions
- Invited to join the core team for outstanding work

Thank you for helping make TradePro better!