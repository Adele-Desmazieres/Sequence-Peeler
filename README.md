# Project : Genome Fuzzing

*Status : in developpment*

## Description

This is a bioinformatic tool that founds the minimal input of fasta files for a specified command line returning a specified output. It can find one or many fragments of sequences that causes an error or any other output. This allows the user to automatically isolate the problematic nucleotides instead of searching by hand. 

## Installation

Download the code from [Github](https://github.com/Adele-Desmazieres/Pasteur-Genome-Fuzzing). 

Python3 is required. 

## Usage

### Reducing one fasta file

Run this in your console, from the "Code" directory : 

```sh
$ python3 minimise.py 
    <path/to/inputfile.fasta> 
    <"command line"> 
    -r <value of desired returncode>
    -f
```

For example : 
```sh
$ python3 minimise.py 
    ../Data/example.fasta 
    "python3 ../Data/executable.py ../Data/example.fasta" 
    -r 1
    -f
```

### Reducing multiple fasta files

A file of files (fof) is a textual file that contains a list of absolute paths to other files. 
If your command line uses a file of fasta files as input, run this in your console :

```sh
$ python3 minimise.py 
    <path/to/fof.txt> 
    <"command line"> 
    -r <value of desired returncode>
```

For example : 
```sh
$ python3 minimise.py 
    ../Data/fof.txt 
    "python3 ../Data/executable.py ../Data/fof.txt" 
    -r 1
```

### Options

You have to specify at least one of these options : the desired return code (-r), standard output (-o) or standard error (-e). We will check for equality of the return code, and for the presence of the desired output/error inside the actual output/error message. You can specify multiple of them, to check that every condition is met. 

The output files are created in the same directory as their original version. They will be named with the same name + "_result" + same extension. 

Run this to print the options of the program :
```sh
$ python3 minimise.py -h
```

You can specify the directory where the given command line should be run with the option -w. If not specified, it will be executed in the current directory. For example, from the Code directory :
```sh
$ python3 minimise.py 
    ../Data/example.fasta 
    "python3 executable.py example.fasta" 
    -r 1
    -f
    -w ../Data 
```

You can also run the program from any directory, like so from the root of this project :
```sh
$ python3 Code/minimise.py
    Tests/t2.fasta 
    "python3 e1.py t2.fasta" 
    -r 1
    -f
    -w Tests
```


## Author

Adèle DESMAZIERES

Contact : adesmaz.pro@gmail.com

## Licence

GNU AFFERO, GPL3

Licence change request : adesmaz.pro@gmail.com