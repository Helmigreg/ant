import unittest
import os
from ant_backend import Testcase, TestcaseConfiguration

class TestTestcase(unittest.TestCase):

    def test_creation(self):
        tc = Testcase("Test1", "brclient", "brfw", "tcp", [], [80, 443], 2, True, {})
        self.assertEqual(tc.name, "Test1")
        self.assertEqual(tc.source, "brclient")
        self.assertEqual(tc.destination, "brfw")
        self.assertEqual(tc.proto, "tcp")
        self.assertEqual(tc.s_port, [])
        self.assertEqual(tc.d_port, [80, 443])
        self.assertEqual(tc.points, 2)
        self.assertTrue(tc.allow)
        self.assertEqual(tc.special, {})

class TestTestcaseConfiguration(unittest.TestCase):

    def setUp(self):
        self.config = TestcaseConfiguration()
        self.testdata_dir = "ant_backend/tests/read_testcases"

    def test_add_testcase(self):
        self.config.add_testcase("Test001", "brfw", "192.168.0.1", "icmpv4",[], [], 1, False, {})
        self.assertEqual(len(self.config.testcases), 1)
        self.assertEqual(self.config.testcases[0].proto, "icmpv4")

    def test_load_from_yaml_valid(self):
        path = os.path.join(self.testdata_dir, "Testkriterien_example.yml")
        self.config.load_from_yaml(path)
        self.assertGreater(len(self.config.testcases), 0)
        self.assertEqual(self.config.testcases[0].source, "brclient")
        self.assertEqual(self.config.testcases[0].destination, "brfw")
        self.assertEqual(self.config.testcases[0].proto, "tcp")

    def test_load_from_yaml_missing_source(self):
        path = os.path.join(self.testdata_dir, "missing_source.yml")
        with self.assertRaises(AttributeError):
            self.config.load_from_yaml(path)

    def test_load_from_yaml_missing_destination(self):
        path = os.path.join(self.testdata_dir, "missing_destination.yml")
        with self.assertRaises(AttributeError):
            self.config.load_from_yaml(path)

    def test_load_from_yaml_missing_proto(self):
        path = os.path.join(self.testdata_dir, "missing_proto.yml")
        with self.assertRaises(AttributeError):
            self.config.load_from_yaml(path)

if __name__ == "__main__":
    unittest.main()
