import re
import logging
import yaml
root_logger = logging.getLogger(__name__)

tagger_dictionary = None
with open("tagger_config/tagsets.yml", 'r') as stream:
    tagger_dictionary = yaml.safe_load(stream)

stanford_pos_dictionary = tagger_dictionary['tagsets']['stanford_tags']

def Split_raw_identifier(identifier_data):
    if '(' in identifier_data: 
        identifier_data = identifier_data.split('(')[0]
    identifier_type_and_name = identifier_data.split()
    if len(identifier_type_and_name) < 2: 
        raise Exception("Malformed identifier")
    return identifier_type_and_name

def Parse_stanford(stanford_output, split_identifier_name):
    grammar_pattern = []
    
    #We append 'I' to function names for Stanford. Remove it here.
    if stanford_output[0] == 'I' and not split_identifier_name[0] == 'I':
        stanford_output = ' '.join(stanford_output.split()[1:])

    raw_grammar_pattern = re.findall("_([A-Za-z]+)", stanford_output)
    for pos_token in raw_grammar_pattern:
        if pos_token in stanford_pos_dictionary:
            grammar_pattern.append(stanford_pos_dictionary[pos_token])
        else:
            grammar_pattern.append(pos_token)

    #Sanity check: Identifier name can't be longer than grammar pattern
    if len(split_identifier_name) != len(grammar_pattern):
        root_logger.debug("Stanford: {taggerout} {ident}".format(taggerout=stanford_output, ident=split_identifier_name))
        return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(["FAILURE" for x in split_identifier_name])))
    
    return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(grammar_pattern)))