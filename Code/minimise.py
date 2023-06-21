import os
import os.path
from pathlib import Path
import subprocess
import shutil
import argparse

#TMPFILE = "tmp.fasta"
TMP_EXTENSION = "_tmp"
INFILESNAMES = []
FOFNAME = ""
CMD = ""
WORKDIR = ""
DESIRED_OUTPUT = None

class SpecieData :
	
	def __init__(self, header, begin_seq, end_seq, filename) : # initialise the specie with one seq
		self.header = header # string of the specie name and comments
		self.begin_seq = begin_seq # int, constant
		self.subseqs = set() # int tuple set, variable represents the index of the first char of the seq in the file (included) and the index of the last one (excluded)
		self.subseqs.add((begin_seq, end_seq)) # adds the index of the entire seq to the set
		self.filename = filename # string filename
	
	def __str__(self) : # debug function
		s = ">" + self.header + "\n"
		s += str(self.subseqs)
		return s


def printset(iseqs) :
	print()
	for sp in list(iseqs) :
		print(sp)


# writes the sequences and their species in a fasta file
def iseqs_to_file(iseqs, filename) :
	finput = open(None, 'r') # TODO : remplacer None
	f2 = open(filename, 'w')

	ordered_iseqs = sorted(list(iseqs), key=lambda x:x.begin_seq) # alphabetical ordering of header's sequences
	for (i, sp) in enumerate(ordered_iseqs) :
			
		for (j, subseq) in enumerate(sorted(list(sp.subseqs), key=lambda x:x[0])) :
			if i != 0 or j != 0 :
				f2.write("\n")
			
			(begin, end) = subseq

			firstcharseq = sp.begin_seq
			firstnuclsubseq = begin - firstcharseq + 1
			header = sp.header + ", position " + str(firstnuclsubseq)
			
			f2.write(">" + header + "\n")
			finput.seek(begin)
			actual_seq = finput.read(end-begin)
			f2.write(actual_seq)
	
	finput.close()
	f2.close()


def sp_to_files(spbyfile) :

	for iseqs in spbyfile :

		tmp_specie = iseqs.pop()
		filename = tmp_specie.filename
		iseqs.add(tmp_specie)
		iseqs_to_file(iseqs, filename)


# check that the execution of cmd with the sequences as input gives the desired output
# TODO : execute on the cluster
def check_output(spbyfile) :
	sp_to_files(spbyfile)
	output = subprocess.run(CMD, shell=True, capture_output=True, cwd=WORKDIR)

	checkreturn = DESIRED_OUTPUT[0] == None or DESIRED_OUTPUT[0] == output.returncode
	checkstdout = DESIRED_OUTPUT[1] == None or DESIRED_OUTPUT[1] in output.stdout.decode()
	checkstderr = DESIRED_OUTPUT[2] == None or DESIRED_OUTPUT[2] in output.stderr.decode()
	r = (checkreturn and checkstdout and checkstderr)

	return r


# reduces the sequence, cutting first and last nucleotides
# cutting in half successively with an iterative binary search
# returns the new reduced sequence, and adds it to the species's list of seqs
def strip_sequence(seq, sp, iseqs, spbyfile, flag_begining) :
	
	(begin, end) = seq
	seq1 = seq
	sp.subseqs.remove(seq)

	imin = begin
	imax = end
	imid = (imin+imax) // 2
		
	while imid != imin and imid != imax :

		# get the most central quarter
		seq1 = (imid, end) if flag_begining else (begin, imid)
		sp.subseqs.add(seq1)
		r = check_output(spbyfile)
		sp.subseqs.remove(seq1)

		# if the cut maintain the output, we keep cutting toward the center of the sequence
		if r :
			if flag_begining :
				imin = imid
			else :
				imax = imid

		# else the cut doesn't maintain the output, so we keep cutting toward the exterior
		else :
			# keep the most external quarter
			seq1 = (imin, end) if flag_begining else (begin, imax)
			if flag_begining :
				imax = imid
			else :
				imin = imid
	
		imid = (imin+imax) // 2
	
	sp.subseqs.add(seq1)
	return seq1


