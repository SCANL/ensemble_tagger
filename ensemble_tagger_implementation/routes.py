from ensemble_tagger.ensemble_tagger_implementation.model_classification import annotate_word, add_code_context, calculate_normalized_length, run_external_taggers, root_logger
from flask import Flask

app = Flask(__name__)
@app.route('/<identifier_type>/<identifier_name>/<identifier_context>')
def listen(identifier_type, identifier_name, identifier_context):
    root_logger.debug("INPUT: {ident_type} {ident_name} {ident_context}".format(ident_type=identifier_type, ident_name=identifier_name, ident_context=identifier_context))
    ensemble_input = run_external_taggers(identifier_type + ' ' + identifier_name, identifier_context)
    ensemble_input = calculate_normalized_length(ensemble_input)
    ensemble_input = add_code_context(ensemble_input,identifier_context)
    
    output = []
    for key, value in ensemble_input.items():
        result = annotate_word(value[0], value[1], value[2], value[3], value[4].value)
        #output.append("{identifier},{word},{swum},{posse},{stanford},{prediction}"
        #.format(identifier=(identifier_name),word=(key),swum=value[0], posse=value[1], stanford=value[2], prediction=result))
        output.append("{word}|{prediction}".format(word=(key[:-1]),prediction=result))
    output_str = ','.join(output)
    return str(output_str)