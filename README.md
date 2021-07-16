


# SCANL Ensemble tagger 
This the official release of the SCANL ensemble part-of-speech tagger.

## Cloning the repo
Please clone recursive since we are currently using submodules. This may change in the future.

	git clone --recursive https://github.com/SCANL/ensemble_tagger.git

## Setup and Run
You will need **python3** installed. We will explicitly use the **python3** command below but, of course, if your environment is configured to use python3 by default, you do not need to. We have also only tested this on **Ubuntu 18**. It most likely works on all recent versions of Ubuntu, but we cannot guarantee it will work in other environments.

You will also need to install **JDK 15** or later.

The tagger is split into two parts: 
1. A C++ script which SAX parses a srcML archive and sends identifier names, along with other sorts of static information, to the python script via RESTful HTTP.

2. A Python Flask server that listens to a port for input on a specific route. Once it receives input in the form of an identifier, it runs three external taggers: SWUM, POSSE, and Stanford tagger. It then takes the output of these taggers and feeds it into a machine learning algorithm which decides the final POS tag for each word. 

Before compiling the C++ script, you need to install:
- Cmake (tested on 3.5)
- libxml2-dev

To compile the C++ script, do the following in the root (i.e., ensemble_tagger) directory:
- mkdir build
- cd build
- cmake ..
- make (consider using -j3 to make it go faster)

Once it is compiled, you should have an executable in the build/bin folder. 

Before running the python server, you need to install required modules. To download all of the required modules, use:

    pip3 install -r requirements.txt

You will then need to configure flask, so that it knows how to run the server:

    export FLASK_APP=model_classification.py

You will also need to configure POSSE (one of the taggers).  Do the following:
1. Install wordnet-dev
2. Open POSSE/Scripts/getWordNetType.sh
3. You **MAY** need to modify this line, which is at the top of the file: `/usr/bin/wn $1 | grep "Information available for (noun|verb|adj|adv) $1" | cut -d " " -f4` by changing the path to wordnet (/usr/bin/wn) to the path on your own system. But usr/bin is the typical installation directory so it is unlikely you need to do this step.
4. set your PERL5LIB path to point to the Scripts folder in POSSE's directory: `export PERL5LIB=/path/from/root/ensemble_tagger/POSSE/Scripts`

Finally, you need to install Spiral, which we use for identifier splitting:

    sudo pip3 install git+https://github.com/casics/spiral.git

Once it is all installed, you should be able to run the server:

    flask run

This will start the server, which will listen for identifier names sent via HTTP over the route:

http://127.0.0.1:5000/{identifier_type}/{identifier_name}/{code_context}

Where "code context" is one of:
- FUNCTION
- ATTRIBUTE
- CLASS
- DECLARATION
- PARAMETER

This is where the C++ script comes in. You can run this script using the following command, assuming you're in the build folder:

    ./bin/grabidentifiers {srcML file name}

This will run the program that automatically queries the route above using all identifiers in the srcml file. **Make sure the server is running before you run the C++ script**. Otherwise, it won't be able to communicate with the server.

## Configure the script
### Choose a model
You can configure the yourself by commenting out various parts of it and uncommenting others. There is a comment after each .pkl file, telling you which configuration each model represents. Uncomment the one you want to run, comment the ones you don't want to run. The code looks like this:

    input_model = 'models/model_DecisionTreeClassifier_training_set_conj.pkl'  #DTCP

### Choose a tagset
You will also need to comment/uncomment the tagsets at the top depending on which model you are using.  You can look at the comment above each tagset to see which two configurations each one should be used for. Each tagset is used for one decision tree configuration and one random forest configuration, so two configurations in total.

## Errors?
Please make an issue if you run into errors

# Please Cite the Paper!
(COMING SOON)

# Training set
The data used to train this tagger can be found here: https://github.com/SCANL/datasets/tree/master/ensemble_tagger_training_data

# Interested in our other work?
Find our other research here: https://www.scanl.org/
