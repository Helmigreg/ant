import unittest
from ant_backend import NetworkConfiguration


class UnitTest(unittest.TestCase):

    def setUp(self):
        self.valid_config = NetworkConfiguration()
        self.valid_config.add_networks("test_network", 24, "192.168.0.0")
        self.valid_config.add_machine("test_machine", ["192.168.1.1"], "10.0.0.1",
                                      "toor", "toor123")

    def test_fully_working(self):
        fully_working_netconfig = NetworkConfiguration()

        fully_working_netconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra.yml")

        self.assertEqual(fully_working_netconfig, self.valid_config)

    def test_value_error(self):
        testconfig = NetworkConfiguration()
        with self.assertRaises(ValueError):
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_wrong_ipv4.yml")
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_wrong_ipv6.yml")

    def test_attribute_error(self):
        testconfig = NetworkConfiguration()
        with self.assertRaises(AttributeError):
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_missing_networks.yml")
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_missing_machine.yml")

    def test_key_error(self):
        testconfig = NetworkConfiguration()
        with self.assertRaises(KeyError):
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_missing_network_value.yml")
            testconfig.load_from_yaml("ant_backend/tests/read_testinfra/infra_missing_machine_value.yml")

if __name__ == '__main__':
    unittest.main()
