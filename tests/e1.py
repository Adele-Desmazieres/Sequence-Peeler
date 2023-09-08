import sys


def no_three_same_letters(sequences) :
    c = 0
    for specie,seq in sequences.items() :
        for i in range(len(seq) - 2) :
            if seq[i] == seq[i+1] and seq[i+1] == seq[i+2] :
                c += 1
                if c >= 3 :
                    raise Exception("Error : three times three same pair of nucleotides in file. ")
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
    print("This program raises an exception on a triple reapeat of 2 nucleotides")
    filename = sys.argv[1]
    sequences = parsing(filename)
    print(sequences)
    no_three_same_letters(sequences)
    print("Done.")

