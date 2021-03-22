## The script for sending multiple get request to FLASK sever to POS tag number of function/method names. 
## Date: March 22nd,2021.
## Developed by Reem Alsuhaibani
## CSV file is the file the contains all the method names that you would like to tag, make sure you have all the three parameters there. 
## Make sure you replace empty cells with quotation marks, otherwise you will error in the sever. 


import csv
import requests

with open('names_for_tagger.csv', 'rt') as dataset:
    dataset_rows = csv.reader(dataset)

    for line in dataset_rows:
        identifier_type = line[0]
        identifier_name = line[1]
        identifier_context = line[2]
        
        try:
            r = requests.get(f'http://127.0.0.1:5000/{identifier_type}/{identifier_name}/{identifier_context}')
            print (r.text)
        except Exception as error:
            print(error)
            continue