# reduces the sequences of the specie and return the new set of SpecieData instances
# use an iterative binary search
def reduce_specie(sp, iseqs, spbyfile) :
	
	tmpsubseqs = sp.subseqs.copy()
	
	while tmpsubseqs : # while set not empty
		
		seq = tmpsubseqs.pop() # take an arbitrary element
		sp.subseqs.remove(seq)
		(begin, end) = seq
		middle = (seq[0] + seq[1]) // 2		
		seq1 = (begin, middle)
		seq2 = (middle, end)
		
		# case where the target fragment is in the first half
		sp.subseqs.add(seq1)
		if middle != end and check_output(spbyfile) :
			tmpsubseqs.add(seq1)
			continue
		else :
			sp.subseqs.remove(seq1)		
		
		# case where the target fragment is in the second half
		sp.subseqs.add(seq2)
		if middle != begin and check_output(spbyfile) :
			tmpsubseqs.add(seq2)
			continue
		else :
			sp.subseqs.remove(seq2)		
		
		# case where there are two co-factor sequences
		# so we cut the seq in half and add them to the seq to be reduced
		# TODO : relancer le check_output pour trouver les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		sp.subseqs.add(seq1)
		sp.subseqs.add(seq2)
		if middle != end and middle != begin and check_output(spbyfile) :
			tmpsubseqs.add(seq1)
			tmpsubseqs.add(seq2)
			continue
		else :
			sp.subseqs.remove(seq1)
			sp.subseqs.remove(seq2)
		
		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		sp.subseqs.add(seq)
		seq = strip_sequence(seq, sp, iseqs, spbyfile, True)
		seq = strip_sequence(seq, sp, iseqs, spbyfile, False)
	
	return iseqs	


# returns every reduced sequences of a file in a set of SpecieData
def reduce_one_file(iseqs, spbyfile) :
	reduced_iseqs = iseqs.copy()

	for sp in iseqs :
		# check if desired output is obtained whithout the sequence of the specie
		reduced_iseqs.remove(sp)
		
		if not check_output(spbyfile) :
			# otherwise reduces the sequence
			reduced_iseqs.add(sp)
			reduced_iseqs = reduce_specie(sp, reduced_iseqs, spbyfile)

	return reduced_iseqs


def reduce_all_files(spbyfile) :
	reduced = spbyfile.copy()

	for iseqs in spbyfile :
		# check if desired output is obtained whithout the sequences of the file
		reduced.remove(iseqs)
		
		if not check_output(reduced) :
			# otherwise reduces the sequences of the file
			reduced.add(iseqs)
			reduced = reduce_one_file(iseqs, reduced)

	return reduced


# returns the representation of a fasta file parsed in a set of SpecieData
# they contain the index of the first and last characteres of the sequence in the file
# the first is included and the last is excluded
def parsing(filename) :
	try :
		with open(filename, 'r') as f :
			header = None
			specie = None
			begin = 0
			end = 0
			sequences = set()
			c = 0

			for line in f :
				
				c += len(line)
				if line[0] == '>' :
					
					if header != None :
						end = c - len(line) - 1
						specie = SpecieData(header, begin, end, filename)
						sequences.add(specie)
					
					header = line[1:].rstrip('\n')
					begin = c
					end = c+1
				
		# adds the last seq to the set
		end = c
		specie = SpecieData(header, begin, end, filename)
		sequences.add(specie)
		return sequences

	except IOError :
		print("File " + filename + " not found.")
		raise
		


# takes a file that contains the files name
# and return the set of sets of species by file
def parsing_multiple_files(filesnames) :
	spbyfile = set()

	for filename in filesnames :
		if len(filename) >= 1 :
			seqs = parsing(filename)
			spbyfile.add(seqs)

	return spbyfile


