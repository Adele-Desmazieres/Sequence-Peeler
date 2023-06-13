import sys

def are_complement_nucl(n1, n2) :
    if n1 == 'A' and n2 == 'T' :
        return True
    elif n1 == 'T' and n2 == 'A' :
        return True
    elif n1 == 'C' and n2 == 'G' :
        return True
    elif n1 == 'G' and n2 == 'C' :
        return True
    return False


def are_inverse_complement(s1, s2) :
    if len(s1) != len(s2) : 
        return False
    for i in range(len(s1)) :
        if not are_complement_nucl(s1[i], s2[-i-1]) :
            return False
    return True            


def matching(sequences) :
    k = 5
    for specie,seq in sequences.items() :
        for i in range(len(seq) - k) :
            if are_inverse_complement(seq[i:i+k], seq[i+1:i+k+1]) :
                raise Exception("(k+1)mers inverse complement found : " + seq[i:i+k+1])
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
    matching(sequences)
    print("Done.")

