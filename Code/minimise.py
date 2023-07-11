from pathlib import Path
import subprocess
import shutil
import argparse
import multiprocessing
from multiprocessing import Pool

TMP_EXTENSION = "_tmp"
NB_PROCESS = 0

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
		self.seqfilesnames = []
		self.verbose = verbose
	
	def init_seqfilesnames(self) :
		if nofof :
			self.seqfilesnames = [self.infilename]
		else :
			self.seqfilesnames = fof_to_list(self.infilename)

	def get_all_files(self) :
		return [self.infilename] if self.nofof else self.seqfilesnames + [self.infilename]
		
	

def printset(iseqs) :
	for sp in list(iseqs) :
		print(sp)

def print_debug(spbyfile) :
	print("ACTUAL STATE")
	for iseqs in spbyfile :
		printset(iseqs)
	print()

def print_files_debug(dirname) :
	pdir = Path(dirname)
	for filename in pdir.iterdir() :
		p = Path(filename)
		outputfilename = dirname + "/" + p.name
		
		print("\nIn file \"" + outputfilename + "\" :\n")
		with open(outputfilename) as f :
			print(f.read())
		
	print()


### code from https://stackoverflow.com/a/26209275
def chunks(fd, buffer_size=4096):
	chunk = fd.read(buffer_size)
	while chunk:
		yield chunk
		chunk = fd.read(buffer_size)

def chars(fd, buffersize=4096):
	for chunk in chunks(fd, buffersize):
		for char in chunk:
			yield char
### end of code copy


# writes the sequences and their species in a fasta file
def iseqs_to_file(iseqs, inputfilename, outputfilename) :
	inputfile = open(inputfilename, 'r')
	outputfile = open(outputfilename, 'w')
	outputfile.truncate(0)

	ordered_iseqs = sorted(list(iseqs), key=lambda x:x.begin_seq) # ordering of header's sequences by index of first nucleotide of the initial sequence
	for (i, sp) in enumerate(ordered_iseqs) :
			
		for (j, subseq) in enumerate(sorted(sp.subseqs, key=lambda x:x[0])) :
			if i != 0 or j != 0 :
				outputfile.write("\n")
			
			(begin, end) = subseq
			firstcharseq = sp.begin_seq
			inputfile.seek(firstcharseq)
			
			# counts the number of line breaks in the seq before the first nucl of the subseq
			nb_line_breaks = 0
			ic = firstcharseq
			for c in chars(inputfile) :
				if ic < begin :
					if c == '\n' : 
						nb_line_breaks += 1
					ic += 1
				else :
					break
				
			# writes the header
			firstnuclsubseq = begin - firstcharseq + 1 - nb_line_breaks
			header = sp.header + ", position " + str(firstnuclsubseq)
			outputfile.write(">" + header + "\n")
			
			# read the subseq from the input and writes it in the output
			inputfile.seek(begin)
			actual_subseq = inputfile.read(end-begin)
			outputfile.write(actual_subseq)
	
	inputfile.close()
	outputfile.close()


# returns the filenames with the input and the output extension
def get_in_out_filename(filename, input_extension, output_extension) :
	p = Path(filename)
	inputfilename = str(p.parent) + "/" + p.stem + input_extension + p.suffix
	outputfilename = str(p.parent) + "/" + p.stem + output_extension + p.suffix
	return (inputfilename, outputfilename)

def get_output_filename(filename, dirname) :
	return dirname + "/" + Path(filename).name

# writes the content of the fof and call the function that writes their contents
# reading from files with the input_extension, and writting in ones with the output_extension
def sp_to_files(spbyfile, cmdargs, dirname) :

	if cmdargs.nofof : 
		iseqs = spbyfile[0]
		if len(iseqs) != 0 :
			inputfilename = iseqs[0].filename
			outputfilename = get_output_filename(inputfilename, dirname)
			iseqs_to_file(spbyfile[0], inputfilename, outputfilename)
		
		# makes the empty file
		else :
			open(get_output_filename(cmdargs.infilename, dirname), 'w').close()
		
		return None

	files_to_truncate = cmdargs.get_all_files()
	outfofname = get_output_filename(cmdargs.infilename, dirname)
	
	try :
		with open(outfofname, 'w') as fof :
			
			for (i, iseqs) in enumerate(spbyfile) :
				
				if len(iseqs) != 0 :
					
					inputfilename = iseqs[0].filename
					outputfilename = get_output_filename(inputfilename, dirname)

					# writes its name in the file of files
					if i != 0 :
						fof.write("\n")
					fof.write(Path(outputfilename).name)
		
					# call the function that writes the content of the file
					iseqs_to_file(iseqs, inputfilename, outputfilename)

					files_to_truncate.remove(iseqs[0].filename)
				
			for f in files_to_truncate :
				open(get_output_filename(f, dirname), 'w').close()
					
	except IOError :
		raise


