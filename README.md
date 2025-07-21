# ANT

## 🧾 Overview

The **ANT-Tool** is a command-line application for automated testing and evaluation of `nftables` scripts. It reads YAML-based configurations to set up a virtual test environment, deploys firewall rules, executes connectivity tests, and produces evaluation reports.

This tool is intended for instructors and students working on network security exercises involving `nftables`.


## ⚙️ Installation

```bash
git clone https://github.com/Helmigreg/ant
cd ant
pip install -r ant_backend/requirements
pip install .
```

### Dependencies

- [Python 3.8+](https://www.python.org "Python 3.8+")
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Ansible Runner](https://pypi.org/project/ansible-runner/)
- [NFTables](https://git.netfilter.org/nftables/tree/py/src/nftables.py)
- [PyYAML](pypi.org/project/PyYAML/)
- [sshpass](https://sourceforge.net/projects/sshpass/)
- Access to testing VMs

### Requirements

Install required Python packages:
```bash
pip install -r requirements.txt
```
or
```bash
pip install ansible_runner pyyaml git+https://salsa.debian.org/pkg-netfilter-team/pkg-nftables@4dd66909609214e54230572ea717edb4984bb46a#subdirectory=py
```


## 🚀 Usage

### Command Syntax
```bash
python3 ant_backend/main.py -i infra_file.yml -t tests_file.yml -c template_mapping.yml [-r report.json] [-p protocol.json] [-d output_dir] [-v]
```

**Use our help page [-h] for further information regarding the usage.**

### Parameters

| Flag         | Description                                                        |
|--------------|--------------------------------------------------------------------|
| `-i`  `--infrafile`  | Path to the infrastructure config file (YAML, required)     |
| `-t`  `--testcases`  | Path to the test definitions file (YAML, required)          |
| `-c`  `--config`     | Template mapping file (default: `template_mapping.yml`)             |
| `-r`  `--report`     | Output report filename (JSON format)                       |
| `-p`  `--protocol`   | Optional output file for internal protocol logging         |
| `-d`  `--dir`        | Directory to store results (default: `.`)                  |
| `-v`  `--verbose`    | Enable verbose mode for debugging                          |


## 🏗 File Descriptions

**For more information on the YAML-files, please check out our `how-to-YAML` document.**

### `test_infra.yml`
Defines the test environment:
- **Networks**: Names, IP ranges (IPv4/IPv6)
- **Machines**: IPs, credentials, optional `NFTable` script path

### `tests.yml`
Defines the test cases:
- `Name`, `Source`, `Destination`, `Proto`, `D_port`
- Optional: `S_port`, `points`, `allow`, `special`

### `template_mapping.yml`
Maps protocol fields (`tcp`, `udp`, `icmp`) to variable names used in templates.




## 📊 Output

The tool outputs:
- A **report file** containing all test results
- Optional **protocol/debug information**
- Exit codes: `0` = success, `1` = error




## 🧯 Troubleshooting

- **Missing file**: Ensure all file paths are correct
- **Invalid YAML**: Check for correct indentation and formatting
- **Unreachable VMs**: Validate your network setup and SSH access
- **nftables syntax error**: Tool validates each script before testing


## 📘 Glossary

- **nftables**: Linux firewall framework
- **VM**: Virtual Machine
- **Testcase**: A defined connection to be tested
- **NFTable**: Firewall rule set to be evaluated
