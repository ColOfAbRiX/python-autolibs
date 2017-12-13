# autolibs

## Python Automation Library

Utilities for a structure automation project including tools to work with Ansible, Terraform and Packer.

### Scripts

The package installs the following binaries:

 - **deploy**: wrapper to run Ansible deployments.
 - **vault**: wrapper to run ansible-vault.
 - **inventory**: custom dynamic inventory script to use YAML.
 - **inventory-aws**: custom inventory script to fetch information from AWS.
 - **packit**: utility script to provide Packer with build information

### Autocompletion

The package installs autocompletion for:

 - deploy
 - vault

### GIT hooks

The package installs system wide GIT hooks to perform checks on the repository.

## Requirements

The package requires the following additional python packages:

- **cfutils**
- **configparser2**
- **ansible** from version 2.0.0 up to version 2.3.x

To work properly, the autocompletion scripts need to be loaded at session startup, usually adding:

```BASH
#!/bin/bash
source "$(which support-deploy)"
source "$(which support-vault)"
```

to the `~/.bashrc` file in the home directory or to a `.sh` file inside `/etc/profile.d` for a system wide configuration.

## Credits

Fabrizio Colonna <colofabrix@tin.it>