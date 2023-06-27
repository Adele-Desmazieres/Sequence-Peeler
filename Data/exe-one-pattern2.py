import sys

# copied code from https://stackoverflow.com/a/26209275
def chunks(filename, buffer_size=4096):
    with open(filename, "rb") as fp:
        chunk = fp.read(buffer_size)
        while chunk:
            yield chunk
            chunk = fp.read(buffer_size)

def chars(filename, buffersize=4096):
    for chunk in chunks(filename, buffersize):
        for char in chunk:
            yield char


def matching(filename, pattern) :

    try :
        with open(filename, 'r') as f :
            
            # prepare the reading frame
            n = len(pattern)
            pointer = 0
            frame = [""] * n

            # create a list of all rotations of the pattern as lists of chars
            # TODO transformer ca en set d'entiers hachant les strings des rotations
            pattchars = [*pattern]
            patts = list()
            tmp = pattchars.copy()
            for i in range(n) :
                tmp = pattchars[i:] + pattchars[:i]
                #patts.append(pattchars)
                patts.append(''.join(tmp))

            for c in chars(filename) :
                frame[pointer] = chr(c)
                #print(frame)
                s = ''.join(frame)
                if s in patts :
                    reordered_s = ''.join(frame[pointer+1:] + frame[:pointer+1])
                    if reordered_s == pattern :
                        raise Exception(pattern + " found in file.")
                pointer = (pointer + 1) % n

    except IOError :
        print("Fichier introuvable.")


if __name__ == '__main__' :
    filename = sys.argv[1]
    pattern = "CAACTAGTTGCATCATACAACTAATAAACGTGGTGAATCCAATTGTCGAGATTTATTTTTTATAAAATTATCCTAAGTAAACAGAAGG"
    #pattern = "ATCG"
    matching(filename, pattern)
    print("Done.")

