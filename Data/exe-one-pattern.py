import sys
import string


def no_three_same_letters(sequences) :
    for specie,seq in sequences.items() :
        for i in range(len(seq) - 3) :
            if seq[i:i+4] == "ATCG" :
                raise Exception("ATCG found in file.")
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
    print(sequences)
    no_three_same_letters(sequences)
    print("Done.")

