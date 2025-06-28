# Contributing to TikTok-Sayer

Thank you for your interest in contributing to TikTok-Sayer! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for TikTok-Sayer. Following these guidelines helps maintainers understand your report, reproduce the issue, and find related reports.

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as many details as possible.
- **Provide specific examples to demonstrate the steps**.
- **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
- **Explain which behavior you expected to see instead and why.**
- **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem.
- **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for TikTok-Sayer, including completely new features and minor improvements to existing functionality.

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
- **Provide specific examples to demonstrate the steps** or point out the part of TikTok-Sayer which the suggestion is related to.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
- **Explain why this enhancement would be useful** to most TikTok-Sayer users.

### Pull Requests

- Fill in the required template
- Do not include issue numbers in the PR title
- Include screenshots and animated GIFs in your pull request whenever possible
- Follow the Python styleguide
- Include tests when adding new features
- Update documentation when changing the API

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Python Styleguide

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/).

### Documentation Styleguide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation.
- Reference functions, classes, and modules in markdown using the appropriate syntax.

## Development Process

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Setting Up Development Environment

1. Clone your fork of the repository
2. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # if exists
   ```
3. Run the test script to ensure everything is set up correctly:
   ```bash
   python test_tiktok_sayer.py
   ```

## Testing

- Write tests for new features
- Run tests before submitting a pull request
- Ensure all tests pass

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* **bug** - Issues that are bugs
* **enhancement** - Issues that are feature requests
* **documentation** - Issues or pull requests related to documentation
* **good first issue** - Good for newcomers
* **help wanted** - Extra attention is needed
* **question** - Further information is requested

## Thank You!

Your contributions to open source, large or small, make projects like this possible. Thank you for taking the time to contribute.