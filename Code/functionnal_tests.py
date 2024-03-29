#!/bin/python3

import subprocess
import filecmp
import sys
from pathlib import Path

ABSOLUTE_PATH_TO_EXE = "/home/benoit/Documents/Stage-2023-Pasteur/Pasteur-Genome-Fuzzing/Tests/"
#ABSOLUTE_PATH_TO_EXE = "/home/yoshihiro/Documents/Pasteur-Genome-Fuzzing/Tests/"

def make_in_exe_out() :
    in_exe_out = [ \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e0.py ../Tests/t0.fasta\" -r 1 -f", \
        "../Tests/t0_e0.fasta"), \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e1.py ../Tests/t0.fasta\" -r 1 -f", \
        "../Tests/t0_e1.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e1.py ../Tests/t1.fasta\" -r 1 -f", \
        "../Tests/t1_e1.fasta"), \
    ( \
        "../Tests/t2.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e1.py ../Tests/t2.fasta\" -r 1 -f", \
        "../Tests/t2_e1.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e2.py ../Tests/t1.fasta\" -r 1 -f", \
        "../Tests/t1_e2.fasta"), \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e3.py ../Tests/t0.fasta\" -r 1 -f", \
        "../Tests/t0_e3.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e3.py ../Tests/t1.fasta\" -r 1 -f", \
        "../Tests/t1_e3.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "e4.py ../Tests/t1.fasta\" -r 1 -f", \
        "../Tests/t1_e4.fasta") \
    ]
    return in_exe_out

def make_fof_ex_out() :
    fof_exe_out = [ \
    ( \
        "../Tests/fof0.txt", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "exe-fof.py ../Tests/fof0.txt\" -r 1", \
        [("../Tests/fof0_expected.txt", "Results/fof0.txt")]), \
    ( \
        "../Tests/fof1.txt", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "exe-fof.py ../Tests/fof1.txt\" -r 1", \
        [("../Tests/fof1_expected.txt", "Results/fof1.txt"),
         ("../Tests/t3_fof1_expected.fasta", "Results/t3.fasta"), 
         ("../Tests/t4_fof1_expected.fasta", "Results/t4.fasta")
        ]), \
    ( \
        "../Tests/fof2.txt", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "exe-fof.py ../Tests/fof2.txt\" -r 1", \
        [("../Tests/fof2_expected.txt", "Results/fof2.txt"),
         ("../Tests/t5_fof2_expected.fasta", "Results/t5.fasta"), 
         ("../Tests/t1_fof2_expected.fasta", "Results/t1.fasta")
        ]), \
    ( \
        "../Tests/fof3.txt", \
        "\"python3 " + ABSOLUTE_PATH_TO_EXE + "exe-fof.py ../Tests/fof3.txt\" -r 1", \
        [("../Tests/fof3_expected.txt", "Results/fof3.txt"),
         ("../Tests/t4_fof3_expected.fasta", "Results/t4.fasta"), 
         ("../Tests/Toto/t4_fof3_expected.fasta", "Results/t4_1.fasta")
        ]) \
    ]
    return fof_exe_out

EXTENSION = "_result"
OKGREEN = '\033[92m'
WARNING = '\033[93m'
ENDC = '\033[0m'


class TestCmdData :

    def __init__(self, input_file, cmd, comparison_files) :
        self.input_file = input_file # string
        self.cmd = cmd # string
        self.comparison_files = comparison_files # list of couples of string ("expected.fasta", "result.fasta")
    
    def buildcmd(self, cmdbegin) :
        return cmdbegin + " " + self.input_file + " " + self.cmd
    
    def run(self, cmdbegin) :
        cmdline = self.buildcmd(cmdbegin)
        print(cmdline)
        subprocess.run(cmdline, shell=True)

    def output_correct(self) :
        for (expected, result) in self.comparison_files :
            if not Path(result).is_file() :
                return False
            if not filecmp.cmp(expected, result) :
                return False
        return True


def test_fof(cmdbegin, fof_exe_out) :
    c = 0

    for (input, exe, expectedoutput) in fof_exe_out :
        t = TestCmdData(input, exe, expectedoutput)
        t.run(cmdbegin)

        if t.output_correct() :
            print("Test réussi.\n")
            c += 1
        else : 
            print(WARNING + "Test raté." + ENDC + "\n")
    
    if c == len(fof_exe_out) :
        print(OKGREEN + str(c) + "/" + str(len(fof_exe_out)) + " tests réussis.\n" + ENDC)
        return True
    else :
        print(WARNING + str(c) + "/" + str(len(fof_exe_out)) + " tests réussis.\n" + ENDC)
        return False


def test_fasta(cmdbegin, in_exe_out) :
    c = 0
    for (input, exe, expectedoutput) in in_exe_out :
        
        cmdline = cmdbegin + " " + input + " " + exe
        print(cmdline)
        subprocess.run(cmdline, shell=True)

        p = Path(input)
        #realoutput = str(p.parent) + "/" + p.stem + EXTENSION + p.suffix
        realoutput = "Results/" + p.name
        
        if filecmp.cmp(expectedoutput, realoutput) :
            print("Test réussi.\n")
            c += 1
        else : 
            print(WARNING + "Test raté." + ENDC + "\n")
    
    if c == len(in_exe_out) :
        print(OKGREEN + str(c) + "/" + str(len(in_exe_out)) + " tests réussis.\n" + ENDC)
        return True
    else :
        print(WARNING + str(c) + "/" + str(len(in_exe_out)) + " tests réussis.\n" + ENDC)
        return False


def printing_cmd(cmdbegin, in_exe_out, fof_exe_out) :
    for (input, exe, expectedoutput) in in_exe_out :
        cmdline = cmdbegin + " " + input + " " + exe
        print(cmdline)
        print()
    
    for (input, exe, expectedoutput) in fof_exe_out :
        t = TestCmdData(input, exe, expectedoutput)
        print(t.buildcmd(cmdbegin))
        print()



if __name__=='__main__' :
    cmdbegin = "./minimise.py"

    argc = len(sys.argv)

    if argc >= 2 :
        ABSOLUTE_PATH_TO_EXE = sys.argv[1]
        ABSOLUTE_PATH_TO_EXE = ABSOLUTE_PATH_TO_EXE + "/" if ABSOLUTE_PATH_TO_EXE[-1] != "/" else ABSOLUTE_PATH_TO_EXE
        in_exe_out = make_in_exe_out()
        fof_exe_out = make_fof_ex_out()

        if argc >= 3 and sys.argv[2] == "-n" :

                printing_cmd(cmdbegin, in_exe_out, fof_exe_out)
                exit(0)
        
        else :
            
            test_fasta(cmdbegin, in_exe_out)
            test_fof(cmdbegin, fof_exe_out)

    else :
        print("Arguments Error : ./functionnal_tests.py </path/to/Tests> [-n]")