def replace_path_in_cmd(cmd, files) :
	for f in files :
		cmd = cmd.replace(f, Path(f).name)
	return cmd


# check that the execution of cmd with the sequences as input gives the desired output
def check_output(spbyfile, cmdargs, dirname) :

	cmd_replaced_files = replace_path_in_cmd(cmdargs.subcmdline, cmdargs.get_all_files())
	
	if cmdargs.verbose :
		#print("subprocess " + str(NB_PROCESS))
		print("subprocess " + str(multiprocessing.current_process().pid))
		print(cmd_replaced_files)
		print_debug(spbyfile)
		#print_files_debug(dirname)

	output = subprocess.run(cmd_replaced_files, shell=True, capture_output=True, cwd=dirname)
	
	shutil.rmtree(dirname)

	dout = cmdargs.desired_output
	checkreturn = dout[0] == None or dout[0] == output.returncode
	checkstdout = dout[1] == None or dout[1] in output.stdout.decode()
	checkstderr = dout[2] == None or dout[2] in output.stderr.decode()
	r = (checkreturn and checkstdout and checkstderr)

	if cmdargs.verbose :
		#print("end subprocess " + str(NB_PROCESS))
		print("end subprocess " + str(multiprocessing.current_process().pid))

	return r


def make_new_dir() :
	i = 0
	dirname = str(i)
	while Path(dirname).exists() :
		i += 1
		dirname = str(i)
	Path(dirname).mkdir()
	return dirname


def prepare_subprocess(spbyfile, cmdargs) :
	global NB_PROCESS
	NB_PROCESS += 1
	dirname = make_new_dir()
	sp_to_files(spbyfile, cmdargs, dirname)
	return dirname


# reduces the sequence, cutting first and last nucleotides
# cutting in half successively with an iterative binary search
# returns the new reduced sequence, WITHOUT ADDING IT TO THE SPECIE'S LIST OF SEQS
def strip_sequence(seq, sp, spbyfile, flag_begining, cmdargs) :
	(begin, end) = seq
	seq1 = (begin, end)

	imin = begin
	imax = end
	imid = (imin+imax) // 2
		
	while imid != imin and imid != imax :

		# get the most central quarter
		seq1 = (imid, end) if flag_begining else (begin, imid)
		sp.subseqs.append(seq1)
		dirname = prepare_subprocess(spbyfile, cmdargs)
		testresult = check_output(spbyfile, cmdargs, dirname)
		sp.subseqs.remove(seq1)

		# if the cut maintain the output, we keep cutting toward the center of the sequence
		if testresult :
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
	
	return seq1


# reduces the sequences of the specie and puts it in the list spbyfile
# use an iterative binary search, returns nothing
def reduce_specie(sp, spbyfile, cmdargs) :
	
	tmpsubseqs = sp.subseqs.copy()
	
	while tmpsubseqs : # while set not empty
		
		seq = tmpsubseqs.pop() # take an arbitrary sequence of the specie
		sp.subseqs.remove(seq)
		(begin, end) = seq

		middle = (seq[0] + seq[1]) // 2		
		seq1 = (begin, middle)
		seq2 = (middle, end)

		# prepare the files and directories needed to check if they pass the test
		sp.subseqs.append(seq1)
		dirname1 = prepare_subprocess(spbyfile, cmdargs)
		sp.subseqs.remove(seq1)		

		sp.subseqs.append(seq2)
		dirname2 = prepare_subprocess(spbyfile, cmdargs)

		sp.subseqs.append(seq1)
		dirname3 = prepare_subprocess(spbyfile, cmdargs)
		sp.subseqs.remove(seq1)
		sp.subseqs.remove(seq2)

		dirnames = [dirname1, dirname2, dirname3]

		# TODO : https://stackoverflow.com/questions/71192894/python-multiprocessing-terminate-other-processes-after-one-process-finished 
		# prepare and launches the different processes
		p = Pool(processes=3)
		procargs = [(spbyfile, cmdargs, d) for d in dirnames]
		data = p.starmap(check_output, procargs)
		p.close()
		case1 = data[0]
		case2 = data[1]
		case3 = data[2]
		
		# case where the target fragment is in the first half
		if middle != end and case1 :
			sp.subseqs.append(seq1)		
			tmpsubseqs.append(seq1)
			continue
		
		# case where the target fragment is in the second half
		if middle != begin and case2 :
			sp.subseqs.append(seq2)		
			tmpsubseqs.append(seq2)
			continue
		
		# case where there are two co-factor sequences
		# so we cut the seq in half and add them to the set to be reduced
		# TODO : relancer le check_output pour trouver les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		if middle != end and middle != begin and case3 :
			sp.subseqs.append(seq1)
			sp.subseqs.append(seq2)
			tmpsubseqs.append(seq1)
			tmpsubseqs.append(seq2)
			continue
		
		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		seq = strip_sequence(seq, sp, spbyfile, True, cmdargs)
		seq = strip_sequence(seq, sp, spbyfile, False, cmdargs)
		sp.subseqs.append(seq)
	
	return None


