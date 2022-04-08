from ensemble_functions import Annotate_word, Run_external_taggers
from process_features import Calculate_normalized_length, Add_code_context
import logging, os
root_logger = logging.getLogger(__name__)
from flask import Flask

app = Flask(__name__)
@app.route('/<identifier_type>/<identifier_name>/<identifier_context>')
def listen(identifier_type, identifier_name, identifier_context):
    root_logger.info("INPUT: {ident_type} {ident_name} {ident_context}".format(ident_type=identifier_type, ident_name=identifier_name, ident_context=identifier_context))
    ensemble_input = Run_external_taggers(identifier_type + ' ' + identifier_name, identifier_context)
    ensemble_input = Calculate_normalized_length(ensemble_input)
    ensemble_input = Add_code_context(ensemble_input,identifier_context)
    
    output = []
    for key, value in ensemble_input.items():
        result = Annotate_word(value[0], value[1], value[2], value[3].value)
        #output.append("{identifier},{word},{swum},{posse},{stanford},{prediction}"
        #.format(identifier=(identifier_name),word=(key),swum=value[0], posse=value[1], stanford=value[2], prediction=result))
        output.append("{word}|{prediction}".format(word=(key[:-1]),prediction=result))
    output_str = ','.join(output)
    return str(output_str)


class MSG_COLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    if 'PERL5LIB' not in os.environ or os.environ.get('PERL5LIB') == '':
        print(f"{MSG_COLORS.FAIL}**** Warning: PERL5LIB not set; accuracy of the tagger may be compromised.****{MSG_COLORS.ENDC}")
    if 'PYTHONPATH' not in os.environ or os.environ.get('PYTHONPATH') == '':
        print(f"{MSG_COLORS.FAIL}**** Warning: PYTHONPATH not set; if something isn't working, try setting PYTHONPATH****{MSG_COLORS.ENDC}")
    app.run(host='0.0.0.0')