import re
import logging
import yaml
root_logger = logging.getLogger(__name__)

tagger_dictionary = None
with open("tagger_config/tagsets.yml", 'r') as stream:
    tagger_dictionary = yaml.safe_load(stream)

swum_pos_dictionary = tagger_dictionary['tagsets']['swum_tags']
posse_pos_dictionary = tagger_dictionary['tagsets']['posse_tags']
stanford_pos_dictionary = tagger_dictionary['tagsets']['stanford_tags']

def Split_raw_identifier(identifier_data):
    if '(' in identifier_data: 
        identifier_data = identifier_data.split('(')[0]
    identifier_type_and_name = identifier_data.split()
    if len(identifier_type_and_name) < 2: 
        raise Exception("Malformed identifier")
    return identifier_type_and_name

def Parse_swum(swum_output, split_identifier_name):
    code_context = swum_output.split('#')
    raw_grammar_pattern = grammar_pattern = identifier = []
    if code_context[0] == 'FIELD':
        identifier = code_context[1].split('-')[1].split()
        raw_grammar_pattern = re.findall('([A-Z]+)', ' '.join(identifier))
    else:
        identifier = code_context[1].split('@')[1].split('|')
        raw_grammar_pattern = re.findall('([A-Z]+)', ' '.join(identifier))
    
    for pos in raw_grammar_pattern:
        if pos in swum_pos_dictionary:
            grammar_pattern.append(swum_pos_dictionary[pos])

    #Sanity check: Identifier name can't be longer than grammar pattern
    if len(split_identifier_name) != len(grammar_pattern):
        root_logger.debug("SWUM: {taggerout} {ident}".format(taggerout=swum_output, ident=split_identifier_name))
        return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(["FAILURE" for x in split_identifier_name])))
        #raise Exception("Mismatch between name ({idname}) and grammar pattern ({gp})".format(idname=split_identifier_name, gp=grammar_pattern))

    return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(grammar_pattern)))
    
def Parse_posse(posse_output, split_identifier_name):
    grammar_pattern = []
    raw_grammar_pattern = re.findall(':([A-Z-a-z]+)', posse_output)
    for pos_token in raw_grammar_pattern:
        if pos_token in posse_pos_dictionary:
            grammar_pattern.append(posse_pos_dictionary[pos_token])
        else:
            grammar_pattern.append(pos_token)
    
    #Sanity check: Identifier name can't be longer than grammar pattern
    if len(split_identifier_name) != len(grammar_pattern):
        root_logger.debug("POSSE: {taggerout} {ident}".format(taggerout=posse_output, ident=split_identifier_name))
        return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(["FAILURE" for x in split_identifier_name])))
    
    return("{identifier_names},{grammar_pattern}"
          .format(identifier_names=' '.join(split_identifier_name), 
            grammar_pattern=' '.join(grammar_pattern)))

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