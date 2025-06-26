import unittest
from ant_backend import AnsibleManager, TestcaseConfiguration, NetworkConfiguration

class AnsibleManagerTest(unittest.TestCase):

    def setUp(self):
        self.manager = AnsibleManager('ant_backend/tests/ansible_manager/testprotos.yml')
        self.netconfig = NetworkConfiguration()
        self.testconfig = TestcaseConfiguration()

    def test_invalid_destination(self):
        self.netconfig.load_from_yaml('ant_backend/tests/ansible_manager/infra.yml')
        self.testconfig.load_from_yaml('ant_backend/tests/ansible_manager/invalid_machine.yml')

        with self.assertRaises(ValueError):
            self.manager.create_inventory('', self.netconfig, self.testconfig)
            self.testconfig.load_from_yaml('ant_backend/tests/ansible_manager/invalid_ip.yml')
            self.manager.create_inventory('', self.netconfig, self.testconfig)

    def test_invalid_proto(self):
        self.netconfig.load_from_yaml('ant_backend/tests/ansible_manager/infra.yml')
        self.testconfig.load_from_yaml('ant_backend/tests/ansible_manager/invalid_proto.yml')

        with self.assertRaises(KeyError):
            self.manager.create_inventory('', self.netconfig, self.testconfig)

    def test_valid(self):
        self.netconfig.load_from_yaml('ant_backend/tests/ansible_manager/infra.yml')
        self.testconfig.load_from_yaml('ant_backend/tests/ansible_manager/valid_tests.yml')

        referenceFile = 'ant_backend/tests/ansible_manager/ref_inventory.yml'
        testFile = 'ant_backend/tests/ansible_manager/check_inventory.yml'

        self.manager.create_inventory(testFile, self.netconfig, self.testconfig)

        with open(referenceFile, 'r', encoding='utf-8') as ref, open(testFile,
                                                                     'r', encoding='utf-8') as cmp:
            self.assertListEqual(list(ref), list(cmp))


if __name__ == '__main__':
    unittest.main()
