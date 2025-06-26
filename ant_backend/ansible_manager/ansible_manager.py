"""Defines a management interface for ansible as used by ant_backend"""

import ipaddress
import shutil
import os
import yaml
import ansible_runner
from ant_backend import NetworkConfiguration, TestcaseConfiguration

class AnsibleManager(object):
    """
    A management Interface for ansible
    """

    def __init__(self, conf_path:str):
        self.inventory = {}
        with open(conf_path,'r',encoding='utf-8') as conf_file:
            self.protos:dict = yaml.safe_load(conf_file)

        for proto in self.protos.keys():
            self.inventory.setdefault(proto, {})
            self.inventory[proto].setdefault('hosts', {})

    def create_inventory(self, path:str, netconfig: NetworkConfiguration,
                         testconfig: TestcaseConfiguration):
        """
        Creates an ansible inventory based on the given network and testconfiguration
          at the location specified by path
        """
        for testcase in testconfig.testcases:
            machine = netconfig.machines[testcase.source]
            hostdict = {
                'ansible_host': machine.management_ip.exploded,
                'ansible_user': machine.user,
                'ansible_password': machine.password
            }

            try:
                for key, value in self.protos[testcase.proto].items():
                    if value == 'destination':
                        hostdict[key] = self.parse_dest(testcase.destination, netconfig)
                    else:
                        hostdict[key] = testcase.__dict__[value]

                self.inventory[testcase.proto]['hosts']['-'.join((machine.name,
                                                                str(testcase.name)))] = hostdict
            except KeyError as err:
                raise ValueError(f"{testcase.proto} is not a valid proto") from err

        with open(path, 'w', encoding='utf-8') as inventory_file:
            yaml.dump(self.inventory, inventory_file)

    def parse_dest(self, destination, netconfig:NetworkConfiguration):
        """
        Parses the Destination Value to a list of IP Address strings
        Destination may be:
            - the name of a Machine
            - the name of a Network
            - an IP-Address
            - an IP-Network
        Returns:
            List of IP-Addresses
        """
        destinations = []

        try:
            ipaddress.ip_address(destination)
        except ValueError:
            pass
        else:
            return [ipaddress.ip_address(destination).exploded]

        try:
            ipaddress.ip_network(destination)
        except ValueError:
            pass
        else:
            network = ipaddress.ip_network(destination)
            for machine in netconfig.machines.values():
                for ip in machine.ip_addresses:
                    if ip in network:
                        destinations.append(ip.exploded)

            if not destinations:
                raise ValueError(f"No Machines in Network {destination}")

        if destination in netconfig.machines:
            for ip in netconfig.machines[destination].ip_addresses:
                destinations.append(ip.exploded)

        if destination in netconfig.networks:
            for machine in netconfig.machines.values():
                for ip in machine.ip_addresses:
                    if ip in netconfig.networks[destination]:
                        destinations.append(ip.exploded)

        if not destinations:
            raise ValueError(f"{destination} is not a Valid Destination")
        return destinations

    def create_nft_inventory(self, path:str, netconfig: NetworkConfiguration):
        '''
        Creates a inventory file to setup the nftable files
        '''
        inventory = {'setup':{'hosts':{}}}
        for _, machine in netconfig.machines.items():
            if machine.nftable != '':
                hostdict = {
                    'ansible_host': machine.management_ip.exploded,
                    'ansible_user': machine.user,
                    'ansible_password': machine.password,
                    'nft_file': os.path.abspath(machine.nftable),
                    'filename': os.path.basename(machine.nftable)
                }
                inventory['setup']['hosts'][machine.name] = hostdict

        with open(path, 'w', encoding='utf-8') as inventory_file:
            yaml.dump(inventory, inventory_file)


    def execute_playbook(self, playbook):
        '''
        Runs a specific playbook
        '''
        cnt = {}
        return_dict = {}
        runner = ansible_runner.run(private_data_dir="ansible_runner",
                                        playbook=playbook, quiet=True, timeout=30)

        if runner.status == 'timeout':
            raise TimeoutError(f"Ansible playbook {playbook} Timed out")
        #get data from ansible
        for event in runner.events:
            data = event.get('event_data', {})
            res = data.get('res', {})
            host = data.get('host')
            if event['event'] == 'runner_item_on_ok' or event['event'] == 'runner_item_on_failed':
                cnt.setdefault(host, 0)
                return_dict[f"{host}-{cnt[host]}"] = {k: res.get(k) for k in ('stdout_lines',
                                                                            'stderr_lines',
                                                                            'rc',
                                                                            'start',
                                                                            'end',
                                                                            'delta',
                                                                            'msg')}
                cmd = res.get('cmd')
                return_dict[f"{host}-{cnt[host]}"]['cmd'] = " ".join(cmd) if \
                    isinstance(cmd, list)  else cmd
                return_dict[f"{host}-{cnt[host]}"]['unreachable'] =  res.get('unreachable', False)
                cnt[host] += 1
            elif playbook == 'setup.yml' and event['event'] == 'runner_on_ok':
                key = f"setup-{host}"

                if data.get('task_action') == "ansible.builtin.copy":
                    return_dict.setdefault(key, {})
                    return_dict[key].setdefault('path', res.get('path', ''))
                    return_dict[key].setdefault('changed', res.get('changed', False))
                    return_dict[key].setdefault('size', res.get('size', 0))
                    return_dict[key].setdefault('upload_start', data.get('start', ''))
                    return_dict[key].setdefault('upload_end', data.get('end', ''))
                    return_dict[key].setdefault('checksum', res.get('checksum', ''))
                    return_dict[key].setdefault('unreachable', False)

                elif data.get('task_action') == "ansible.builtin.command":
                    return_dict.setdefault(key, {})
                    return_dict[key].setdefault("stdout", res.get('stdout', ''))
                    return_dict[key].setdefault('stderr', res.get('stderr', ''))
                    return_dict[key].setdefault('rc', res.get('rc', 1))
                    return_dict[key].setdefault('msg', res.get('msg', ''))
                    cmd = res.get('cmd', '')
                    return_dict[key]['cmd'] = " ".join(cmd) if isinstance(cmd, list)  else cmd
                    return_dict[key].setdefault('load_rules_start', res.get('start', ''))
                    return_dict[key].setdefault('load_rules_end', res.get('end', ''))
                    return_dict[key].setdefault('unreachable', False)

            elif playbook == 'setup.yml' and event['event'] == 'runner_on_unreachable':
                key = f"setup-{host}"
                return_dict.setdefault(key, {})
                return_dict[key].setdefault('start', data.get('start', ''))
                return_dict[key].setdefault('end', data.get('end', ''))
                return_dict[key].update(res)

            elif playbook == 'setup.yml' and event['event'] == 'runner_on_failed':
                key = f"setup-{host}"
                return_dict.setdefault(key, {})
                return_dict[key].setdefault('start', data.get('start', ''))
                return_dict[key].setdefault('end', data.get('end', ''))
                return_dict[key].setdefault('rc', data.get('rc', 1))
                return_dict[key].setdefault('msg', res.get('msg', ''))
                return_dict[key].setdefault('unreachable', False)


        #clean artifacts
        shutil.rmtree("ansible_runner/artifacts")

        return return_dict

    def run(self, verb=1):
        '''
        Runs all Playbooks
        Returns:
            a dictionary with data from every playbook run looking like the following:
            {'hqfw-testcase_3': {
                'stdout': '...',
                'stderr': '',
                'rc': 0,
                'cmd': 'ping -c 4 172.16.0.10',
                'start': '2025-06-04 21:45:03.450576',
                'end': '2025-06-04 21:45:06.492123',
                'delta': '0:00:03.041547',
                'msg': '',
                'unreachable': False
                }
            }
        '''
        return_dict = {}

        for key in self.protos.keys():

            if verb >= 1:
                print(f"Starting {key} tests")

            return_dict.update(self.execute_playbook(f"{key}_playbook.yml"))

        return return_dict
