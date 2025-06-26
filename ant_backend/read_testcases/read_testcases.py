"""
Module: read_testcases.py

This module provides classes for defining and loading network test cases 
used for automated firewall rule validation. Test cases are described in 
a YAML file and include parameters such as source and destination hosts, 
protocols, ports, scoring points, and expected allow/deny behavior.

Classes:
    Testcase: Represents a single network test case with its parameters.
    TestcaseConfiguration: Loads and stores multiple Testcase objects from a YAML file.

Exceptions:
    - AttributeError: Raised when required attributes are missing in the YAML file.
"""

import yaml

class Testcase:
    """
    Represents a single network test case with relevant parameters.
    """
    def __init__(self, name, source, destination, proto, s_port=None,
                 d_port=None, points=0, allow=True, special = None):
        self.name = name
        self.source = source
        self.destination = destination
        self.proto = proto
        self.s_port = s_port
        self.d_port = d_port
        self.points = points
        self.allow = allow
        self.special = special

    def __repr__(self):
        return (f"Testcase(name={self.name}, source={self.source}, destination={self.destination}, "
                f"proto={self.proto}, s_port={self.s_port}, d_port={self.d_port}, "
                f"points={self.points}, allow={self.allow}, special={self.special})")

class TestcaseConfiguration:
    """
    Loads and stores multiple Testcase objects from a YAML configuration file.
    """
    def __init__(self):
        # List of Testcase objects
        self.testcases = []

    def add_testcase(self, name, source: str, destination: str, proto: str,
                     s_port: list[int], d_port: list[int], points: int, 
                     allow: bool, special: dict):
        """
        Adds a single Testcase instance to the configuration.
        """
        self.testcases.append(Testcase(name, source, destination, proto, s_port, d_port, points,
                                       allow, special))

    def load_from_yaml(self, file_name):
        """
        Loads test cases from a YAML file and adds them to the configuration.
        """
        with open(file_name, 'r', encoding='utf-8') as testcases_file:
            data = yaml.safe_load(testcases_file)

        for index, entry in enumerate(data):
            # Use default name if not explicitly provided
            name = entry.get("Name") or f"testcase_{index}"
            source = entry.get("Source").lower()
            destination = entry.get("Destination").lower()
            proto = entry.get("Proto")
            s_port = entry.get("S_port") or []
            d_port = entry.get("D_port") or []
            points = entry.get("Points") or 1
            allow = entry.get("Allow") or True
            special = entry.get("Special") or {}

            # Ensure required fields are present
            if not source:
                raise AttributeError(f"{file_name} missing Source attribute!\n")
            if not destination:
                raise AttributeError(f"{file_name} missing Destination attribute!\n")
            if not proto:
                raise AttributeError(f"{file_name} missing Proto attribute!\n")

            if points <= 0:
                points = 1

            self.add_testcase(name, source, destination, proto, s_port, d_port, points, allow, special)

    def __repr__(self):
        return f"TestcaseConfiguration(testcases={self.testcases})"
