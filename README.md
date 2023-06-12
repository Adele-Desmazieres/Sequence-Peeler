# Project : Genome Fuzzing

Status : in developpment

## Description

This is a bioinformatic tool that founds the minimal input for a specified command line returning a specified output. It can find one or many fragments of sequences from a fasta file that causes an error or any other output. This allows the user to automatically isolate the problematic nucleotides instead of searching by hand. 

## Installation



## Usage

In your console in Code directory, you should run : 

```sh
$ python3 minimiser.py <inputname.fasta> <"command line with ../tmp/tmp.fasta instead of the inputname.fasta"> <returncode desired>
```

For example : 
```sh
$ python3 minimise.py ../Data/example.fasta "python3 ../Data/executable.py ../tmp/tmp.fasta" 1
```

## Author

Adèle DESMAZIERES

Contact : adesmaz.pro@gmail.com

## Licence

GNU AFFERO, GPL3