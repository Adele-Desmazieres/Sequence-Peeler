# Project : Genome Fuzzing

## Wiki introduction

This wiki explains in details the algorithms implemented in the project Genome Fuzzing. 

## Principle

This tool looks for the minimal input data that causes a given program to return a given output. The input data is a fasta file containing one or multiple sequences.

### Sequence suppression

First, it suppresses the sequences that are not neccessary to obtain the desired output. A suppressed sequence could also cause the target output, but as it is obtained without it, we don't keep it. To do this, we remove the sequence from the data, and if the given program gives the target output, then we continue without the sequence, otherwise we keep it. 

### Sequence reduction

If we keep the sequence, we have to reduce it to isolate the sub-sequence(s) causing the desired output. We use the dichotomy algorithm to do that : at each step we halve the sequence, and check if each half causes the specified output. 

If one of the two halves replacing the original sequence in the data causes the target output, we keep it. If both of them causes separatly the specified output, we keep one of them at random. In both cases, we continue the dichotomy on the sub-sequence kept. 

If none of them causes de specified output, there are two hypothesis that could explain it : whether we cutted the target sequence in half, or whether there are multiple target sequences on both sides of the cut, which causes the target ouptput only when they are both present. We call them co-factor sequences. 

### Co-factor sequences

To check if we are in the case of co-factor sequences, we temporarly add to the data two separate species with one half of the sequence each, and check if this gives the target output. If it does, we then continue to reduce individually these sequences like any other sequence. 

For now, if one of multiple co-factor sequences is cutted in half, we can't detect it. We treat this case as if it was one target sequence cutted in half, so unnecessary nucleotids will remain in between the co-factor sequences. 

### Target sequence cutted in half

If we aren't in any previous case, it can be explained if we cutted the target sequence in half. So to reduce it to the minimum, we cut some nucleotids at the begining and at the end of the sequence. We use dichotomy to find where is the first nucleotid needed to cause the desired output, and the same is done to find the last one. 

For example, to find the first nucleotid we halve the first half of the sequence to get two quarters of the sequence. If the target output is obtained without the first quarter, we remove it and continue the dichotomy on the second quarter. Else we keep the entire sequence for now and continue the dichotomy on the first quarter. With this method, we are sure to cut out any unnecessary nucleotid. 

## Possible extensions

- use more than one fasta file in input
- parallelize the execution
