import sys


def matching(sequences) :
    pattern = "CACACAT"
    for specie,seq in sequences.items() :
        for i in range(len(seq) - len(pattern) + 1) :
            if seq[i:i+len(pattern)] == pattern :
                raise Exception(pattern + " found in file.")
    return 1

# returns the representation of a fasta file by a dictionnary where
# the key is the specie header, and the value is the specie sequence
# for example : {"Fraise":"ATTCG", "Pomme":"GGGGCTC"}
def parsing(filename) :
    try :
        with open(filename, 'r') as f :
            specie = None
            sequences = dict()
            for line in f :
                line = line.strip()
                if len(line) >= 1 : 
                    if line[0] == '>' :
                        specie = line[1:].strip()
                        sequences[specie] = ""
                    elif specie != None : 
                        sequences[specie] += line # concatenate line to the previous string
        return sequences

    except IOError :
        print("Fichier introuvable.")


if __name__ == '__main__' :
    filename = sys.argv[1]
    sequences = parsing(filename)
    matching(sequences)
    print("Done.")

