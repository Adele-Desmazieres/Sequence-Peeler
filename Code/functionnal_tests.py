import subprocess
import filecmp

IN_EXE_OUT = [ \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 ../Tests/e0.py tmp.fasta\" 1", \
        "../Tests/t0_e0.fasta"), \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 ../Tests/e1.py tmp.fasta\" 1", \
        "../Tests/t0_e1.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 ../Tests/e1.py tmp.fasta\" 1", \
        "../Tests/t1_e1.fasta"), \
    ( \
        "../Tests/t2.fasta", \
        "\"python3 ../Tests/e1.py tmp.fasta\" 1", \
        "../Tests/t2_e1.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 ../Tests/e2.py tmp.fasta\" 1", \
        "../Tests/t1_e2.fasta"), \
    ( \
        "../Tests/t0.fasta", \
        "\"python3 ../Tests/e3.py tmp.fasta\" 1", \
        "../Tests/t0_e3.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 ../Tests/e3.py tmp.fasta\" 1", \
        "../Tests/t1_e3.fasta"), \
    ( \
        "../Tests/t1.fasta", \
        "\"python3 ../Tests/e4.py tmp.fasta\" 1", \
        "../Tests/t1_e4.fasta") \
]

OKGREEN = '\033[92m'
WARNING = '\033[93m'
ENDC = '\033[0m'

def test_all(cmdbeginning) :
    c = 0
    for (input, exe, output) in IN_EXE_OUT :
        
        cmdline = cmdbeginning + " " + input + " " + exe
        print(cmdline)
        subprocess.run(cmdline, shell=True)

        if filecmp.cmp("../Results/minimised.fasta", output) :
            print("Test réussi.\n")
            c += 1
        else : 
            print(WARNING + "Test raté." + ENDC + "\n")
    
    if c == len(IN_EXE_OUT) :
        print(OKGREEN + str(c) + "/" + str(len(IN_EXE_OUT)) + " tests réussis." + ENDC)
        return True
    else :
        print(WARNING + str(c) + "/" + str(len(IN_EXE_OUT)) + " tests réussis." + ENDC)
        return False


if __name__=='__main__' :
    cmdbeginning = "python3 minimise.py"
    test_all(cmdbeginning)

    


