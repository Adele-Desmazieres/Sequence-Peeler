import argparse
from time import time
from pathlib import Path
from shutil import rmtree

from seqpeeler.minimise import reduce_all_files, sp_to_files, write_stats


class SpecieData :
    
    def __init__(self, header, begin_seq, end_seq, filename) : # initialise the specie with one seq
        self.header = header # string of the specie name and comments
        self.begin_seq = begin_seq # int, constant
        self.subseqs = [(begin_seq, end_seq)] # int tuple list, variable represents the index of the first char of the seq in the file (included) and the index of the last one (excluded)
        self.filename = filename # string filename
    
    def __str__(self) : # debug function
        s = ">" + self.header + "\n"
        s += str(self.subseqs)
        return s


class CmdArgs :

    def __init__(self, subcmdline, infilename, nofof, outfilesnames, desired_output, verbose) :
        self.subcmdline = subcmdline
        self.infilename = infilename # the name of the fof or the only file of sequences
        self.nofof = nofof
        self.outfilesnames = outfilesnames
        self.desired_output = desired_output
        self.verbose = verbose
        self.seqfilesnames = []
        self.init_seqfilesnames()
        self.fileregister = self.make_fileregister(self.get_all_infiles() + self.outfilesnames)
        self.subcmdline_replaced = self.replace_path_in_cmd(self.get_all_infiles() + self.outfilesnames)
        print(self.fileregister)
        print(self.subcmdline_replaced)
    
    def init_seqfilesnames(self) :
        if self.nofof :
            self.seqfilesnames = [self.infilename]
        else :
            self.seqfilesnames = fof_to_list(self.infilename)

    def get_all_infiles(self) :
        return [self.infilename] if self.nofof else self.seqfilesnames + [self.infilename]
        
    def replace_path_in_cmd(self, files) :
        cmd = self.subcmdline
        for f in files :
            cmd = cmd.replace(f, self.fileregister[f])
        return cmd
    
    # returns the dict of filepath:renamedfile
    # where renamedfile is either the filename or something else if this filename is already used
    def make_fileregister(self, files) :
        fileregister = dict()
        for f in files :
            i = 1
            p = Path(f)
            tmpname = p.name
            while tmpname in fileregister.values() :
                tmpname = p.stem + "_" + str(i) + p.suffix
                i += 1
            fileregister[f] = tmpname
        return fileregister
    
    def save_fileregister(self, filepath) :
        infiles = self.get_all_infiles()
        f = open(filepath, 'w')
        for oldpath,newname in self.fileregister.items() :
            if oldpath in infiles :
                f.write(oldpath + " : " + newname + "\n")
        f.close()


# prepare the argument parser and parses the command line
# returns an argparse.Namespace object
def set_args() :
    parser = argparse.ArgumentParser(prog="Genome Fuzzing")

    # non positionnal arguments
    parser.add_argument('-e', '--stderr', default=None)
    parser.add_argument('-f', '--onefasta', action='store_true')
    parser.add_argument('-o', '--outfilesnames', action='extend', nargs='+', type=str, default=[])
    parser.add_argument('-r', '--returncode', default=None, type=int)
    parser.add_argument('-u', '--stdout', default=None)
    parser.add_argument('-v', '--verbose', action='store_true')

    # positionnal arguments
    parser.add_argument('filename')
    parser.add_argument('cmdline')
    
    args = parser.parse_args()
    if args.returncode is None and args.stdout is None and args.stderr is None :
        parser.error("No output requested, add -r or -e or -u.")
    
    return args


# returns the list of filenames (as string) in the file of files
def fof_to_list(fofname) :
    try :
        with open(fofname) as fof :
            filesnames = []

            for line in fof :
                filename = line.rstrip('\n')
                if len(filename) >= 1 :
                    filesnames.append(filename)

        return filesnames

    except IOError :
        print("File " + fofname + " not found.")
        raise


# returns the representation of a fasta file parsed in a list of SpecieData
# they contain the index of the first and last characteres of the sequence in the file
# the first is included and the last is excluded
def parsing(filename) :
    try :
        with open(filename, 'r') as f :
            header = None
            specie = None
            begin = 0
            end = 0
            sequences = list()
            c = 0

            for line in f :
                
                c += len(line)
                if line[0] == '>' :
                    
                    if header != None :
                        end = c - len(line) - 1
                        specie = SpecieData(header, begin, end, filename)
                        sequences.append(specie)
                    
                    header = line[1:].rstrip('\n')
                    begin = c
                    end = c+1
                
        # adds the last seq to the set
        end = c
        specie = SpecieData(header, begin, end, filename)
        sequences.append(specie)
        sequences.sort(key=lambda x:x.subseqs[0][1] - x.subseqs[0][0], reverse=True) # order by seq length from bigger to smaller, to minimize bigger sequences in first
        return sequences

    except IOError :
        print("File " + filename + " not found.")
        raise
        

# takes a file that contains the files name
# and return the list of lists of species by file
def parsing_multiple_files(filesnames) :
    spbyfile = list()

    for filename in filesnames :
        if len(filename) >= 1 :
            seqs = parsing(filename)
            spbyfile.append(seqs)

    return spbyfile




def main():

    starttime = time()

    # set and get the arguments
    args = set_args()

    # get the arguments
    desired_output = (args.returncode, args.stdout, args.stderr)
    infilename = args.filename
    nofof = args.onefasta

    cmdargs = CmdArgs(args.cmdline, infilename, nofof, args.outfilesnames, desired_output, args.verbose)
    allfiles = cmdargs.get_all_infiles()

    if cmdargs.verbose :
        s = "\n - Desired output : " + str(cmdargs.desired_output) + "\n"
        s += " - Fofname : " + cmdargs.infilename + "\n"
        s += " - Input files names : " + str(cmdargs.seqfilesnames) + "\n"
        s += " - Command : " + cmdargs.subcmdline + "\n"
        print(s)

    # parse the sequences of each file
    spbyfile = parsing_multiple_files(cmdargs.seqfilesnames)
    
    # process the data
    spbyfile = reduce_all_files(spbyfile, cmdargs)
    
    resultdir = "Results"
    rmtree(resultdir, ignore_errors=True)
    Path(resultdir).mkdir()
    
    # writes the reduced seqs in files in a new directory
    sp_to_files(spbyfile, cmdargs, resultdir)
    
    # writes the file register
    cmdargs.save_fileregister(resultdir + "/fileregister.txt")
    
    duration = time() - starttime
    write_stats(duration, resultdir + "/stats.txt")

    if args.verbose :
        print("\n", resultdir, " : ", sep="")
        print_files_debug(resultdir)
        print("\nDone.")
