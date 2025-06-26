"""a quick test for the script validator"""
import unittest
from ant_backend import validate_script

class NftScriptTest(unittest.TestCase):
    def setUp(self):
        self.valid_file = "ant_backend/tests/validate_nft/valid.nft"
        self.invalid_file = "ant_backend/tests/validate_nft/invalid.nft"

    def test_no_file(self):
        self.assertIsNotNone(validate_script(""))
        self.assertIsNone(validate_script(self.valid_file))

    def test_file_valid(self):
        error = ('ant_backend/tests/validate_nft/invalid.nft:24:6-11: Error: syntax error,'
        ' unexpected string\n\t\tct states established counter accept #error here\n\t\t   ^^^^^^\n')
        self.assertIsNone(validate_script(self.valid_file))
        self.assertTupleEqual((['Error: syntax error, unexpected string\n'],error),
                              validate_script(self.invalid_file))


if __name__ == '__main__':
    unittest.main()
