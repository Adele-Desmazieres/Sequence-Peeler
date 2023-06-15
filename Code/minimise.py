import os
import os.path
import subprocess
import shutil
import argparse

TMPFILE = "tmp.fasta"
INPUTFILE = ""
CMD = ""

# writes the sequences and their species in a fasta file
def iseqs_to_file(iseqs, filename) :
	finput = open(INPUTFILE, 'r')
	f2 = open(filename, 'w')

	for (index, (specie, (begin, end))) in enumerate(iseqs.items()) :
		if index != 0 :
			f2.write("\n")
		s = specie
		s = specie.rstrip('#$') + " " + str(begin)
		f2.write(">" + s + "\n")
		finput.seek(begin)
		s = finput.read(end-begin)
		f2.write(s)
	
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


# reduces the sequence by cutting begining or ending nucleotides
# cutting in half successively, with an iterative dichotomy
# returns the new reduced sequence inside the dict sequences, and its new position
def strip_sequence(iseqs, specie, cmd, desired_output, wd, flag_begining) :
	(begin, end) = iseqs[specie]
	found = False
	
	if flag_begining :
		imin = begin
		imax = (begin+end) // 2
	else :
		imin = (begin+end) // 2
		imax = end

	while not found :

		imid = (imin + imax) // 2

		# stopping condition
		if imid == imin or imid == imax :
			loc = (imin, end) if flag_begining else (begin, imax)
			iseqs[specie] = loc
			found = True
			continue

		# get the most central quarter
		loc = (imid, end) if flag_begining else (begin, imid)
		iseqs[specie] = loc
		# if the cut maintain the output, we keep cutting toward the center of the sequence
		if check_output(iseqs, cmd, desired_output, wd) :
			if flag_begining :
				imin = imid
			else :
				imax = imid

		# else the cut doesn't maintain the output, so we keep cutting toward the exterior
		else :
			if flag_begining :
				imax = imid
			else :
				imin = imid
	
	return iseqs


# returns the new sequences dict with the reduced sequenced of the specified specie
# use an iterative dichotomy
def dichotomy_cut_one_seq_iter(iseqs, specie, cmd, desired_output, wd) : 

	found = False

	while not found :
		(begin, end) = iseqs[specie]
		middle = (begin + end) // 2

		# case where the target fragment is in the first half
		iseqs[specie] = (begin, middle)
		if middle != end and check_output(iseqs, cmd, desired_output, wd) :
			continue
		else :
			del iseqs[specie]

		# case where the target fragment is in the second half
		iseqs[specie] = (middle, end)
		if middle != end and check_output(iseqs, cmd, desired_output, wd) :
			continue
		else :
			del iseqs[specie]

		# case where there are two co-factor sequences
		# so we separate them under two different header
		sp0 = specie + "#"
		sp1 = specie + "$"
		iseqs[sp0] = (begin, middle)
		iseqs[sp1] = (middle, end)
		# TODO : relancer le check_output pour chopper les co-factors qui ne sont pas de part et d'autre du milieu de la séquence
		if check_output(iseqs, cmd, desired_output, wd) :
			iseqs = dichotomy_cut_one_seq_iter(iseqs, sp0, cmd, desired_output, wd)
			iseqs = dichotomy_cut_one_seq_iter(iseqs, sp1, cmd, desired_output, wd)
			break
		else : 
			del iseqs[sp0]
			del iseqs[sp1]

		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		iseqs[specie] = (begin, end)
		iseqs = strip_sequence(iseqs, specie, cmd, desired_output, wd, True)
		iseqs = strip_sequence(iseqs, specie, cmd, desired_output, wd, False)
		found = True
	
	return iseqs


# returns every reduced sequences
def dichotomy_cut(iseqs, cmd, desired_output, wd) :
	cutted_iseqs = iseqs.copy()
	for sp in iseqs.keys() :

		# check if desired output is obtained whithout the sequence of the specie
		tmp_iseqs = {k:v for k,v in cutted_iseqs.items() if k != sp} # TODO : éviter la copie
		if check_output(tmp_iseqs, cmd, desired_output, wd) :
			cutted_iseqs = tmp_iseqs
		
		# otherwise reduces the sequence
		else :
			cutted_iseqs = dichotomy_cut_one_seq_iter(cutted_iseqs, sp, cmd, desired_output, wd)

	print(cutted_iseqs)
	return cutted_iseqs


# returns the representation of a fasta file parsed in a dictionnary where
# the key is the specie header
# and the value is the tuple (begin, end) 
# they are the index of the characteres of the sequence in the file
# "begin" is included and "end" is excluded
# for example : {"Fraise":(8, 25), "Pomme":(33, 50)}
def parsing(filename) :
	try :
		with open(filename, 'r') as f :
			specie = None
			sequences = dict()
			c = 0

			for line in f :
				c += len(line)
				if line[0] == '>' :

					if specie != None :
						sequences[specie] = (sequences[specie][0], c-len(line)-1)

					specie = line[1:].rstrip('\n') + ", position 1"
					sequences[specie] = (c, c+1)

		sequences[specie] = (sequences[specie][0], c)
		return sequences

	except IOError :
		print("File not found.")


# remove the file TMPFILE
def rm_tmpfile() :
	os.remove(TMPFILE)


# create the file TMP which is a copy of the inputfile
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


# set the destination file to workdir/minimised.fasta if None
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

	args = get_args()
	desired_output = (args.returncode, args.stdout, args.stderr)
	wd = args.workdir if args.workdir[len(args.workdir)-1] != '/' else args.workdir[:-1]
	outputfile = get_outputfile(args.destfile, wd)
	TMPFILE = wd + "/" + TMPFILE

	init_tmpfile(args.filename)

	if args.verbose :
		print("Desired output : " + str(desired_output))
		print("Working directory : " + wd)
		print("Tmp filename : " + TMPFILE)
		print("Output filename : " + outputfile + "\n")

	INPUTFILE = args.filename
	iseqs = parsing(INPUTFILE)
	cutted_iseqs = dichotomy_cut(iseqs, args.cmdline, desired_output, wd)

	iseqs_to_file(cutted_iseqs, outputfile)
	rm_tmpfile()

	if args.verbose :
		print("\nMinimised sequences:")
		with open(outputfile) as f :
			print(f.read())
		print("\nDone.")

	