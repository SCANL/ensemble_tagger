import csv, sys, subprocess, os

with open(sys.argv[1], "r") as identifier_file:
    lines = identifier_file.readlines()
    count = 0
    for line in lines:
        with open('inputs/ident'+str(count), 'w') as singleIdent:
            singleIdent.write(line)
            count = count + 1

with open(sys.argv[1]+"_individual",'a') as outfile:
    for file in os.listdir('inputs'):
        print(file)
        subprocess.call(["./stanford-postagger.sh", "models/english-bidirectional-distsim.tagger", "inputs/"+file], stdout=outfile)