# Project : Genome Fuzzing

Status : in developpment

## Description

This is a bioinformatic tool that founds the minimal input for a specified executable returning a specified output. It can find one or many fragments of sequences from a fasta file that causes an error or any other output, when used as an input in the executable. This allows the user to automatically isolate the problematic nucleotids instead of searching by hand. 

## Installation



## Usage

In your console run : 

```sh
$ python3 minimiser.py <inputname.fasta> <executablename> <returncode>
```

For example : 
```sh
$ python3 minimiser.py ../Data/example.fasta ../Data/dist/exe-one-pattern/exe-one-pattern 1
```

## Author

Adèle DESMAZIERES

Contact : adesmaz.pro@gmail.com

## Licence

GNU AFFERO, GPL3