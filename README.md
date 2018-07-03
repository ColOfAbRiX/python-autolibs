# autolibs

## Python Automation Library

Utilities and wrappers for Ansible, Terraform and Packer for improved efficiency and security.

The toolset defines some standards and a project structure that then is used to provide simplified tools to the user and it's targeted at command-line users. The main features are:

- Simplified command lines to run Ansible, just specify the target and the playbook
- Command line autocompletion for the tools that search on the Ansible code
- Powerful and clean YAML-based dynamic inventory
  - Support for plug-in inventories
  - Clean directory structure to manage different scenarios
  - Management of only one or multiple environments
  - Support for the two Ansible recommended [directory structures][1]
- Centralized configuration file for all the tools
- Security checks for sensitive files (git hooks, file system permissions)
- Using GIT on your project is the foundation of the tools

The package installs the following binaries:

- **deploy**: wrapper to run Ansible deployments.
- **vault**: wrapper to run ansible-vault, comes in 2 flavours (vault-host and vault-group).
- **inventory**: custom dynamic inventory script to use YAML.
- **inventory-aws**: custom inventory script to fetch information from AWS.
- **packit**: utility script to provide Packer with build information (work in progress)

The package installs autocompletion for:

- **deploy**
- **vault**

The package installs system wide GIT hooks to perform checks on the repository. The hooks have to be linked manually when desired.

- **commit-msg**
- **pre-commit**
- **pre-push**

[1]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#directory-layout

## Requirements

The package requires the following additional python packages (installed automatically by python):

- **ansible** from version 2.0.0 up to version 2.3.x
- **boto3**
- **colored**
- **configparser2**
- **GitPython**
- **mock**
- **pycrypto**
- **PyYAML**

## Installation

Install using PIP:

```
sudo pip install https://github.com/ColOfAbRiX/python-autolibs/archive/master.zip
```

The autocompletion scripts need to be loaded at session startup, usually adding:

```BASH
#!/bin/bash
source "$(which support-deploy)"
source "$(which support-vault)"
```

to the `~/.bashrc` file in the home directory or to a `.sh` file inside `/etc/profile.d` for a system wide configuration.

## Directory structure

## Configuration file

The tools use a configuration file in the GIT repository root named `.repoconfig`. This file contains a set of parameters to customize the project structure and the behaviour of the tools.

The example file can be found here [.repoconfig](repoconfig-example) and it contains descriptions of all the options together with their default values.

## Tools

### deploy

Wrapper for ansible-playbook and deployment management.

`deploy [-h] [--skip-signature] playbook target [filter] [ansible [ansible ...]]`

##### Positional arguments

- `playbook`: Name of the Ansible Playbook found anywhere in the playbooks directory.
- `target`: Target of the run. It can be a usual Ansible inventory or an executable file as dynamic inventory; if a relative path then it will be searched in various default locations.
- `filter`: An Ansible pattern that will be used to further filter the target hosts, it's equivalent to the Ansible -l option.
- `ansible`: These options will be passed, as they are, directly to Ansible.

##### Optional arguments

- `-h, --help`: Show this help message and exit
- `--skip-signature`: If present, it will skip the writing and updating of the deployment signature.

##### Other features

- automatic secret file
- environments management
- dynamic inventory use

##### Project directory structure

##### Configuration file

### vault-host, vault-group

`vault-host [-h] {create,decrypt,edit,encrypt,rekey,view} environment target [ansible [ansible ...]]`
`vault-group [-h] {create,decrypt,edit,encrypt,rekey,view} environment target [ansible [ansible ...]]`

##### Positional arguments

- `{create,decrypt,edit,encrypt,rekey,view}`: Vault action
- `environment`: The environment to target.
- `target` The group or host target.
- `ansible` These options will be passed directly to Ansible as they are.

##### Optional arguments

- `-h, --help`: Show this help message and exit

### inventory

### inventory-aws

## License

MIT

## Author Information

[Fabrizio Colonna](mailto:colofabrix@tin.it)
