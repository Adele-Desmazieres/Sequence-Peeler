import os
import os.path
import subprocess
import shutil
import argparse

TMPFILE = "tmp.fasta"
INPUTFILE = ""
CMD = ""

class SpecieData :
	
	def __init__(self, header, begin_seq, end_seq) : # initialise the specie with one seq
		self.header = header # string of the specie name and comments
		self.begin_seq = begin_seq # int, constant
		self.subseqs = set() # int tuple set, variable represents the index of the first char of the seq in the file (included) and the index of the last one (excluded)
		self.subseqs.add((begin_seq, end_seq)) # adds the index of the entire seq to the set
	
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
	finput = open(INPUTFILE, 'r')
	f2 = open(filename, 'w')

	ordered_iseqs = sorted(list(iseqs), key=lambda x:x.header) # alphabetical ordering of header's sequences
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


# check that the execution of cmd with the sequences as input gives the desired output
# TODO : execute on the cluster
def check_output(iseqs, cmd, desired_output, wd) :
	iseqs_to_file(iseqs, TMPFILE)
	output = subprocess.run(cmd, shell=True, capture_output=True, cwd=wd)

	checkreturn = desired_output[0] == None or desired_output[0] == output.returncode
	checkstdout = desired_output[1] == None or desired_output[1] == output.stdout
	checkstderr = desired_output[2] == None or desired_output[2] == output.stderr
	r = (checkreturn and checkstdout and checkstderr)

	return r


# reduces the sequence, cutting first and last nucleotides
# cutting in half successively with an iterative binary search
# returns the new reduced sequence, and adds it to the species's list of seqs
def strip_sequence(seq, sp, iseqs, cmd, desired_output, wd, flag_begining) :
	
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
		r = check_output(iseqs, cmd, desired_output, wd)
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
def reduce_specie(sp, iseqs, cmd, desired_output, wd) :
	
	tmpsubseqs = sp.subseqs.copy()
	
	while tmpsubseqs : # while set not empty
		
		seq = tmpsubseqs.pop() # take an arbitrairy element
		sp.subseqs.remove(seq)
		(begin, end) = seq
		middle = (seq[0] + seq[1]) // 2		
		seq1 = (begin, middle)
		seq2 = (middle, end)
		
		# case where the target fragment is in the first half
		sp.subseqs.add(seq1)
		if middle != end and check_output(iseqs, cmd, desired_output, wd) :
			tmpsubseqs.add(seq1)
			continue
		else :
			sp.subseqs.remove(seq1)		
		
		# case where the target fragment is in the second half
		sp.subseqs.add(seq2)
		if middle != begin and check_output(iseqs, cmd, desired_output, wd) :
			tmpsubseqs.add(seq2)
			continue
		else :
			sp.subseqs.remove(seq2)		
		
		# case where there are two co-factor sequences
		# so we cut the seq in half and add them to the seq to be reduced
		# TODO : relancer le check_output pour trouver les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		sp.subseqs.add(seq1)
		sp.subseqs.add(seq2)
		if middle != end and middle != begin and check_output(iseqs, cmd, desired_output, wd) :
			tmpsubseqs.add(seq1)
			tmpsubseqs.add(seq2)
			continue
		else :
			sp.subseqs.remove(seq1)
			sp.subseqs.remove(seq2)
		
		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		sp.subseqs.add(seq)
		seq = strip_sequence(seq, sp, iseqs, cmd, desired_output, wd, True)
		seq = strip_sequence(seq, sp, iseqs, cmd, desired_output, wd, False)
	
	return iseqs	


# returns every reduced sequences in a set of SpecieData
def reduce_data(iseqs, cmd, desired_output, wd) :
	cutted_iseqs = iseqs.copy()

	for sp in iseqs :
		# check if desired output is obtained whithout the sequence of the specie
		cutted_iseqs.remove(sp)
		
		if not check_output(cutted_iseqs, cmd, desired_output, wd) :
			# otherwise reduces the sequence
			cutted_iseqs.add(sp)
			cutted_iseqs = reduce_specie(sp, cutted_iseqs, cmd, desired_output, wd)

	return cutted_iseqs


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
						specie = SpecieData(header, begin, end)
						sequences.add(specie)
					
					header = line[1:].rstrip('\n')
					begin = c
					end = c+1
				
		# adds the last seq to the set
		end = c
		specie = SpecieData(header, begin, end)
		sequences.add(specie)
		
		return sequences

	except IOError :
		print("File not found.")


# removes the file TMPFILE
def rm_tmpfile() :
	os.remove(TMPFILE)


# creates the file TMP which is a copy of the inputfile
# ask the user to truncate it if this file already exists
# raise an error if a directory with this name already exists
def init_tmpfile(inputfile) :
	try :
		with open(TMPFILE, 'x') :
			shutil.copy(inputfile, TMPFILE)

	except OSError as e :

		if os.path.isfile(TMPFILE) :
			print(TMPFILE + " already exists, unable to create it.")
			truncate = input("Do you want to truncate " + TMPFILE + " ? (y,n) ")
			if truncate == 'y' : 
				with open(TMPFILE, 'w') as tmp :
					shutil.copy(inputfile, TMPFILE)
			else :
				exit(0)
		
		else :
			print("Unable to create the file" + TMPFILE + " : a directory with this name already exists.")
			raise(e)


# set the destination file to "workdir/minimised.fasta" if None specified
def get_outputfile(destfile, workdir) :
	if destfile == None :
		destfile = workdir + "/minimised.fasta"
	return destfile


def get_args() :
	parser = argparse.ArgumentParser(prog="Genome Fuzzing")

	# options that takes a value
	parser.add_argument('-d', '--destfile', default=None)
	parser.add_argument('-e', '--stderr', default=None)
	parser.add_argument('-o', '--stdout', default=None)
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-w', '--workdir', default=os.getcwd())

	# positionnal arguments
	parser.add_argument('filename')
	parser.add_argument('cmdline')
	parser.add_argument('returncode', type=int)
	
	args = parser.parse_args()
	return args


if __name__=='__main__' :

	# initialise the directories
	args = get_args()
	desired_output = (args.returncode, args.stdout, args.stderr)
	wd = args.workdir if args.workdir[len(args.workdir)-1] != '/' else args.workdir[:-1]
	outputfile = get_outputfile(args.destfile, wd)
	INPUTFILE = args.filename
	TMPFILE = wd + "/" + TMPFILE
	init_tmpfile(args.filename)

	if args.verbose :
		print(" - Desired output : " + str(desired_output))
		print(" - Working directory : " + wd)
		print(" - Tmp filename : " + TMPFILE)
		print(" - Output filename : " + outputfile + "\n")

	iseqs = parsing(INPUTFILE)

	# process the data
	cutted_iseqs = reduce_data(iseqs, args.cmdline, desired_output, wd)

	iseqs_to_file(cutted_iseqs, outputfile)
	rm_tmpfile()

	if args.verbose :
		print("\n - Minimised sequences:")
		with open(outputfile) as f :
			print(f.read())
		print("\nDone.")

	