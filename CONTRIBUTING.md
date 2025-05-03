# Contributing

Thank you for thinking of making a contribution!

## Pull Request Process

### 0. Before you begin

If this is your first time contributing to an opensource project, [start by reading this guide](https://opensource.guide/how-to-contribute/#how-to-submit-a-contribution).

Please note that any contribution you make will be licensed under [the project's licence](https://github.com/mdevolde/aztec_tool/blob/master/LICENSE).

### 1. Find something to work on

The best contributions are those that try to resolve the [issues](https://github.com/mdevolde/aztec_tool/issues).

If there are no open issues, or if they are not actionable or blocked, there is a list of things to do in the [TODO file](https://github.com/mdevolde/aztec_tool/blob/master/TODO.md).

### 2. Fork the repository and make your changes

If you want to contribute, you first need to fork the repo (and preferably create a branch with a name that says something about the changes you're going to make).

To start developing, you can install all the necessary packages in your python environment with this command (optional dependencies will be installed):
```shell
pip install -e .[dev]
```

When pushing commits, please use the project naming conventions, which are available in [this guide](https://www.conventionalcommits.org/en/v1.0.0/).
If you haven't respected these conventions, do a rebase before making the pull request.

The documentation style used in the project is **NumPy**. Please, if you add or modify documentation, use this style. If you need more information or examples, look in the code, or in [this guide](https://numpydoc.readthedocs.io/en/latest/format.html).

Before creating your pull request, when you have made all your commits, you need to run this:
```shell
# Run linters (maybe you will have to fix some issues)
ruff check aztec_tool tests

# Format code
black aztec_tool tests

# Tests
pytest
```

Please do not manually bump the version number in [pyproject.toml](./pyproject.toml), this will be handled by the maintainers during release.

### 3. Checklist

Before pushing and creating your pull request, you should make sure you've done the following:

- Updated any relevant tests.
- Updated any relevant documentation. This includes docstrings and [README](./README.md) file.
- Added comments to your code where necessary (especially if the code is not self-explanatory).
- Formatted your code, run the linters and tests.

### 4. Create your pull request

When you create your pull request, make sure you give it a name that clearly indicates what you have modified in the library.

- Why the pull request was made
- Summary of changes
- If it resolves one or more issues, name them
- If you have used external resources, mention them

### 5. Code review

Your code will be reviewed by a maintainer.

If you're not familiar with code review start by reading [this guide](https://google.github.io/eng-practices/review/).

## Contacting the Maintainers

As far as possible, communicate on github, in discussions on issues or pull requests.
If you really need to use another channel (need to contact privately e.g.), you can contact the email addresses in [pyproject.toml](./pyproject.toml).

---

Thank you for helping make **aztec_tool** better for everyone!
