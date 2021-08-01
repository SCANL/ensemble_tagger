import unittest, csv
from process_features import CODE_CONTEXT, Calculate_normalized_length, Add_code_context
from ensemble_functions import Annotate_word, Generate_ensemble_tagger_input_format

class TestNormalizeLength(unittest.TestCase):
    def setUp(self):
        self.ensemble_input_with_normalized_length_0 = {'Get0': ['V', 'V', 'VBP']}
        self.ensemble_input_with_normalized_length_1 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N']}
        self.ensemble_input_with_normalized_length_2 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N'], 'Name': ['N', 'N', 'N']}
        self.ensemble_input_with_normalized_length_3 = {'Get0': ['V', 'V', 'VBP'], 'Identifier1': ['N', 'N', 'N'], 'Name': ['N', 'N', 'N'], 'String': ['N', 'N', 'N']}
    def test_normalized_length_0(self):
        processed_input = Calculate_normalized_length(self.ensemble_input_with_normalized_length_0)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0]}, processed_input)
    def test_normalized_length_1(self):
        processed_input = Calculate_normalized_length(self.ensemble_input_with_normalized_length_1)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 2]}, processed_input)
    def test_normalized_length_2(self):
        processed_input = Calculate_normalized_length(self.ensemble_input_with_normalized_length_2)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 2]}, processed_input)
    def test_normalized_length_3(self):
        processed_input = Calculate_normalized_length(self.ensemble_input_with_normalized_length_3)
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 1],'String': ['N', 'N', 'N', 2]}, processed_input)

class TestAddCodeContext(unittest.TestCase):
    def setUp(self):
        self.ensemble_input_with_conext_attribute = {'Get0': ['V', 'V', 'VBP', 0]}
        self.ensemble_input_with_conext_class = {'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 2]}
        self.ensemble_input_with_conext_declaration = {'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 2]}
        self.ensemble_input_with_conext_function = {'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 1],'String': ['N', 'N', 'N', 2]}
        self.ensemble_input_with_conext_parameter = {'Get0': ['V', 'V', 'VBP', 0], 'Identifier1': ['N', 'N', 'N', 1], 'Name': ['N', 'N', 'N', 1],'String': ['N', 'N', 'N', 2]}
    def test_add_context_attribute(self):
        processed_input = Add_code_context(self.ensemble_input_with_conext_attribute, "ATTRIBUTE")
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0, CODE_CONTEXT.ATTRIBUTE]}, processed_input)
    def test_add_context_class(self):
        processed_input = Add_code_context(self.ensemble_input_with_conext_class, "CLASS")
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0, CODE_CONTEXT.CLASS], 'Identifier1': ['N', 'N', 'N', 2, CODE_CONTEXT.CLASS]}, processed_input)
    def test_add_context_declaration(self):
        processed_input = Add_code_context(self.ensemble_input_with_conext_declaration, "DECLARATION")
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0, CODE_CONTEXT.DECLARATION], 'Identifier1': ['N', 'N', 'N', 1, CODE_CONTEXT.DECLARATION], 'Name': ['N', 'N', 'N', 2, CODE_CONTEXT.DECLARATION]}, processed_input)
    def test_add_context_function(self):
        processed_input = Add_code_context(self.ensemble_input_with_conext_function, "FUNCTION")
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0, CODE_CONTEXT.FUNCTION], 'Identifier1': ['N', 'N', 'N', 1,CODE_CONTEXT.FUNCTION], 'Name': ['N', 'N', 'N', 1,CODE_CONTEXT.FUNCTION],'String': ['N', 'N', 'N', 2,CODE_CONTEXT.FUNCTION]}, processed_input)
    def test_add_context_parameter(self):
        processed_input = Add_code_context(self.ensemble_input_with_conext_parameter,"PARAMETER")
        self.assertEqual({'Get0': ['V', 'V', 'VBP', 0, CODE_CONTEXT.PARAMETER], 'Identifier1': ['N', 'N', 'N', 1, CODE_CONTEXT.PARAMETER], 'Name': ['N', 'N', 'N', 1, CODE_CONTEXT.PARAMETER],'String': ['N', 'N', 'N', 2, CODE_CONTEXT.PARAMETER]}, processed_input)
    def test_add_context_raises_exception(self):
       with self.assertRaises(Exception):
           Add_code_context(self.ensemble_input_with_conext_parameter,"PARAM")

class TestGenerateEnsembleTaggerInputFormat(unittest.TestCase):
    def setUp(self):
        self.raw_input = ['Get Identifier,V N', 'Get Identifier,FAILURE FAILURE', 'Get Identifier,VBP N']
    def test_generate_input_format_with_failure(self):
        processed_input = Generate_ensemble_tagger_input_format(self.raw_input)
        self.assertEqual({'Get0': ['V', 'FAILURE', 'VBP'], 'Identifier1': ['N', 'FAILURE', 'N']},processed_input)

class TestTaggerAccuracyOnTestSet(unittest.TestCase):
    def setUp(self):
        self.tagged_identifier_list = []
        with open('test_data/testing_set_CP.csv', newline='') as csvfile:
            pos_reader = csv.DictReader(csvfile, quotechar='"')
            for row in pos_reader:
                identifier = row['IDENTIFIER']
                stanford_pos = row['STANFORD']
                swum_pos = row ['SWUM']
                posse_pos = row ['POSSE']
                normalized_position = row['NORMALIZED_POSITION']
                context = row['CONTEXT']
                expected = row['PREDICTION']
                self.tagged_identifier_list.append([identifier, swum_pos, posse_pos, stanford_pos, normalized_position, context, expected])
    def test_generate_input_format_with_failure(self):
        for tagged_identifier in self.tagged_identifier_list:
            prediction = Annotate_word(tagged_identifier[1], tagged_identifier[2], tagged_identifier[3], int(tagged_identifier[4]), int(tagged_identifier[5]))
            self.assertEqual(prediction, tagged_identifier[6])
class TestTaggerAccuracyOnTrainingSet(unittest.TestCase):
    def setUp(self):
        self.tagged_identifier_list = []
        with open('test_data/training_set_CP.csv', newline='') as csvfile:
            pos_reader = csv.DictReader(csvfile, quotechar='"')
            for row in pos_reader:
                identifier = row['IDENTIFIER']
                stanford_pos = row['STANFORD']
                swum_pos = row ['SWUM']
                posse_pos = row ['POSSE']
                normalized_position = row['NORMALIZED_POSITION']
                context = row['CONTEXT']
                expected = row['PREDICTION']
                self.tagged_identifier_list.append([identifier, swum_pos, posse_pos, stanford_pos, normalized_position, context, expected])
    def test_generate_input_format_with_failure(self):
        for tagged_identifier in self.tagged_identifier_list:
            prediction = Annotate_word(tagged_identifier[1], tagged_identifier[2], tagged_identifier[3], int(tagged_identifier[4]), int(tagged_identifier[5]))
            self.assertEqual(prediction, tagged_identifier[6])
            #root_logger.info("Checking {identifier}".format(identifier=tagged_identifier[0]))
if __name__ == '__main__':
    unittest.main()