# returns every reduced sequences of a file in a list of SpecieData
def reduce_one_file(iseqs, spbyfile, cmdargs) :
	copy_iseqs = iseqs.copy()

	for sp in copy_iseqs :
		# check if desired output is obtained whithout the sequence of the specie
		iseqs.remove(sp)
		
		dirname = prepare_subprocess(spbyfile, cmdargs)
		testresult = check_output(spbyfile, cmdargs, dirname)
		if not testresult :
			# otherwise reduces the sequence
			iseqs.append(sp)
			reduce_specie(sp, spbyfile, cmdargs)
		
	return iseqs


def reduce_all_files(spbyfile, cmdargs) :
	
	if len(spbyfile) == 1 :
		reduce_one_file(spbyfile[0], spbyfile, cmdargs)
		return spbyfile
	
	copy_spbyfile = spbyfile.copy()

	for iseqs in copy_spbyfile :
		# check if desired output is obtained whithout the file
		spbyfile.remove(iseqs)

		dirname = prepare_subprocess(spbyfile, cmdargs)
		testresult = check_output(spbyfile, cmdargs, dirname)
		if not testresult :
			# otherwise reduces the sequences of the file
			spbyfile.append(iseqs)
			reduce_one_file(iseqs, spbyfile, cmdargs)

	return spbyfile


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
def copy_files(filesnames) :
	for filename in filesnames : 
		copy_file_with_extension(filename, TMP_EXTENSION)


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


def rm_file(filename) :
	p = Path(filename)
	p.unlink()


def set_args() :
	parser = argparse.ArgumentParser(prog="Genome Fuzzing")

	# non positionnal arguments
	parser.add_argument('-e', '--stderr', default=None)
	parser.add_argument('-f', '--onefasta', action='store_true')
	parser.add_argument('-r', '--returncode', default=None, type=int)
	parser.add_argument('-o', '--outfilesnames', action='extend', nargs='+', type=str, default=[])
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-u', '--stdout', default=None)

	# positionnal arguments
	parser.add_argument('filename')
	parser.add_argument('cmdline')
	
	args = parser.parse_args()
	if not (args.returncode or args.stdout or args.stderr) :
		parser.error("No output requested, add -r or -e or -u.")
	
	return args


if __name__=='__main__' :

	# set and get the arguments
	args = set_args()

	# get the arguments
	desired_output = (args.returncode, args.stdout, args.stderr)
	infilename = args.filename
	nofof = args.onefasta

	cmdargs = CmdArgs(args.cmdline, infilename, nofof, args.outfilesnames, desired_output, args.verbose)
	cmdargs.init_seqfilesnames()
	allfiles = cmdargs.get_all_files()

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
	
	resultdir = "Results" # TODO : delete the previous Results directory ? ask the user ? make a new one with a different name ?
	#tmpdir = resultdir
	#i = 1
	#while Path(resultdir).exists() :
	#	resultdir = tmpdir + str(i)
	#	i += 1
	shutil.rmtree(resultdir, ignore_errors=True)
	Path(resultdir).mkdir()
	
	# writes the reduced seqs in files in a new directory
	sp_to_files(spbyfile, cmdargs, resultdir)
	
	print("Process number : " + str(NB_PROCESS))
	print_debug(spbyfile)
	if args.verbose :
		#print("\n", resultdir, " : ", sep="")
		#print_files_debug(resultdir)
		print("\nDone.")
