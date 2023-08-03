#!/bin/python3

from time import sleep, time, gmtime, strftime
from pathlib import Path
from subprocess import Popen
from subprocess import PIPE
from shutil import rmtree
import argparse

NB_PROCESS_STARTED_SEQUENTIAL = 0
NB_PROCESS_ENDED_SEQUENTIAL = 0
NB_PROCESS_STARTED_PARALLEL = 0
NB_PROCESS_ENDED_PARALLEL = 0
NB_PROCESS_INTERRUPTED = 0
CHUNK_SIZE = 200_000_000 # char number, string of about 0.8 Go


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
		if nofof :
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


class PopenExtended(Popen) :

	def __init__(self, args, bufsize=-1, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None, universal_newlines=None, startupinfo=None, creationflags=0, restore_signals=True, start_new_session=False, pass_fds=(), *, encoding=None, errors=None, text=None, prioritised=True) :
		self.prioritised = prioritised # new attribute
		super().__init__(args=args, bufsize=bufsize, executable=executable, stdin=stdin, stdout=stdout, stderr=stderr, preexec_fn=preexec_fn, close_fds=close_fds, shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines, startupinfo=startupinfo, creationflags=creationflags, restore_signals=restore_signals, start_new_session=start_new_session, pass_fds=pass_fds, encoding=encoding, errors=errors, text=text)


def printset_debug(iseqs) :
	for sp in list(iseqs) :
		print(sp)

def print_debug(spbyfile) :
	print("ACTUAL STATE")
	for iseqs in spbyfile :
		printset_debug(iseqs)
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
			while ic < begin :
				if ic + CHUNK_SIZE < begin :
					nb_line_breaks += inputfile.read(CHUNK_SIZE).count('\n')
					ic += CHUNK_SIZE
				else :
					nb_line_breaks += inputfile.read(begin-ic).count('\n')
					ic = begin
			
			#print("line breaks =", nb_line_breaks)
			
			# writes the header
			firstnuclsubseq = begin - firstcharseq + 1 - nb_line_breaks
			header = sp.header + ", position " + str(firstnuclsubseq)
			outputfile.write(">" + header + "\n")
			
			# read the subseq from the input and writes it in the output
			inputfile.seek(begin)
			ic = begin
			while ic < end :
				if ic + CHUNK_SIZE < end :
					actual_subseq = inputfile.read(CHUNK_SIZE)
					outputfile.write(actual_subseq)
					ic += CHUNK_SIZE
				else :
					actual_subseq = inputfile.read(end-begin)
					outputfile.write(actual_subseq)
					ic = end

			#actual_subseq = inputfile.read(end-begin)
			#outputfile.write(actual_subseq)
	
	inputfile.close()
	outputfile.close()


def get_output_filename(filename, cmdargs, dirname) :
	name = cmdargs.fileregister.get(filename)
	return dirname + "/" + name


# writes the content of the fof in specified directory
# and call the function that writes the content of the files of the fof
def sp_to_files(spbyfile, cmdargs, dirname) :

	if cmdargs.nofof : 
		iseqs = spbyfile[0]
		if len(iseqs) != 0 :
			inputfilename = iseqs[0].filename
			outputfilename = get_output_filename(inputfilename, cmdargs, dirname)
			iseqs_to_file(spbyfile[0], inputfilename, outputfilename)
		
		# makes the empty file
		else :
			open(get_output_filename(cmdargs.infilename, cmdargs, dirname), 'w').close()
		
		return None

	files_to_truncate = cmdargs.get_all_infiles()
	outfofname = get_output_filename(cmdargs.infilename, cmdargs, dirname)
	
	try :
		with open(outfofname, 'w') as fof :
			
			for (i, iseqs) in enumerate(spbyfile) :
				
				if len(iseqs) != 0 :
					
					inputfilename = iseqs[0].filename
					outputfilename = get_output_filename(inputfilename, cmdargs, dirname)

					# writes its name in the file of files
					if i != 0 :
						fof.write("\n")
					fof.write(Path(outputfilename).name)
		
					# call the function that writes the content of the file
					iseqs_to_file(iseqs, inputfilename, outputfilename)

					files_to_truncate.remove(iseqs[0].filename)
				
			for f in files_to_truncate :
				open(get_output_filename(f, cmdargs, dirname), 'w').close()
					
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
def trigger_processes(cmdline, dirnamelist, priorities):
	global NB_PROCESS_STARTED_SEQUENTIAL
	global NB_PROCESS_STARTED_PARALLEL

	dirnamedict = dict()
	nb_proc = len(dirnamelist)

	for i in range(nb_proc):
		dirname = dirnamelist[i]
		#print("Process running in:", dirname)
		p = PopenExtended(cmdline, shell=True, cwd=dirname, stdout=PIPE, stderr=PIPE, prioritised=priorities[i])
		dirnamedict[p] = dirname
		#sleep(0.1) # launches processes at different times

	if nb_proc == 1 :
		NB_PROCESS_STARTED_SEQUENTIAL += nb_proc
	else :
		NB_PROCESS_STARTED_PARALLEL += nb_proc

	return dirnamedict


