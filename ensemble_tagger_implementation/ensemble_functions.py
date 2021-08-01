from process_features import Get_identifier_context, CODE_CONTEXT, Convert_tag_to_numeric_category
from preprocess_identifiers import Parse_posse, Parse_stanford, Parse_swum, Split_raw_identifier

import logging
root_logger = logging.getLogger(__name__)
root_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('tagger_error.log', 'a', 'utf-8')
root_logger.addHandler(handler)
import pandas as pd
import sys, subprocess, joblib, pexpect
import yaml
from spiral import ronin

stanford_process = pexpect.spawn(
    """java -mx3g -cp 
    '../stanford-postagger-2018-10-16/stanford-postagger.jar:' 
    edu.stanford.nlp.tagger.maxent.MaxentTagger 
    -model ../stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger""")

stanford_process.expect("(For EOF, use Return, Ctrl-D on Unix; Enter, Ctrl-Z, Enter on Windows.)")

def Process_identifier_with_swum(identifier_data, context_of_identifier):
    #format identifier string in preparation to send it to SWUM
    identifier_type_and_name = Split_raw_identifier(identifier_data)
    split_identifier_name_raw = ronin.split(identifier_type_and_name[1])
    split_identifier_name = '_'.join(ronin.split(identifier_type_and_name[1]))
    if Get_identifier_context(context_of_identifier) != CODE_CONTEXT.FUNCTION:
        swum_string = "{identifier_type} {identifier_name}".format(identifier_name = split_identifier_name, identifier_type = identifier_type_and_name[0])
        swum_process = subprocess.Popen(['java', '-jar', '../SWUM/SWUM_POS/swum.jar', swum_string, '2', 'true'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        split_identifier_name = split_identifier_name+'('+identifier_data.split('(')[1]
        swum_string = " {identifier_type} {identifier_name}".format(identifier_name = split_identifier_name, identifier_type = identifier_type_and_name[0])
        swum_process = subprocess.Popen(['java', '-jar', '../SWUM/SWUM_POS/swum.jar', swum_string, '1', 'true'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    swum_out, swum_err = swum_process.communicate()
    swum_parsed_out = Parse_swum(swum_out.decode('utf-8').strip(), split_identifier_name_raw)
    return swum_parsed_out

def Process_identifier_with_posse(identifier_data, context_of_identifier):
    #format identifier string in preparation to send it to POSSE
    identifier_type_and_name = Split_raw_identifier(identifier_data)
    split_identifier_name_raw = ronin.split(identifier_type_and_name[1])
    split_identifier_name = ' '.join(split_identifier_name_raw)
    posse_string = "{data} | {identifier_name}".format(data = identifier_data, identifier_name = split_identifier_name)
    type_value = Get_identifier_context(context_of_identifier)
    if any([type_value == x for x in [CODE_CONTEXT.DECLARATION, CODE_CONTEXT.ATTRIBUTE, CODE_CONTEXT.PARAMETER]]):
        posse_process = subprocess.Popen(['../POSSE/Scripts/mainParser.pl', 'A', posse_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif type_value == CODE_CONTEXT.CLASS:
        posse_process = subprocess.Popen(['../POSSE/Scripts/mainParser.pl', 'C', posse_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        posse_process = subprocess.Popen(['../POSSE/Scripts/mainParser.pl', 'M', posse_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    posse_out, posse_err = posse_process.communicate()
    posse_out_parsed = Parse_posse(posse_out.decode('utf-8').strip(), split_identifier_name_raw)
    return posse_out_parsed

def Process_identifier_with_stanford(identifier_data, context_of_identifier):
    identifier_type_and_name = identifier_data.split()
    identifier_type_and_name = Split_raw_identifier(identifier_data)
    split_identifier_name_raw = ronin.split(identifier_type_and_name[1])
    if Get_identifier_context(context_of_identifier) != CODE_CONTEXT.FUNCTION:
        split_identifier_name = "{identifier_name}".format(identifier_name=' '.join(split_identifier_name_raw))
    else:
        split_identifier_name = "I {identifier_name}".format(identifier_name=' '.join(split_identifier_name_raw))
    
    stanford_process.sendline(split_identifier_name)
    stanford_process.expect(' '.join([word+'_[A-Z]+' for word in split_identifier_name_raw]))
    #stanford_out, stanford_err = stanford_process.communicate()
    stanford_out = Parse_stanford(stanford_process.after.decode('utf-8').strip(), split_identifier_name_raw)
    return stanford_out

def Generate_ensemble_tagger_input_format(external_tagger_outputs):
    ensemble_input = dict()
    for tagger_output in external_tagger_outputs:
        identifier, grammar_pattern = tagger_output.split(',')
        identifier_grammarPattern = zip(identifier.split(), grammar_pattern.split())
        i = 0
        for word_gp_pair in identifier_grammarPattern:
            if word_gp_pair[0]+str(i) in ensemble_input:
                ensemble_input[word_gp_pair[0]+str(i)].append(word_gp_pair[1])
            else:
                ensemble_input[word_gp_pair[0]+str(i)] = [word_gp_pair[1]]
            i = i + 1
    root_logger.debug("Final ensemble input: {identifierDat}".format(identifierDat=ensemble_input))
    return ensemble_input

def Run_external_taggers(identifier_data, context_of_identifier):
    external_tagger_outputs = []
    #split and process identifier data into external tagger outputs
    external_tagger_outputs.append(Process_identifier_with_swum(identifier_data, context_of_identifier))
    external_tagger_outputs.append(Process_identifier_with_posse(identifier_data, context_of_identifier))
    external_tagger_outputs.append(Process_identifier_with_stanford(identifier_data, context_of_identifier))
    root_logger.debug("raw ensemble input: {identifierDat}".format(identifierDat=external_tagger_outputs))
    return Generate_ensemble_tagger_input_format(external_tagger_outputs)

def Annotate_word(swum_tag, posse_tag, stanford_tag, normalized_length, code_context):
    model_dictionary = input_model = swum = posse = stanford = None
    
    #Determine whether to go with default model (DTCP) or if user selected one
    with open("tagger_config/model_config.yml", 'r') as stream:
        model_dictionary = yaml.safe_load(stream)
        if len(sys.argv) < 2:
            input_model = model_dictionary['models']['DTCP']
            swum, posse, stanford = Convert_tag_to_numeric_category(swum_tag, posse_tag, stanford_tag, 'DTCP')
        else:
            input_model = model_dictionary['models'][sys.argv[1]]
            swum, posse, stanford = Convert_tag_to_numeric_category(swum_tag, posse_tag, stanford_tag, sys.argv[1])

    data = {'SWUM_TAG': [swum],
            'POSSE_TAG': [posse],
            'STANFORD_TAG': [stanford],
            'NORMALIZED_POSITION': [normalized_length],
            'CONTEXT': [code_context]
            }

    df_features = pd.DataFrame(data,
                               columns=['SWUM_TAG', 'POSSE_TAG', 'STANFORD_TAG', 'NORMALIZED_POSITION', 'CONTEXT'])

    clf = joblib.load(input_model)
    y_pred = clf.predict(df_features)
    return (y_pred[0])

#read_from_cmd_line()