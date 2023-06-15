# Project : Genome Fuzzing

*Status : in developpment*

## Description

This is a bioinformatic tool that founds the minimal input for a specified command line returning a specified output. It can find one or many fragments of sequences from a fasta file that causes an error or any other output. This allows the user to automatically isolate the problematic nucleotides instead of searching by hand. 

## Installation

Download the code from [Github](https://github.com/Adele-Desmazieres/Pasteur-Genome-Fuzzing). 

Python3 is required. 

## Usage

In your console from the Code directory you can run : 

```sh
$ python3 minimiser.py 
    <path/to/inputfile.fasta> 
    <"command line with tmp.fasta instead of the path/to/inputfile.fasta"> 
    <value of desired returncode>
```

For example : 
```sh
$ python3 minimise.py 
    ../Data/example.fasta 
    "python3 ../Data/executable.py tmp.fasta" 
    1
```

To print the options of the program you can run :
```sh
$ python3 minimise.py -h
```

You can specify the directory where the given command line should be run with the option -w. If not specified, it will be executed in the current directory. For example, from the Code directory :
```sh
$ python3 minimise.py 
    -w ../Data 
    ../Data/example.fasta 
    "python3 executable.py tmp.fasta" 
    1
```

You can specify the name and destination of the output file with the option -d. If not specified, the output file will be created in the working directory with the name "minimised.fasta". The output file will truncate any existing file at same path with same name. For example, from the Code directory :
```sh
$ python3 minimise.py 
    -d ../Results/minimised.fasta 
    ../Data/example.fasta 
    "python3 ../Data/executable.py tmp.fasta" 
    1
```

You can also run the program from any directory and combine multiples options, like so from the root of this project :
```sh
$ python3 Code/minimise.py -v
    -d Results/minimised.fasta 
    -w Tests Tests/t2.fasta 
    "python3 e1.py tmp.fasta" 
    1
```


## Author

Adèle DESMAZIERES

Contact : adesmaz.pro@gmail.com

## Licence

GNU AFFERO, GPL3

Licence change request : adesmaz.pro@gmail.com