# Contributing to Camera To Keyboard

Thank you for considering contributing to this project. There are 2 routes to contribute:

## Non-technical

You can contribute to the project by adding data to the training dataset. This will be
possible after a pipeline has been established.

## Technical

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.
Please note we have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

### Development environment setup

To set up a development environment, please follow these steps:

1. Clone the repo

   ```sh
   git clone https://github.com/mnvoh/cameratokeyboard
   ```

2. Install the dependencies:

   ```sh
   pip install -r requirements.txt
   pip install -r requirements.dev.txt
   ```

3. If you intend on using GPU for training or inference:
   - Install cuda drivers
   - Install a compatible version of torch

4. If anything goes wrong, or doesn't work feel free to reach out.

### Issues and feature requests

You've found a bug in the source code, a mistake in the documentation or maybe you'd like a new feature? You can help us by [submitting an issue on GitHub](https://github.com/mnvoh/cameratokeyboard/issues). Before you create an issue, make sure to search the issue archive -- your issue may have already been addressed!

Please try to create bug reports that are:

- _Reproducible._ Include steps to reproduce the problem.
- _Specific._ Include as much detail as possible: which version, what environment, etc.
- _Unique._ Do not duplicate existing opened issues.
- _Scoped to a Single Bug._ One bug per report.

**Even better: Submit a pull request with a fix or new feature!**

#### How to submit a Pull Request

1. Search our repository for open or closed
   [Pull Requests](https://github.com/mnvoh/cameratokeyboard/pulls)
   that relate to your submission. You don't want to duplicate effort.
2. Fork the project
3. Create your feature branch (`git checkout -b feat/amazing_feature`)
4. Commit your changes (`git commit -m 'feat: add amazing_feature'`) Camera To Keyboard uses [conventional commits](https://www.conventionalcommits.org), so please follow the specification in your commit messages.
5. Push to the branch (`git push origin feat/amazing_feature`)
6. [Open a Pull Request](https://github.com/mnvoh/cameratokeyboard/compare?expand=1)

#### Conventional Commits

Here's a quick guide on conventional commits:

Format

```
<type>[optional scope]: <description> [optional body] [optional footer(s)]
```

Components of a Conventional Commit Message:

- <type> (required): This is a single word that indicates the nature of the change introduced in the commit. Here are some common types:
   - feat: Introduces a new feature.
   - fix: Fixes a bug.
   - refactor: Refactors existing code without changing functionality.
   - docs: Adds or updates documentation.
   - style: Makes stylistic changes without affecting functionality (e.g., whitespace formatting).
   - test: Adds missing tests or updates existing tests.
   - build: Changes the build process or configuration.
   - ci: Changes the continuous integration configuration.
   - chore: Other miscellaneous changes that don't fall into the above categories (e.g., updating dependencies).
- [optional scope]: This can be used to provide additional context about the change, especially in larger projects. It's typically separated from the type with a colon (:). For example, "feat(auth): implement login functionality".
- <description> (required): This is a concise description of the change, ideally written in the imperative mood (e.g., "fix memory leak" or "update documentation for new feature").
- [optional body]: This section can be used to provide more detailed information about the change, such as the motivation behind it, breaking changes, or links to related issues.
- [optional footer(s)]: This section can be used to include additional information like:
   - BREAKING CHANGE: If the commit introduces a breaking change, you can use this keyword followed by a colon (:) and a description of the breaking change.
   - Closes #issueNumber: You can reference related issues closed by the commit using this format.