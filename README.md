# Git Anonymize

Given a git repository produce a new repository with anonymized commits.

Intention behind this project is to provide convenient and automated way
for **copy-left (GPL) compliance** while maintaining confidentiality
of contributors identities in public mirror of repository.

Contributors have option to opt-in for public attribution by
opting-out from the anonymization using toml file.

## Configuring Public Contributors

You can create file `public-contributors.toml` which looks similarly to following:

```toml
[tester]
name = "Tester"
email = "tester@ictunion.cz"

[very_public_person]
name = [ "ME", "My Other Name" ]
email = [ "you-all-know@me.com", "other-email@somewhere.here" ]
```

Committers listed in this file will be assigned as authors of their commits even
in anonymized repository.

Both values can be either string or list of strings for cases where single person
is using multiple git configurations.

## Using The Project

Easiest way to install this tool is via [nix](nixos.org/).
At the moment there is no pip installation or similar.

If you have [flakes](https://nixos.wiki/wiki/Flakes) experimental feature enabled
you can just run this without explicitly installing the script on machine:

```
nix run github:ictunion/git-anonymize -- .
```

If you use don't want to use flake you can simply build or install
derivation using `release.nix`

```
nix-build release.nix
```

If you don't want to use nix at all use pip or your package manager of choice
to install following python3 dependencies:

- [git-filter-repo](https://github.com/newren/git-filter-repo)
- [tomli](https://github.com/hukkin/tomli)

### Options

Utility is also configurable by command line argument options.
See help for more info:

```
$ git-anonymize -h
usage: git-anonymize [-h] [-c CONFIG] [-o OUTPUT] [-n NAME] [-e EMAIL]
                     repository

Anonymize git history

positional arguments:
  repository            path to git repository to alter

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to configuration toml file
  -o OUTPUT, --output OUTPUT
                        path to location where altered repository should be created
  -n NAME, --name NAME  name to use instead in commits
  -e EMAIL, --email EMAIL
                        email to use instead in commits

            Developed by volunteers from `Odborová organizace pracujících v ICT`.
            The sectorial union of workers in IT & communications.
            See: http://ictunion.cz

```

## Installing in CI

This project is primary meant to be used in CI.
Current recommended method is to use nix, for other options see [Using Project](#using-the-project).

This is example **GitHub Action** workflow configuration:

```yaml
name: "Publish Source"

on:
  push:

jobs:
  publish-code:
    # Run this action only from private repository
    if: ${{ github.event.repository.name }} == 'my-private-repository'
    runs-on: ubuntu-latest
    steps:
      - name: Clone repository
        uses: actions/checkout@v3
        with:
          # Fetch whole history
          fetch-depth: 0

      # See documentation for this step for more info
      - name: Install SSH key
        uses: shimataro/ssh-key-action@v2
        with:
          key: ${{ secrets.GIT_SSH_KEY }}
          known_hosts: ${{ secrets.KNOWN_HOSTS }}
          if_key_exists: fail

      - name: Install nix
        uses: cachix/install-nix-action@v18

      - name: Create anonymized repo
        run: nix run github:ictunion/git-anonymize -- . -o /tmp/anonymized

      - name: Publish anonymized repository
        working-directory: /tmp/anonymized
        run: |
          git checkout ${{ github.ref_name }}
          git remote add origin {your-public-remote-repository}
          git push --force origin ${{ github.ref_name }}
```

## License

This project is released under [MIT License](LICENSE).