def wait_processes(desired_output, dirnamedict):
	global NB_PROCESS_ENDED_SEQUENTIAL
	global NB_PROCESS_INTERRUPTED

	processes = list(dirnamedict.keys())
	nb_proc = len(dirnamedict)
	firstproc = None
	tmpproc = None

	# wait until the last process terminates
	while len(processes) > 0 : #and firstproc is None :

		# check for terminated process
		for p in processes:
			if p.poll() is not None: # one of the processes finished
				
				processes.remove(p)
				
				# if desired output
				if compare_output((p.returncode, p.stdout, p.stderr), desired_output) :

					if not p.prioritised :
						tmpproc = p
					
					else :
						firstproc = p
						for ptokill in processes :
							ptokill.kill()
							NB_PROCESS_INTERRUPTED += 1

				# finalize the termination of the process
				p.communicate()
				break

		sleep(.001)
	
	if nb_proc == 1 :
		NB_PROCESS_ENDED_SEQUENTIAL += 1

	return firstproc if firstproc is not None else tmpproc


# returns the index of the dirname that caused the first desired output when running commands
# returns -1 if none of them returned the desired output
def trigger_and_wait_processes(cmdargs, dirnamelist, priorities=None) :
	#print(dirnamelist)
	if priorities is None :
		priorities = [True for x in dirnamelist]
	dirnamedict = trigger_processes(cmdargs.subcmdline_replaced, dirnamelist, priorities) # creates dirnamedict of process:dirname
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
		priorities = list()
		if middle != end :
			dirnames.append(dirname1)
			priorities.append(True)
		if middle != begin :
			dirnames.append(dirname2)
			priorities.append(True)
		if middle != end and middle != begin :
			dirnames.append(dirname3)
			priorities.append(False)
		
		#print("nombre de proc simultannés : ", len(dirnames))
		
		firstdirname = trigger_and_wait_processes(cmdargs, dirnames, priorities)
		rmtree(dirname1)
		rmtree(dirname2)
		rmtree(dirname3)

		# TODO : utiliser des elif au lieu des continue ?
		# case where the target fragment is in the first half
		if firstdirname is not None and firstdirname == dirname1 :
			#print("case 1")
			sp.subseqs.append(seq1)
			tmpsubseqs.append(seq1)
			continue
		
		# case where the target fragment is in the second half
		if firstdirname is not None and firstdirname == dirname2 :
			#print("case 2")
			sp.subseqs.append(seq2)
			tmpsubseqs.append(seq2)
			continue
		
		# case where there are two co-factor sequences
		# so we cut the seq in half and add them to the set to be reduced
		# TODO : relancer le check_output pour trouver les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		if firstdirname is not None and firstdirname == dirname3 :
			#print("case 3")
			sp.subseqs.append(seq1)
			sp.subseqs.append(seq2)
			tmpsubseqs.append(seq1)
			tmpsubseqs.append(seq2)
			continue
		
		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		#print("case 4")
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

	for sp in iseqs :
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

	for iseqs in spbyfile :
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


if __name__=='__main__' :

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
	
	#print_debug(spbyfile)
	NB_PROCESS_ENDED_PARALLEL = NB_PROCESS_STARTED_PARALLEL - NB_PROCESS_INTERRUPTED
	print("NB_PROCESS_STARTED_SEQUENTIAL : " + str(NB_PROCESS_STARTED_SEQUENTIAL))
	print("NB_PROCESS_ENDED_SEQUENTIAL : " + str(NB_PROCESS_ENDED_SEQUENTIAL))
	print("NB_PROCESS_STARTED_PARALLEL : " + str(NB_PROCESS_STARTED_PARALLEL))
	print("NB_PROCESS_ENDED_PARALLEL : " + str(NB_PROCESS_ENDED_PARALLEL))
	print("NB_PROCESS_INTERRUPTED : " + str(NB_PROCESS_INTERRUPTED))

	duration = time() - starttime
	print("Duration: " + strftime("%H:%M:%S", gmtime(duration)))

	if args.verbose :
		print("\n", resultdir, " : ", sep="")
		print_files_debug(resultdir)
		print("\nDone.")
