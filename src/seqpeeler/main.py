import argparse
from time import time
from pathlib import Path
from os import path, mkdir
from shutil import rmtree

from seqpeeler.minimise import reduce_file_set, sp_to_files, write_stats
from seqpeeler.filemanager import FileManager


# class CmdArgs :

#     def __init__(self, subcmdline, infilename, nofof, outfilesnames, desired_output, verbose) :
#         self.subcmdline = subcmdline
#         self.infilename = infilename # the name of the fof or the only file of sequences
#         self.nofof = nofof
#         self.outfilesnames = outfilesnames
#         self.desired_output = desired_output
#         self.verbose = verbose
#         self.seqfilesnames = []
#         self.init_seqfilesnames()
#         self.fileregister = self.make_fileregister(self.get_all_infiles() + self.outfilesnames)
#         self.subcmdline_replaced = self.replace_path_in_cmd(self.get_all_infiles() + self.outfilesnames)
#         # print(self.fileregister)
#         # print(self.subcmdline_replaced)
    
#     def init_seqfilesnames(self) :
#         if self.nofof :
#             self.seqfilesnames = [self.infilename]
#         else :
#             self.seqfilesnames = fof_to_list(self.infilename)

#     def get_all_infiles(self) :
#         return [self.infilename] if self.nofof else self.seqfilesnames + [self.infilename]
        
#     def replace_path_in_cmd(self, files) :
#         cmd = self.subcmdline
#         for f in files :
#             cmd = cmd.replace(f, self.fileregister[f])
#         return cmd
    
#     # returns the dict of filepath:renamedfile
#     # where renamedfile is either the filename or something else if this filename is already used
#     def make_fileregister(self, files) :
#         fileregister = dict()
#         for f in files :
#             i = 1
#             p = Path(f)
#             tmpname = p.name
#             while tmpname in fileregister.values() :
#                 tmpname = p.stem + "_" + str(i) + p.suffix
#                 i += 1
#             fileregister[f] = tmpname
#         return fileregister
    
#     def save_fileregister(self, filepath) :
#         infiles = self.get_all_infiles()
#         f = open(filepath, 'w')
#         for oldpath,newname in self.fileregister.items() :
#             if oldpath in infiles :
#                 f.write(oldpath + " : " + newname + "\n")
#         f.close()


# returns the list of filenames (as string) in the file of files
def fof_to_list(fofname) :
    try :
        with open(fofname) as fof :
            filesnames = []

            for line in fof :
                filename = line.rstrip('\n')
                if not path.isfile(filename):
                    raise FileNotFoundError(f"File from fof not found: {filename}")
                filenames.append(path.abspath(filename))

        return filesnames

    except IOError :
        print("fof " + fofname + " not found.")
        raise

        

def parsing_files(filesnames) :
    """ Reads a list of files and return their file manager objects
    """
    files = []

    for filename in filesnames :
        manager = FileManager(filename)
        manager.index_sequences()
        files.append(manager)

    return files



def print_files_debug(dirname) :
    pdir = Path(dirname)
    for filename in pdir.iterdir() :
        p = Path(filename)
        outputfilename = dirname + "/" + p.name
        
        print("\nIn file \"" + outputfilename + "\" :\n")
        with open(outputfilename) as f :
            print(f.read())
        
    print()



# prepare the argument parser and parses the command line
# returns an argparse.Namespace object
def parse_args() :
    parser = argparse.ArgumentParser(prog="Genome Fuzzing")

    # non positionnal arguments
    parser.add_argument('-e', '--stderr', default=None)
    parser.add_argument('-f', '--onefasta', action='store_true')
    parser.add_argument('-o', '--outfilesnames', action='extend', nargs='+', type=str, default=[])
    parser.add_argument('-r', '--returncode', default=None, type=int)
    parser.add_argument('-u', '--stdout', default=None)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--outdir', default='Results')

    # positionnal arguments
    parser.add_argument('filename')
    parser.add_argument('cmdline')
    
    args = parser.parse_args()
    if args.returncode is None and args.stdout is None and args.stderr is None :
        parser.error("No output requested, add -r or -e or -u.")
    
    return args



def main():

    starttime = time()

    # set and get the arguments
    args = parse_args()

    # Creates the results directory
    if path.exists(args.outdir):
        rmtree(args.outdir)
    args.outdir = path.abspath(args.outdir)
    mkdir(args.outdir)

    # get the arguments
    desired_output = (args.returncode, args.stdout, args.stderr)
    seqfiles = [args.filename] if args.onefasta else fof_to_list(args.filename)

    if args.verbose :
        s = "\n - Desired output : " + str(desired_output) + "\n"
        s += " - Fofname : " + args.filename + "\n"
        s += " - Input files names : " + str(", ".join(seqfiles)) + "\n"
        s += " - Command : " + cmdline + "\n"
        print(s)

    # parse the sequences of each file
    file_managers = parsing_files(seqfiles)
    for manager in file_managers:
        manager.verbose = True
        print(manager)
        manager.verbose = False
    
    # process the data
    reduced = reduce_file_set(file_managers, args)
    
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
