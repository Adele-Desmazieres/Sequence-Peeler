# Project : Sequence Peeler

*Status: in developpment*

## Description

seqpeel is a tool to help bioinfo developers to extract minimal examples (minimal set of small sequences) that produce a certain software behavious.
For example, if your software is ending with an error code, seqpeel will reduce your input file(s) until the bug disapears.
It will then return the last input the triggered the error code.

Both software return code or terminal outputs can be used to trigger the sequence peeler.
The peeling process is done by recursive calls of the software with dichotomic-like reductions of the input(s).

See [Wiki.md](Wiki/Wiki.md) for more information on the algorithmic side.


## Installation

Download the code from [Github](https://github.com/Adele-Desmazieres/Pasteur-Genome-Fuzzing). 

Python3 is required. 

## Usage

3 hooks can be used to track a behavior: The program return code, stdout, stderr (or combinations of them)
The return code can be tracked using the `-r <code>` option, stdout with `-u <text-to-track>` and stderr with `-e <text-to-track>`.
These options can be used if you are peeling one file or a set of files.


### Reducing one fasta file

To reduce one fasta file, you have to specify the fasta input file, the command line and the desired returncode. The path in the command line referencing the input file is specified with the filename positional argument. The paths to output files have to be identified with the -o flag. The other paths should be **absolute paths**. 

The minimal command must be:
```sh
    python3 minimise.py \
      -f <path/to/inputfile.fasta> \
      -c <"command line that raise the behavious of interest"> \
      -o <list of output files in the command> \
      [-r <desired value of returncode>] [-u <stdout text>] [-e <stderr text>] # pick at least one
```


An example where we suppose that we are tracking a segmentation fault on stderr that is raised by the following command:
```bash
	myprogram --input mydata.fasta --uselessval 3 --output out.txt --stats stats.txt
```

In this command we want to peel `mydata.fasta` such as the segmentation fault is still raised.
`out.txt` and `stats.txt` must be considered as outputs because they are generated at each execution of the program.

Corresponding command example: 
```bash
    python3 minimise.py \
      -f mydata.fasta \
      -c "myprogram --input mydata.fasta --uselessval 3 --output out.txt --stats stats.txt" \
      -o out.txt stats.txt \
      -e "segmentation fault"
```

### Reducing multiple files

If you want to reduce a set of fasta files, you must indicate the file list in a file of files.
Then you have to use the `-m` option to give the fof to seqpeel.

Command:
```bash
    python3 minimise.py \
      -m <path/to/fileoffiles.txt> \
      -c <"command line that raise the behavious of interest"> \
      -o <list of output files in the command> \
      [-r <desired value of returncode>] [-u <stdout text>] [-e <stderr text>] # pick at least one
```

Modified command line example:
```bash
    myprogram --R1 mydata_R1.fasta --R2 mydata_R2.fasta --uselessval 3 --output out.txt --stats stats.txt
```

Peeling the example: 
```sh
    python3 minimise.py \
      -m fof.txt \
      -c "myprogram --R1 mydata_R1.fasta --R2 mydata_R2.fasta --uselessval 3 --output out.txt --stats stats.txt" \
      -o out.txt stats.txt \
      -e "segmentation fault"
```

`fof.txt`
```
    mydata_R1.fasta
    mydata_R2.fasta
```


### Results

The resulting files will be created in a "Result" directory (removing any previous one). The file of files will contain the name of the resulting fasta files. They will contain the resulting minimised sequences. Each input / output file will be named with its original name, or with a number added at the end if another file already has the same name. 

For example, when running from the Code directory:
```sh
$ python3 minimise.py 
    ../Tests/fof3.txt 
    "python3 /path/to/Tests/exe-fof.py ../Tests/fof3.txt" 
    -r 1 
```

It will make a "Results" directory containing the files fof3.txt, t4.fasta and t4_1.fasta. 



## Limits

This program will always find a minimal exemple of sequences causing the desired output, except in the following case. If two fragments of the same sequence provoque the output, the program may return them separatly under two sequences, or it may returns them together with all the unnecessary nucleotids in between. 


## Tests

To run the tests, run from the Code directory:

```sh
python3 functionnal_tests.py /absolute/path/to/Tests
```

To only print the commands used in the tests, run this:

```sh
python3 functionnal_tests.py /absolute/path/to/Tests -n
```

## Authors

Adèle DESMAZIERES
Contact: adesmaz.pro@gmail.com

Yoann DUFRESNE
Contact: yoann.dufresne@pasteur.fr

## Licence

GNU AFFERO, GPL3

Licence change request is possible by contacting : adesmaz.pro@gmail.com, yoann.dufresne@pasteur.fr