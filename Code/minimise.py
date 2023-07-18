from time import sleep
from pathlib import Path
from subprocess import Popen
from subprocess import PIPE
from shutil import rmtree
from shutil import copy as shutilcopy
from multiprocessing import Pool
import argparse

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
		self.subcmdline_replaced = self.replace_path_in_cmd(self.get_all_files() + self.outfilesnames)
	
	def init_seqfilesnames(self) :
		if nofof :
			self.seqfilesnames = [self.infilename]
		else :
			self.seqfilesnames = fof_to_list(self.infilename)

	def get_all_files(self) :
		return [self.infilename] if self.nofof else self.seqfilesnames + [self.infilename]
		
	def replace_path_in_cmd(self, files) :
		cmd = self.subcmdline
		for f in files :
			cmd = cmd.replace(f, Path(f).name)
		return cmd


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


def compare_output(acutal_output, desired_output) :
	rcode, stdout, stderr = acutal_output
	rcode2, stdout2, stderr2 = desired_output

	checkreturn = rcode2 is None or rcode2 == rcode
	checkstdout = stdout2 is None or stdout2 in stdout.decode()
	checkstderr = stderr2 is None or stderr2 in stderr.decode()
	r = checkreturn and checkstdout and checkstderr
	return r


# launches the processes in the console, from a command and a list of directories
# returns the dictionnary of process(Popen) : dirname(String)
def trigger_processes(cmdline, dirnamelist):
	dirnamedict = dict()

	for dirname in dirnamelist:
		#print("Cmd running in:", dirname)
		p = Popen(cmdline, shell=True, cwd=dirname, stdout=PIPE, stderr=PIPE)
		dirnamedict[p] = dirname
		sleep(0.1) # launches process at different times

	return dirnamedict


def wait_processes(desired_output, dirnamedict):
	processes = list(dirnamedict.keys())
	#print("processes : ", processes)
	firstproc = None

	# wait until the last process terminates
	while len(processes) > 0 : #and firstproc is None :

		# check for terminated process
		for p in processes:
			if p.poll() is not None: # one of the process finished
				
				#print(f"Process terminated on code {p.returncode}")
				#for line in p.stdout:
				#	print(line)
				
				# TODO : prioritize keeping first half and last half before keeping both
				# if desired output
				if compare_output((p.returncode, p.stdout, p.stderr), desired_output) : 
					firstproc = p
					for ptokill in processes :
						ptokill.kill()

				# finalize the termination of the process
				processes.remove(p)
				p.communicate()
				break

		sleep(.1)
	
	return firstproc


# returns the index of the dirname that caused the first desired output when running commands
# returns -1 if none of them returned the desired output
def trigger_and_wait_processes(cmdargs, dirnamelist) :
	#print(dirnamelist)
	dirnamedict = trigger_processes(cmdargs.subcmdline_replaced, dirnamelist) # creates dirnamedict of process:dirname
	#print("proc dict : ", dirnamedict)
	firstproc = wait_processes(cmdargs.desired_output, dirnamedict.copy())
	#print("first process : ", firstproc)

	if firstproc is None :
		return None
	else :
		return dirnamedict.get(firstproc)
	

def make_new_dir() :
	i = 0
	dirname = str(i)
	while Path(dirname).exists() :
		i += 1
		dirname = str(i)
	Path(dirname).mkdir()
	return dirname


def prepare_dir(spbyfile, cmdargs) :
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
		dirname = prepare_dir(spbyfile, cmdargs)
		firstdirname = trigger_and_wait_processes(cmdargs, [dirname])
		rmtree(dirname)
		sp.subseqs.remove(seq1)

		# if the cut maintain the output, we keep cutting toward the center of the sequence
		if firstdirname is not None and firstdirname == dirname :
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
		dirname1 = prepare_dir(spbyfile, cmdargs)
		sp.subseqs.remove(seq1)		

		sp.subseqs.append(seq2)
		dirname2 = prepare_dir(spbyfile, cmdargs)

		sp.subseqs.append(seq1)
		dirname3 = prepare_dir(spbyfile, cmdargs)
		sp.subseqs.remove(seq1)
		sp.subseqs.remove(seq2)

		dirnames = list()
		if middle != end :
			dirnames.append(dirname1)
		if middle != begin :
			dirnames.append(dirname2)
		if middle != end and middle != begin :
			dirnames.append(dirname3)
		
		firstdirname = trigger_and_wait_processes(cmdargs, dirnames)
		rmtree(dirname1)
		rmtree(dirname2)
		rmtree(dirname3)

		# TODO : utiliser des elif au lieu des continue ?
		# case where the target fragment is in the first half
		if firstdirname is not None and firstdirname == dirname1 :
			print("case 1")
			sp.subseqs.append(seq1)
			tmpsubseqs.append(seq1)
			continue
		
		# case where the target fragment is in the second half
		if firstdirname is not None and firstdirname == dirname2 :
			print("case 2")
			sp.subseqs.append(seq2)
			tmpsubseqs.append(seq2)
			continue
		
		# case where there are two co-factor sequences
		# so we cut the seq in half and add them to the set to be reduced
		# TODO : relancer le check_output pour trouver les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		if firstdirname is not None and firstdirname == dirname3 :
			print("case 3")
			sp.subseqs.append(seq1)
			sp.subseqs.append(seq2)
			tmpsubseqs.append(seq1)
			tmpsubseqs.append(seq2)
			continue
		
		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		print("case 4")
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
		
		dirname = prepare_dir(spbyfile, cmdargs)
		firstdirname = trigger_and_wait_processes(cmdargs, [dirname])
		rmtree(dirname)

		if firstdirname is None :
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

		dirname = prepare_dir(spbyfile, cmdargs)
		firstdirname = trigger_and_wait_processes(cmdargs, [dirname])
		rmtree(dirname)

		if firstdirname is None :
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
			shutilcopy(filename, tmp_fname)

	except OSError :

		if Path(tmp_fname).is_file() :
			print(tmp_fname + " file already exists, unable to create it.")
			truncate = input("Do you want to truncate " + tmp_fname + " ? (y,n) ")
			if truncate == 'y' : 
				shutilcopy(filename, tmp_fname)
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
	
	resultdir = "Results"
	rmtree(resultdir, ignore_errors=True)
	Path(resultdir).mkdir()
	
	# writes the reduced seqs in files in a new directory
	sp_to_files(spbyfile, cmdargs, resultdir)
	
	print("Process number : " + str(NB_PROCESS))
	print_debug(spbyfile)
	if args.verbose :
		#print("\n", resultdir, " : ", sep="")
		#print_files_debug(resultdir)
		print("\nDone.")
