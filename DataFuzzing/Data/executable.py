import sys
import string


def no_three_same_letters(sequences) :
    for specie,seq in sequences.items() :
        for i in range(len(seq) - 3) :
            if seq[i] == seq[i+1] and seq[i+1] == seq[i+2] :
                raise Exception("Erreur obscure")
    return 1

# renvoie la représentation d'un fichier fasta sous forme d'un dict de header:seq
# avec header en string et seq aussi, par exemple "Fraise":"ATTCGATGTGTGG"
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
                        sequences[specie] += line # concatennation de line avec le string précédent
        return sequences

    except IOError :
        print("Fichier introuvable.")


if __name__ == '__main__' :
    filename = sys.argv[1]
    sequences = parsing(filename)
    print(sequences)
    no_three_same_letters(sequences)
    print("Done.")

