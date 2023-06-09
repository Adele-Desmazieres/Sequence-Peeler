# Project: Genome Fuzzing

## Wiki introduction

This wiki explains in detail the algorithms implemented in the project *Genome Fuzzing*. 

## Principle

This tool looks for the minimal input data that causes a given program to return a given output. The input data is a fasta file containing one or multiple sequences.

### Sequence suppression

First, it suppresses the sequences that are not neccessary to obtain the desired output. A suppressed sequence could also cause the target output, but as it is obtained without it, we don't keep it. To do so, we remove the sequence from the data, and if the given program gives the desired output, we continue without the sequence, otherwise we keep it. 

### Sequence reduction

If we keep the sequence, we have to reduce it to isolate the sub-sequence(s) causing the desired output. We use the binary search algorithm to do that: at each step we halve the sequence, and check if each one causes the target output. 

If one of the two halves replacing the original sequence in the data causes the target output, we keep it. If both of them separatly cause the desired output, we keep one of them at random. In both cases, we continue the binary search on the sub-sequence. 

If none of them causes de specified output, there are two possible explanations: either we cut the target sequence in half, or there are multiple target sequences on both sides of the cut, which cause the target output only when they are both present. We call them co-factor sequences. 

### Co-factor sequences

To check if there is co-factor sequences, we temporarily add to the data two separate species with one half of the sequence each, and check if this gives the desired output. If it does, we then continue to reduce these individually like any other sequence. 

For now, if one of multiple co-factor sequences is cut in half, we can not detect it. We treat this case as if it were one target sequence, so unnecessary nucleotides will remain in between the co-factor sequences. 

### Target sequence cutted in half

If no previous case apply, it means that we tried to cut the target sequence in half. To reduce it to the minimum, we cut out some nucleotides at the begining and at the end of the sequence. We use binary search to find where are the first and the last nucleotide needed to cause the desired output.

For example, to find the first nucleotide we halve the first half of the sequence to get two quarters of it. If the desired output is obtained without the first quarter, we remove it and continue the binary search on the second quarter. Else we keep the entire sequence for now and continue the search on the first quarter. With this method, we are sure to cut out any unnecessary nucleotide and not more. 

## Possible extensions

- use more than one fasta file in input
- parallelize the execution
