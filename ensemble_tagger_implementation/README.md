

# Ensemble tagger sample
This is a usable sample of the ensemble tagger described in our (in-submission) manuscript. A full release is coming!

## Setup and Run
You will need **python3** installed. We will explicitly use the **python3** command below but, of course, if your environment is configured to use python3 by default, you do not need to.

To download all of the required files, use:

    pip3 install -r requirements.txt

Once it is all installed, you should be able to run the script immediately:

    python3 model_classification.py

This will cause the script to begin reading the suplied ensemble_testdb.db file, which contains all data the ensemble needs to apply a part-of-speech annotation.

## Files
The **ensemble_testdb** file is in the test_data directory and contains our test data. This directory also contains a training_set_sample.csv containing a sample of our training set.

The numbers under the **context** feature represent the following categories (number -> category):
1.	attribute
2.	class
3.	declaration
4.	function
5.  parameter

The models (i.e., generating using random forest and decision tree) are all in the models directory. There are 8 of them. Each model is a different configuration, which is explained in the manuscript. By default, the ensemble will use **DTCP** unless you reconfigure it. 

## Reconfiguring the script
### Choose a model
You can configure the yourself by commenting out various parts of it and uncommenting others. There is a comment after each .pkl file on lines 36-43, telling you which configuration each model represents. Uncomment the one you want to run, comment the ones you don't want to run. The code looks like this:

    input_model = 'models/model_DecisionTreeClassifier_training_set_conj.pkl'  #DTCP

### Choose a tagset
You will also need to comment/uncomment the tagsets at the top depending on which model you are using. These are on lines 8 - 30.  You can look at the comment above each tagset to see which two configurations each one should be used for. Each tagset is used for one decision tree configuration and one random forest configuration, so two configurations in total.

### Choose the right test set
The ensemble_testdb file has several configurations of the dataset in it. Each one is meant to be run with a different configuration of the ensemble. There is a comment next to each to let you know which configurations it is meant to work best with. Uncomment the one you want, comment out the ones you do not want.

## Output
The ensemble outputs to a file called **predictions.csv** in the project root directory.

## Errors?
If you are getting low accuracy, something is configured incorrectly. 

## Can I run it on code?
Not yet, unfortunately. We are currently working on a version that works on a  [srcML archive](https://www.srcml.org). The version you see here is just a prototype we are using to evaluate the accuracy of the ensemble.
