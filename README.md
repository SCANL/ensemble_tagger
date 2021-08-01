# SCANL Ensemble tagger 
This the official release of the SCANL ensemble part-of-speech tagger.

## Cloning the repo
Please clone recursive since we are currently using submodules. This may change in the future.

	git clone --recursive https://github.com/SCANL/ensemble_tagger.git

## Setup and Run
You will need **python3** installed. We will explicitly use the **python3** command below but, of course, if your environment is configured to use python3 by default, you do not need to. We have also only tested this on **Ubuntu 18**. It most likely works on all recent versions of Ubuntu, but we cannot guarantee it will work in other environments.

**If you are on Windows, the tagger has been confirmed to work on Ubuntu via [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)**

You will also need to install **JDK 15** or later. This page can help - https://www.linuxuprising.com/2020/09/how-to-install-oracle-java-15-on-ubuntu.html

You'll need to install pip3:

``sudo apt-get install python3-pip``

The tagger is split into two parts: 
1. A C++ script which SAX parses a srcML archive and sends identifier names, along with other sorts of static information, to the python script via RESTful HTTP.

2. A Python Flask server that listens to a port for input on a specific route. Once it receives input in the form of an identifier, it runs three external taggers: SWUM, POSSE, and Stanford tagger. It then takes the output of these taggers and feeds it into a machine learning algorithm which decides the final POS tag for each word. 

Before compiling the C++ script, you need to install:
- Cmake (tested on 3.5) - ``sudo apt install cmake``
- libxml2-dev - ``sudo apt install libxml2-dev``

To compile the C++ script, do the following in the root (i.e., ensemble_tagger) directory:
- ``mkdir build``
- ``cd build``
- ``cmake ..``
- ``make -j3`` (-j3 to make it go faster)

Once it is compiled, you should have an executable in the build/bin folder. 

Before running the python server, you need to install required modules. To download all of the required modules, use:

	sudo pip3 install -r requirements.txt

Configure ``PYTHONPATH`` as well:

	export PYTHONPATH=~/path/to/ensemble_tagger/ensemble_tagger_implementation

You will also need to configure POSSE (one of the taggers).  Do the following:
1. Install wordnet-dev
2. Open POSSE/Scripts/getWordNetType.sh
3. You **MAY** need to modify this line, which is at the top of the file: ``/usr/bin/wn $1 | grep "Information available for (noun|verb|adj|adv) $1" | cut -d " " -f4`` by changing the path to wordnet (/usr/bin/wn) to the path on your own system. But usr/bin is the typical installation directory so it is unlikely you need to do this step.
4. set your PERL5LIB path to point to the Scripts folder in POSSE's directory: ``export PERL5LIB=~/path/to/ensemble_tagger/POSSE/Scripts``

Finally, you need to install Spiral, which we use for identifier splitting:

    sudo pip3 install git+https://github.com/casics/spiral.git

Once it is all installed, you should be able to run the server:

    cd ensemble_tagger_implementation
    python3 routes.py [MODEL]

Where MODEL can be one of the below. ``DTCP`` is the default if you do not specify a model:
1. DTCP
2. RFCP
3. DTCA
4. RFCA
5. DTNP
6. RFNP
7. DTNA
8. RFNA

This will start the server, which will listen for identifier names sent via HTTP over the route:

http://127.0.0.1:5000/{identifier_type}/{identifier_name}/{code_context}

Where "code context" is one of:
- FUNCTION
- ATTRIBUTE
- CLASS
- DECLARATION
- PARAMETER

For example:

Tag a declaration: ``http://127.0.0.1:5000/int/numberArray/DECLARATION``

Tag a function: ``http://127.0.0.1:5000/int/GetNumberArray(int* begin, int* end)/FUNCTION``

Tag an class: ``http://127.0.0.1:5000/class/PersonRecord/CLASS``

**You should run the tests the validate that everything is set up at this point**

Make sure you're in the ``ensemble_tagger_implementation`` directory, then run:
```
python -m unittest
```
If the tests do not pass, something above is misconfigured. Re-scan over the instructions carefully. If you can't figure out what's wrong, make an issue.

You can use HTTP to interact with the server and get part-of-speech annotations. This is where the C++ script comes in. You can run this script using the following command, assuming you're in the build folder:

    ./bin/grabidentifiers {srcML file name}

This will run the program that automatically queries the route above using all identifiers in the srcml file. **Make sure the server is running before you run the C++ script**. Otherwise, it won't be able to communicate with the server.

If you are unfamiliar with srcML, [check it out](https://www.srcml.org/). Since the actual tagger is a web server, you don't have to use srcML. You could always use other AST-based code representations, or any other method of obtaining identifier information. If you decide not to use srcML, you should ignore the C++ script.

## Errors?
Please make an issue if you run into errors

# Please Cite the Paper!
1. Christian  D.  Newman,  Michael  J.  Decker,  Reem  S.  AlSuhaibani,  Anthony  Peruma,  Satyajit  Mohapatra,  Tejal  Vishnoi, Marcos Zampieri, Mohamed W. Mkaouer, Timothy J. Sheldon, and Emily Hill, "An Ensemble Approach for Annotating Source Code Identifiers with Part-of-speech Tags," in IEEE Transactions on Software Engineering, doi: 10.1109/TSE.2021.3098242.

# Training set
The data used to train this tagger can be found here: https://github.com/SCANL/datasets/tree/master/ensemble_tagger_training_data

# Interested in our other work?
Find our other research [at our webpage](https://www.scanl.org/) and check out the [Identifier Name Structure Catalogue](https://github.com/SCANL/identifier_name_structure_catalogue)
