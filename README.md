# Project: Genome Fuzzing

*Status: in developpment*

## Description

This is a bioinformatic tool that founds the minimal input of fasta files for a specified command line giving a specified output. It can find one or many fragments of sequences that cause an error or any other output. This allows the user to automatically isolate the problematic nucleotides instead of searching by hand. 

You have a commande line that does prolonged operations on a fasta file, and returns something. This program will run the command multiple times on reduced versions of the fasta file, to isolate the sub sequences that give the specified output. 

See [Wiki.md](Wiki.md) to know more about the implementation. 


## Installation

Download the code from [Github](https://github.com/Adele-Desmazieres/Pasteur-Genome-Fuzzing). 

Python3 is required. 

## Usage

### Reducing one fasta file (option -f)

To reduce one fasta file, you have to specify the fasta input file, the command line and the desired returncode. The path in the command line referencing the input file is specified with the filename positional argument. The paths to output files have to be identified with the -o flag. The other paths should be **absolute paths**. 

Run this in your console, from the "Code" directory: 

```sh
$ python3 minimise.py 
    <path/to/inputfile.fasta> 
    <"command line"> 
    -r <desired value of returncode>
    -f
```

For example: 
```sh
$ python3 minimise.py 
    ../Data/example.fasta 
    "python3 /path/to/Data/executable.py ../Data/example.fasta" 
    -r 1
    -f
```

### Reducing multiple fasta files (without -f)

A file of files (fof) is a textual file that contains a list of absolute paths to other files. 
If your command line uses a file of fasta files as input, run this in your console :

```sh
$ python3 minimise.py 
    <path/to/fof.txt> 
    <"command line"> 
    -r <value of desired returncode>
```

For example: 
```sh
$ python3 minimise.py 
    ../Data/fof.txt 
    "python3 /path/to/Data/executable.py ../Data/fof.txt" 
    -r 1
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


### Options

You have to specify at least one of these options: the desired return code (-r), standard output (-u) or standard error (-e). The program will check for equality of the return code, and for the presence of the desired output/error inside the actual output/error message. You can specify multiple of them, to check that every condition is met. 

Run this to print the options of the program:
```sh
$ python3 minimise.py -h
```

You can specify some output files of the command to be copy-pasted in the same directory as input files with -o:
```sh
$ python3 Code/minimise.py
    Tests/t2.fasta 
    "python3 e1.py t2.fasta out.txt" 
    -r 1 -f -o out.txt
```


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

## Author

Adèle DESMAZIERES

Contact: adesmaz.pro@gmail.com

## Licence

GNU AFFERO, GPL3

Licence change request : adesmaz.pro@gmail.com