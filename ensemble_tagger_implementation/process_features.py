from enum import IntEnum

class CODE_CONTEXT(IntEnum):
    ATTRIBUTE = 1
    CLASS = 2
    DECLARATION = 3
    FUNCTION = 4
    PARAMETER = 5

def Convert_tag_to_numeric_category(key_swum, key_stanford, model_type):
    swum = stanford = None
    #DTCP or RFCP
    if model_type == 'DTCP':
        swum = {'D':0, 'DT':1, 'N':2, 'NM':3, 'P':4, 'PR':5, 'PRE':6, 'V':7, 'FAILURE':8}
        stanford = {'CJ':0, 'D':1, 'DT':2, 'N':3, 'NM':4, 'NPL':5, 'P':6, 'V':7, 'VBD':8, 'VBG':9, 'VBN':10, 'VBP':11, 'VBZ':12, 'VM':13, 'FAILURE':14}

    return swum.get(key_swum), stanford.get(key_stanford)

def Get_identifier_context(id_type):
   IDENTIFIER_TYPE = {}
   IDENTIFIER_TYPE['ATTRIBUTE'] = CODE_CONTEXT.ATTRIBUTE
   IDENTIFIER_TYPE['CLASS'] = CODE_CONTEXT.CLASS
   IDENTIFIER_TYPE['DECLARATION'] = CODE_CONTEXT.DECLARATION
   IDENTIFIER_TYPE['FUNCTION'] = CODE_CONTEXT.FUNCTION
   IDENTIFIER_TYPE['PARAMETER'] = CODE_CONTEXT.PARAMETER
   if id_type in IDENTIFIER_TYPE:
        return IDENTIFIER_TYPE[id_type]
   else:
        raise Exception("CONTEXT {context} NOT FOUND".format(context=id_type))

def Calculate_normalized_length(ensemble_input):
    i = 0
    for key, value in ensemble_input.items():
        if i == 0:
            ensemble_input[key].append(0)
        elif i > 0 and i < (len(ensemble_input)-1):
            ensemble_input[key].append(1)
        else:
            ensemble_input[key].append(2)
        i = i + 1
    return ensemble_input

def Add_code_context(ensemble_input, context):
    for key, value in ensemble_input.items():
        try:
            ensemble_input[key].append(Get_identifier_context(context))
        except Exception as context_exception:
            raise context_exception
    return ensemble_input