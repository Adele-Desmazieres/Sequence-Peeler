import sys

### code from https://stackoverflow.com/a/26209275
def chunks(fd, buffer_size=4096):
    chunk = fd.read(buffer_size)
    while chunk:
        yield chunk
        chunk = fd.read(buffer_size)

def chars(fd, buffersize=4096):
    for chunk in chunks(fd, buffersize):
        for char in chunk:
            yield char
### end of code copy


# create a set of all rotations of the pattern
# pattern rotations are hash of string if hashing is True
# else they are lists of chars
def rotation_set(pattern, hashing=True) :
    pattchars = [*pattern]
    patts = set()
    tmp = pattchars.copy()

    for i in range(len(pattern)) :
        tmp = pattchars[i:] + pattchars[:i]
        s = ''.join(tmp)
        
        if hashing :
            patts.add(hash(s))
        else :
            patts.add(s)
    
    return patts
    

# raise an exception if the pattern is in the fasta file
def matching(filename, pattern) :

    # prepare the reading frame
    n = len(pattern)
    pointer = 0
    frame = [''] * n
    
    # prepare the list of pattern rotations
    patts = rotation_set(pattern, True)
    
    with open(filename, 'r') as fd :
        
        for c in chars(fd) :
            
            if c == '\n' : # ignore breaklines
                continue
                
            frame[pointer] = c
            s = ''.join(frame)
            h = hash(s)
        
            if h in patts :
                reordered_s = ''.join(frame[pointer+1:] + frame[:pointer+1])
                if reordered_s == pattern :
                    raise Exception(pattern + " found in file.")
                
            pointer = (pointer + 1) % n


if __name__ == '__main__' :
    filename = sys.argv[1]
    #pattern = "ATCG"
    pattern = "TGTTTTGGCGGAAGAGACATCGATAAGTAAGCTTGATAGCAGATTAAATCGACAGGTCATAACGGGACGTGTTGATAAAACAGAATTTGCCTGGCGGCC"
    matching(filename, pattern)
    print("Done.")

