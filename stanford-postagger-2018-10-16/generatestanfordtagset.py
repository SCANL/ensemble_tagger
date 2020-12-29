import csv, sys, re, os


def ParseStanford (directory):
    tagset = set()
    for file in os.listdir(directory):
        print(file)
        with open('outputs/'+file, "r") as possefile:
            for line in possefile:
                line = line.split(' ')
                line.pop()
                grammarPattern = str()
                identifier = str()
                for id_pair in line:
                    this_pair = id_pair.split('_')
                    tagset.add(this_pair[1].upper())
    for tag in tagset:
        print(tag)



if __name__ == '__main__':
    ParseStanford(sys.argv[1])