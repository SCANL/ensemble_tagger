from enum import IntEnum

class CODE_CONTEXT(IntEnum):
    ATTRIBUTE = 1
    CLASS = 2
    DECLARATION = 3
    FUNCTION = 4
    PARAMETER = 5

def Convert_tag_to_numeric_category(key_swum, key_posse, key_stanford, model_type):
    swum = posse = stanford = None
    #DTCP or RFCP
    if model_type == 'DTCP' or model_type == 'RFCP':
        swum = {'D':0, 'DT':1, 'FAILURE':2, 'N':3, 'NM':4, 'P':5, 'PR':6, 'PRE':7, 'V':8}
        posse = {'DT':0, 'FAILURE':1, 'N':2, 'NM':3, 'P':4, 'PR':5, 'V':6}
        stanford = {'CJ':0, 'D':1, 'DT':2, 'FAILURE':3, 'N':4, 'NM':5, 'NPL':6, 'P':7, 'PR':8, 'V':9, 'VBD':10, 'VBG':11, 'VBN':12, 'VBP':13, 'VBZ':14, 'VM':15}

    #DTCA or RFCA
    if model_type == 'DTCA' or model_type == 'RFCA':
        swum = {'D':0, 'FAILURE':1, 'N':2, 'NM':3, 'OTHER':4, 'P':5, 'PRE':6, 'V':7, 'PR':8}
        posse = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'V':5}
        stanford = {'D':0, 'FAILURE':1, 'N':2, 'NM':3, 'NPL':4, 'OTHER':5, 'P':6, 'V':7, 'VBD':8, 'VBG':9, 'VBN':10, 'VBP':11, 'VBZ':12}

    #DTNP or RFNP
    if model_type == 'DTNP' or model_type == 'RFNP':
        swum = {'D':0, 'DT':1, 'FAILURE':2, 'N':3, 'NM':4, 'P':5, 'PR':6, 'PRE':7, 'V':8}
        posse = {'DT':0, 'FAILURE':1, 'N':2, 'NM':3, 'P':4, 'PR':5, 'V':6}
        stanford = {'CJ':0, 'D':1, 'DT':2, 'N':3, 'NM':4, 'NPL':5, 'P':6, 'PR':7, 'V':8, 'VM':9, 'FAILURE':10}

    #DTNA or RFNA
    if model_type == 'DTNA' or model_type == 'RFNA':
        swum = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'PRE':5, 'V':6, 'PR':7}
        posse = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'V':5}
        stanford = {'N':0, 'NM':1, 'NPL':2, 'OTHER':3, 'P':4, 'V':5,'FAILURE':6}

    return swum.get(key_swum), posse.get(key_posse), stanford.get(key_stanford)

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