"""
Module: infrastructure.py

This module provides classes for representing a network infrastructure, including networks and 
    machines. 
It allows loading network configurations from a YAML file and validating IP addresses.

Exceptions:
    - ValueError: Raised when an invalid IP address is provided.
    - AttributeError: Raised when required attributes are missing in the YAML file.
"""

import ipaddress
import os
import yaml

class Machine(object):
    """
    Class representing a machine
    """
    def __init__(self, name:str, ip_addresses:list, management_ip:str, username:str, password:str, nftable:str):
        self.name = name
        self.ip_addresses = []
        ipv6 = False
        if ipaddress.ip_address(ip_addresses[0]).version == 6:
            ipv6 = True
        for ip_address in ip_addresses:
            ip = ipaddress.ip_address(ip_address)
            if ipv6 and ip.version == 4:
                raise AttributeError("Ipv4 and IPv6 Addresses mixed")
            elif not ipv6 and ip.version == 6:
                raise AttributeError("Ipv4 and IPv6 Addresses mixed")
            self.ip_addresses.append(ip)
        self.management_ip = ipaddress.ip_address(management_ip)
        self.user = username
        self.password = password
        self.nftable = nftable

    def __eq__(self, other):
        return self.name == other.name and self.ip_addresses == other.ip_addresses and \
            self.management_ip == other.management_ip

    def __repr__(self):
        return f"(name={self.name}, ip_address={self.ip_addresses}, \
            management_ip={self.management_ip})"

class NetworkConfiguration(object):
    """
    Class representing the Network Configuration.
    """
    def __init__(self):
        self.networks = {}
        self.machines = {}

    def __eq__(self, other):
        return self.networks == other.networks and self.machines == other.machines

    def add_networks(self, name, netmask, netaddress):
        """
        Methode for adding a new Network Object for the Network Configuration
        """
        self.networks[name] = ipaddress.ip_network((netaddress, netmask))

    def add_machine(self, name, ip_address, management_ip, username, password, nftable):
        """
        Methode for adding a new Machine Object for the Network Configuration
        """
        self.machines[name] = Machine(name, ip_address, management_ip, username, password, nftable)

    def __repr__(self):
        return f"NetworkConfiguration(networks={self.networks}, machine={self.machines})"


    def load_from_yaml(self, file_name):
        """
        Methode for loading a .yml-file and creating new networks and machine classes from the 
        loaded .yml-file
        """
        nftable_exists = False
        with open(file_name, 'r', encoding='utf-8') as infrastructur_file:
            data = yaml.safe_load(infrastructur_file)

        for net_name, net_info in data.get("Networks", {}).items():
            self.add_networks(net_name.lower(), net_info["Netmask"], net_info["Netaddress"])

        for machine_name, machine_info in data.get("Machines", {}).items():
            self.add_machine(machine_name.lower(), machine_info["IP"], machine_info["Management"],
                             machine_info["User"], machine_info["Password"],
                             machine_info.get('NFTable', ''))
            if machine_info.get('NFTable', '') != '' and os.path.isfile(machine_info.get('NFTable')):
                nftable_exists = True

        if not self.networks:
            raise AttributeError(f"{file_name} missing Networks attribute")

        if not self.machines:
            raise AttributeError(f"{file_name} missing Machines attribute")
        
        if not nftable_exists:
            raise AttributeError("Missing at least one NFTable configuration file")
