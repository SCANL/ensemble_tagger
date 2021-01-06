import unittest
from model_classification import calculate_normalized_length
from model_classification import CODE_CONTEXT
class TestNormalizeLength(unittest.TestCase):
    def setUp(self):
        self.ensemble_input_with_normalized_length_0 = {'Get0': ['V', 'V', 'VBP']}
        self.ensemble_input_with_normalized_length_1 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N']}
        self.ensemble_input_with_normalized_length_2 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N'], 'Name': ['N', 'N', 'N']}
        self.ensemble_input_with_normalized_length_3 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N'], 'Name': ['N', 'N', 'N'], 'String': ['N', 'N', 'N']}
    def test_normalized_length_0(self):
        processed_input = calculate_normalized_length(self.ensemble_input_with_normalized_length_0)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0]}, processed_input)
    def test_normalized_length_1(self):
        processed_input = calculate_normalized_length(self.ensemble_input_with_normalized_length_1)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 2]}, processed_input)
    def test_normalized_length_2(self):
        processed_input = calculate_normalized_length(self.ensemble_input_with_normalized_length_2)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 2]}, processed_input)
    def test_normalized_length_3(self):
        processed_input = calculate_normalized_length(self.ensemble_input_with_normalized_length_3)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 1],'String': ['N', 'N', 'N', 2]}, processed_input)
if __name__ == '__main__':
    unittest.main()