# removes the file TMPFILE
def rm_tmpfiles(filesnames) :

	for fname in filesnames : 
		p = Path(fname)
		tmp_fname = str(p.parent) + p.stem + TMP_EXTENSION + p.suffix
		Path(tmp_fname).rename(Path(fname)) # rename the original files with their original name, and truncate the temporary files


# copies a file with the same name with an extension to its stem
# ask the user to truncate it when it already exists
# raise an error if a directory with its name already exists
def copy_file_with_extension(filename, extension) :
	p = Path(filename)
	tmp_fname = str(p.parent) + p.stem + extension + p.suffix

	try :
		with open(tmp_fname, 'x') : # exclusive creation
			shutil.copy(filename, tmp_fname)

	except OSError :

		if Path(tmp_fname).isfile() :
			print(tmp_fname + " file already exists, unable to create it.")
			truncate = input("Do you want to truncate " + tmp_fname + " ? (y,n) ")
			if truncate == 'y' : 
				shutil.copy(filename, tmp_fname)
			else :
				exit(0)
		
		else :
			print(tmp_fname + " directory already exists, unable to create it.")
			raise


# creates the temporary files as copies of input files
def copy_infiles(filesnames) :
	for filename in filesnames : 
		copy_file_with_extension(filename, TMP_EXTENSION)

def copy_fof(fofname) :
	copy_file_with_extension(fofname, TMP_EXTENSION)	


# returns the list of filenames in the fof (file of files)
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


# set the destination file to "workdir/minimised.fasta" if None specified
def get_destdir(destdir, workdir) :
	if destdir == None :
		destdir = workdir
	destdir = destdir if destdir[len(destdir)-1] == '/' else destdir + '/'
	return destdir


def get_args() :
	parser = argparse.ArgumentParser(prog="Genome Fuzzing")

	# options that takes a value
	parser.add_argument('-d', '--destdir', default=None)
	parser.add_argument('-e', '--stderr', default=None)
	#parser.add_argument('-f', '--onefasta', action='store_true')
	parser.add_argument('-o', '--stdout', default=None)
	parser.add_argument('-r', '--returncode', default=None, type=int)
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-w', '--workdir', default=os.getcwd())

	# positionnal arguments
	parser.add_argument('file_of_files_name')
	parser.add_argument('cmdline')
	
	args = parser.parse_args()
	if not (args.returncode or args.stdout or args.stderr) :
		parser.error("No output requested, add -r or -e or -o.")
	
	return args


if __name__=='__main__' :

	# get the arguments
	args = get_args()
	DESIRED_OUTPUT = (args.returncode, args.stdout, args.stderr)
	CMD = args.cmdline

	# initialise the globals
	WORKDIR = args.workdir if args.workdir[len(args.workdir)-1] == "/" else args.workdir + "/"
	destdir = get_destdir(args.destdir, WORKDIR)
	FOFNAME = args.file_of_files_name
	INFILESNAMES = fof_to_list(FOFNAME)
	# from here every global should be constant

	# copies the input files in temporary files, not to overwrite the temporary ones
	copy_infiles(INFILESNAMES)
	copy_fof(FOFNAME)

	if args.verbose :
		print()
		print(" - Desired output : " + str(DESIRED_OUTPUT))
		print(" - Working directory : " + WORKDIR)
		print(" - Fofname : " + FOFNAME)
		print(" - Input files names : " + INFILESNAMES)
		print(" - Output directory : " + destdir + "\n")

	spbyfile = parsing_multiple_files(None) # TODO : remplacer None

	# process the data
	reduced_spbyfile = reduce_all_files(spbyfile)

	# writes the reduced seqs in files in destination directory
	sp_to_files(reduced_spbyfile, destdir)

	# removes the temporary files and rename the original ones
	rm_tmpfiles(INFILESNAMES)

	#if args.verbose :
	#	print("\n - Minimised sequences:")
	#	with open(outputfile) as f :
	#		print(f.read())
	#	print("\nDone.")

	