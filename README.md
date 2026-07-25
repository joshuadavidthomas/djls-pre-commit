# django-language-server-pre-commit

[pre-commit](https://pre-commit.com/) and [prek](https://prek.j178.dev/) hooks for [django-language-server](https://github.com/joshuadavidthomas/django-language-server).

## Usage

Add the hook to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/joshuadavidthomas/django-language-server-pre-commit
    rev: v6.0.3
    hooks:
      - id: djls-check
```

The hook installs the matching `django-language-server` release in its own environment and runs `djls check` on staged `.html`, `.htm`, and `.djhtml` files. Your Django project still needs a supported Python environment that django-language-server can discover.

Pass any [`djls check` options](https://djls.joshthomas.dev/cli/#djls-check) through `args`:

```yaml
hooks:
  - id: djls-check
    args: [--select, "S100,S117", --color, never]
```

Hook tags match django-language-server releases. Dependabot can keep the revision current:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pre-commit
    directory: /
    schedule:
      interval: weekly
```

## License

Licensed under the Apache License, Version 2.0. See [`LICENSE`](LICENSE).
