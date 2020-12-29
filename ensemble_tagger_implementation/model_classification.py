import sqlite3
import sys
import joblib
import pandas as pd
import subprocess
from spiral import ronin

#java -mx3g -cp '../stanford-postagger-2018-10-16/stanford-postagger.jar:' edu.stanford.nlp.tagger.maxent.MaxentTagger -model ../stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger

def run_external_taggers(data):
    #split and process identifier data
    identifier_type_name = data.split()[0]
    identifier_name = data.split()[1]
    split_identifier_name = ' '.join(ronin.split(identifier_name))

    #format identifier string in preparation to send it to SWUM
    swum_string = "{data}".format(data = data)    
    process = subprocess.Popen(['java', '-jar', '../SWUM/SWUM_POS/swum.jar', swum_string, '2', 'true'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    print("swum: " + out.decode('utf-8').strip())

    #format identifier string in preparation to send it to POSSE
    posse_string = "{data} | {identifier_name}".format(data = data, identifier_name = split_identifier_name)
    print(posse_string)
    process = subprocess.Popen(['../POSSE/Scripts/mainParser.pl', 'A', posse_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    print("posse: " + out.decode('utf-8').strip())

    process = subprocess.Popen(['java', '-mx3g', '-cp',
        '../stanford-postagger-2018-10-16/stanford-postagger.jar:','edu.stanford.nlp.tagger.maxent.MaxentTagger', '-model', '../stanford-postagger-2018-10-16/models/english-bidirectional-distsim.tagger'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    process.stdin.write('asd'.encode('utf-8'))
    out, err = process.communicate()
    print("stanford: " + out.decode('utf-8').strip())

def categorize(key_swum, key_posse, key_stanford):
    #DTCP or RFCP
    #select * from training_set_conj order by random()
    swum = {'D':0, 'DT':1, 'FAILURE':2, 'N':3, 'NM':4, 'P':5, 'PR':6, 'PRE':7, 'V':8}
    posse = {'DT':0, 'FAILURE':1, 'N':2, 'NM':3, 'P':4, 'PR':5, 'V':6}
    stanford = {'CJ':0, 'D':1, 'DT':2, 'FAILURE':3, 'N':4, 'NM':5, 'NPL':6, 'P':7, 'PR':8, 'V':9, 'VBD':10, 'VBG':11, 'VBN':12, 'VBP':13, 'VBZ':14, 'VM':15}

    #DTCA or RFCA
    #select * from training_set_conj_other order by random()
    # swum = {'D':0, 'FAILURE':1, 'N':2, 'NM':3, 'OTHER':4, 'P':5, 'PRE':6, 'V':7, 'PR':8}
    # posse = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'V':5}
    # stanford = {'D':0, 'FAILURE':1, 'N':2, 'NM':3, 'NPL':4, 'OTHER':5, 'P':6, 'V':7, 'VBD':8, 'VBG':9, 'VBN':10, 'VBP':11, 'VBZ':12}

    #DTNP or RFNP
    #select * from training_set_norm order by random()
    # swum = {'D':0, 'DT':1, 'FAILURE':2, 'N':3, 'NM':4, 'P':5, 'PR':6, 'PRE':7, 'V':8}
    # posse = {'DT':0, 'FAILURE':1, 'N':2, 'NM':3, 'P':4, 'PR':5, 'V':6}
    # stanford = {'CJ':0, 'D':1, 'DT':2, 'N':3, 'NM':4, 'NPL':5, 'P':6, 'PR':7, 'V':8, 'VM':9, 'FAILURE':10}

    #DTNA or RFNA
    # #select * from training_set_norm_other order by random()
    # swum = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'PRE':5, 'V':6, 'PR':7}
    # posse = {'FAILURE':0, 'N':1, 'NM':2, 'OTHER':3, 'P':4, 'V':5}
    # stanford = {'N':0, 'NM':1, 'NPL':2, 'OTHER':3, 'P':4, 'V':5,'FAILURE':6}

    return swum.get(key_swum), posse.get(key_posse), stanford.get(key_stanford)


def annotate_word(swum_tag, posse_tag, stanford_tag, normalized_length, code_context):
    input_model = 'models/model_DecisionTreeClassifier_training_set_conj.pkl'        #DTCP
    #input_model = 'models/model_RandomForestClassifier_training_set_conj.pkl'       #RFCP
    #input_model = 'models/model_DecisionTreeClassifier_training_set_conj_other.pkl' #DTCA
    #input_model = 'models/model_RandomForestClassifier_training_set_conj_other.pkl' #RFCA
    #input_model = 'models/model_DecisionTreeClassifier_training_set_norm.pkl'       #DTNP
    #input_model = 'models/model_RandomForestClassifier_training_set_norm.pkl'       #RFNP
    #input_model = 'models/model_DecisionTreeClassifier_training_set_norm_other.pkl' #DTNA
    #input_model = 'models/model_RandomForestClassifier_training_set_norm_other.pkl' #RFNA

    # if len(sys.argv) < 2:
    #     print("Syntax: python3 model_classification.py [model]")
    #     quit()
    swum, posse, stanford = categorize(swum_tag, posse_tag, stanford_tag)

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

def read_from_cmd_line():
    run_external_taggers(sys.argv[1])
    print("IDENTIFIER,GRAMMAR_PATTERN,WORD,SWUM,POSSE,STANFORD,CORRECT,PREDICTION,MATCH,SYSTEM,CONTEXT,IDENT", file=open("predictions.csv", "a"))
    # result = annotate_word(swum_tag, posse_tag, stanford_tag, normalized_length, code_context)
    # print("{identifier},{pattern},{word},{swum},{posse},{stanford},{correct},{prediction},{agreement},{system_name},{context},{ident}"
    # .format(identifier=(actual_identifier),word=(actual_word),pattern=(actual_pattern),swum=swum_tag, 
    # posse=posse_tag, stanford=stanford_tag, correct=correct_tag, prediction=result, agreement=(correct_tag==result),
    # system_name=system, context=code_context, ident=ident), file=open("predictions.csv", "a"))

def read_from_database():
    input_file = 'test_data/ensemble_test_db.db'
    sql_statement = "select * from testing_set_conj"         #DTCP or RFCP
    # sql_statement = "select * from testing_set_conj_other" #DTCA or RFCA
    # sql_statement = "select * from testing_set_norm"       #DTNP OR RFNP
    # sql_statement = "select * from testing_set_norm_other" #DTNO OR RFNO
    connection = sqlite3.connect(input_file)

    df_input = pd.read_sql_query(sql_statement, connection)
    print(" --  --  --  -- Read " + str(len(df_input)) + " input rows --  --  --  -- ")
    print("IDENTIFIER,GRAMMAR_PATTERN,WORD,SWUM,POSSE,STANFORD,CORRECT,PREDICTION,MATCH,SYSTEM,CONTEXT,IDENT", file=open("predictions.csv", "a"))
    for i, row in df_input.iterrows():
        print(i)
        actual_word = row['WORD']
        actual_identifier = row['IDENTIFIER']
        actual_pattern  = row['GRAMMAR_PATTERN']
        swum_tag = row['SWUM_TAG']
        posse_tag = row['POSSE_TAG']
        stanford_tag = row['STANFORD_TAG']
        normalized_length = row['NORMALIZED_POSITION']
        code_context = row['CONTEXT']
        correct_tag = row['CORRECT_TAG']
        system = row['SYSTEM']
        ident = row['NUM']
        result = annotate_word(swum_tag, posse_tag, stanford_tag, normalized_length, code_context)
        print("{identifier},{pattern},{word},{swum},{posse},{stanford},{correct},{prediction},{agreement},{system_name},{context},{ident}"
        .format(identifier=(actual_identifier),word=(actual_word),pattern=(actual_pattern),swum=swum_tag, 
        posse=posse_tag, stanford=stanford_tag, correct=correct_tag, prediction=result, agreement=(correct_tag==result),
        system_name=system, context=code_context, ident=ident), file=open("predictions.csv", "a"))


read_from_cmd_line()