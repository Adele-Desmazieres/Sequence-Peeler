import os
import os.path
from pathlib import Path
import subprocess
import shutil
import argparse

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

def print_debug(spbyfile) :
	print("\nACTUAL STATE")
	for iseqs in spbyfile :
		printset(iseqs)

def print_files_debug(extension) :
	print("\nFILES")
	for filename in [FOFNAME] + INFILESNAMES :
		p = Path(filename)
		outputfilename = str(p.parent) + "/" + p.stem + extension + p.suffix
			
		print("\n\"" + outputfilename + "\" :\n")
		with open(outputfilename) as f :
			print(f.read())
	print()

# writes the sequences and their species in a fasta file
def iseqs_to_file(iseqs, inputfilename, outputfilename) :
	inputfile = open(inputfilename, 'r')
	outputfile = open(outputfilename, 'w')

	ordered_iseqs = sorted(list(iseqs), key=lambda x:x.begin_seq) # ordering of header's sequences by index of first nucleotide of the initial sequence
	for (i, sp) in enumerate(ordered_iseqs) :
			
		for (j, subseq) in enumerate(sorted(list(sp.subseqs), key=lambda x:x[0])) :
			if i != 0 or j != 0 :
				outputfile.write("\n")
			
			(begin, end) = subseq

			firstcharseq = sp.begin_seq
			firstnuclsubseq = begin - firstcharseq + 1
			header = sp.header + ", position " + str(firstnuclsubseq)
			
			outputfile.write(">" + header + "\n")
			inputfile.seek(begin)
			actual_seq = inputfile.read(end-begin)
			outputfile.write(actual_seq)
	
	inputfile.close()
	outputfile.close()


def sp_to_files(spbyfile, input_extension, output_extension) :
	
	try :
		with open(FOFNAME, 'w') as fof :
		
			for iseqs in spbyfile :
				
				if len(iseqs) != 0 :
					# récupérer le nom du fichier de ce set() grâce à l'une de ses espèces
					tmp_specie = iseqs.pop()
					filename = tmp_specie.filename
					iseqs.add(tmp_specie)
		
					p = Path(filename)
					outputfilename = str(p.parent) + "/" + p.stem + output_extension + p.suffix
					inputfilename = str(p.parent) + "/" + p.stem + input_extension + p.suffix
					
					# l'écrire dans le fof
					fof.write(outputfilename + "\n")
		
					# lancer l'écriture du fichier
					iseqs_to_file(iseqs, inputfilename, outputfilename)
		
	except IOError :
		raise


# check that the execution of cmd with the sequences as input gives the desired output
# TODO : execute on the cluster
def check_output(spbyfile) :
	sp_to_files(spbyfile, TMP_EXTENSION, "")
	#print_files_debug("")
	output = subprocess.run(CMD, shell=True, capture_output=True, cwd=WORKDIR)

	checkreturn = DESIRED_OUTPUT[0] == None or DESIRED_OUTPUT[0] == output.returncode
	checkstdout = DESIRED_OUTPUT[1] == None or DESIRED_OUTPUT[1] in output.stdout.decode()
	checkstderr = DESIRED_OUTPUT[2] == None or DESIRED_OUTPUT[2] in output.stderr.decode()
	r = (checkreturn and checkstdout and checkstderr)
	print("Result :", r)
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
		
		seq = tmpsubseqs.pop() # take an arbitrary sequence of the specie
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
		# so we cut the seq in half and add them to the set to be reduced
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
	if len(iseqs) <= 1 :
		return iseqs

	copy_iseqs = iseqs.copy()

	for sp in copy_iseqs :
		print("____________________________________")
		print_files_debug("")
		print("____________________________________")
		# check if desired output is obtained whithout the sequence of the specie
		iseqs.remove(sp)
		print("Trying to remove a specie", sp.header)
		
		if not check_output(spbyfile) :
			# otherwise reduces the sequence
			iseqs.add(sp)
			#reduce_specie(sp, iseqs, spbyfile)
		else :
			print("Removing a specie")
		
	return iseqs


def reduce_all_files(spbyfile) :
	copy_spbyfile = spbyfile.copy()
	print_files_debug("")

	for iseqs in copy_spbyfile :
		print("====================================")
		print_files_debug("")
		print("====================================")
		#print("ISEQS : ")
		#printset(iseqs)

		# check if desired output is obtained whithout the file
		spbyfile.remove(iseqs)
		print("Trying to remove a file")

		if not check_output(spbyfile) :
			# otherwise reduces the sequences of the file
			spbyfile.append(iseqs)
			reduce_one_file(iseqs, spbyfile)
		else :
			print("Removing a file")

	return spbyfile


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
	spbyfile = []

	for filename in filesnames :
		if len(filename) >= 1 :
			seqs = parsing(filename)
			spbyfile.append(seqs)

	return spbyfile


def rename_files(filesnames, old_extension, new_extension) :
	for fname in filesnames : 
		p = Path(fname)
		old_fname = str(p.parent) + "/" + p.stem + old_extension + p.suffix
		new_fname = str(p.parent) + "/" + p.stem + new_extension + p.suffix
		if Path(old_fname).is_file() :
			Path(old_fname).rename(Path(new_fname))


# copies a file with the same name with an extension to its stem
# ask the user to truncate it when it already exists
# raise an error if a directory with its name already exists
def copy_file_with_extension(filename, extension) :
	p = Path(filename)
	tmp_fname = str(p.parent) + "/" + p.stem + extension + p.suffix

	try :
		with open(tmp_fname, 'x') : # exclusive creation
			shutil.copy(filename, tmp_fname)

	except OSError :

		if Path(tmp_fname).is_file() :
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
		print(" - Input files names : " + str(INFILESNAMES))
		print()

	# parse the sequences of each file
	spbyfile = parsing_multiple_files(INFILESNAMES)
	
	# test qui ajoute 1 à l'index d'une seq du premier fichier
	'''
	sp = spbyfile[0].pop()
	subseq = sp.subseqs.pop()
	sp.subseqs.add((subseq[0] + 1, subseq[1]))
	spbyfile[0].add(sp)
	'''
	
	# process the data
	spbyfile = reduce_all_files(spbyfile)

	# writes the reduced seqs in files
	sp_to_files(spbyfile, TMP_EXTENSION, "")
	# TODO : writting fof
	
	# rename reduced files with _result
	rename_files(INFILESNAMES + [FOFNAME], "", "_result")
	# rename _tmp files to their original name
	rename_files(INFILESNAMES + [FOFNAME], TMP_EXTENSION, "")
	
	if args.verbose :
		print_files_debug("_result")
		print("\nDone.")

	