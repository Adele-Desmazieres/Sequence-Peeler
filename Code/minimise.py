import sys
import subprocess
import shutil

TMP_FILENAME = "../tmp/tmp.fasta"
RESULTS_DIRECTORY = "../Results/"



# writes the sequences and their species in a fasta file
def seqs_to_file(seqs, filename) :
	f2 = open(filename, 'w')

	for index,(header,seq) in enumerate(seqs.items()) :
		if index != 0 :
			f2.write("\n")
		f2.write("> " + str(header[0]) + ", position " + str(header[1]) + "\n" + seq)
	
	f2.close()


# check that the execution of cmd with the sequences as input gives the desired output
# TODO : execute on the cluster
def check_output(seqs, cmd, desired_output) :
	seqs_to_file(seqs, TMP_FILENAME)
	output = subprocess.run(cmd, shell=True, capture_output=True)

	#print("Exe output : " + str((output.returncode, output.stdout, output.stderr)))
	
	checkreturn = desired_output[0] == None or desired_output[0] == output.returncode
	checkstdout = desired_output[1] == None or desired_output[1] == output.stdout
	checkstderr = desired_output[2] == None or desired_output[2] == output.stderr

	return (checkreturn and checkstdout and checkstderr)


# reduces the sequence by cutting begining or ending nucleotides
# cutting in half successively, with an iterative dichotomy
# returns the new reduced sequence inside the dict sequences, and its new position
def strip_sequence(seqs, sp_loc, cmd, desired_output, flag_begining) :
	seq = seqs[sp_loc]
	seq_ret = seq # the result when it will be reduced
	loc_ret = sp_loc[1]
	tmp_seqs = seqs.copy()
	found = False
	
	if flag_begining :
		imin = 0
		imax = len(seq)//2
	else :
		imin = len(seq)//2
		imax = len(seq)

	while not found :

		imid = (imin + imax) // 2
		# stopping condition
		if imid == imin or imid == imax :
			found = True

		#print(seq, imin, imid, imax)

		seq1 = seq[imid:] if flag_begining else seq[:imid]
		tmp_seqs[sp_loc] = seq1

		# the cut maintained the output, we keep cutting toward the center of the sequence
		if check_output(tmp_seqs, cmd, desired_output) :
			seq_ret = seq1
			if flag_begining :
				imin = imid
				loc_ret = sp_loc[1] + imid
			else :
				imax = imid

		# else the cut didn't maintain the output, we keep cutting toward the exterior
		else :
			tmp_seqs[sp_loc] = seq
			if flag_begining :
				imax = imid
			else :
				imin = imid
	
	# we delete the old sequence from the dict, and add the new one with its new position
	del seqs[sp_loc]
	seqs[(sp_loc[0], loc_ret)] = seq_ret
	return seqs, loc_ret


# returns the new sequences dict with the reduced sequenced of the specified specie
# use an iterative dichotomy
def dichotomy_cut_one_seq_iter(seqs, sp_loc, cmd, desired_output) : 

	specie = sp_loc[0]
	location = sp_loc[1]
	location_tmp = location
	found = False

	while not found :
		#print(seqs)

		seq = seqs[(specie, location)]

		# case where the target fragment is in the first half
		seq0 = seq[:len(seq)//2]
		seqs[(specie, location)] = seq0
		if seq0 != seq and check_output(seqs, cmd, desired_output) :
			continue
		else :
			del seqs[(specie, location)]

		# case where the target fragment is in the second half
		seq1 = seq[len(seq)//2:]
		location_tmp += len(seq)//2
		seqs[(specie, location_tmp)] = seq1
		if seq1 != seq and check_output(seqs, cmd, desired_output) :
			location = location_tmp
			continue
		else :
			del seqs[(specie, location_tmp)]

		# case where there is two sequences in co-factor in the sequence
		# so we separate them under two different header
		sp0 = (specie, location)
		sp1 = (specie, location + len(seq)//2)
		seqs[sp0] = seq0
		seqs[sp1] = seq1
		if check_output(seqs, cmd, desired_output) :
			seqs = dichotomy_cut_one_seq_iter(seqs, sp0, cmd, desired_output)
			seqs = dichotomy_cut_one_seq_iter(seqs, sp1, cmd, desired_output)
			break
		else : 
			del seqs[sp0]
			del seqs[sp1]

		# case where the target sequence is on both sides of the cut
		# so we strip first and last unnecessary nucleotids
		seqs[(specie, location)] = seq
		seqs, location = strip_sequence(seqs, (specie, location), cmd, desired_output, True)
		seqs, location = strip_sequence(seqs, (specie, location), cmd, desired_output, False)
		found = True
	
	return seqs


# returns every reduced sequences
def dichotomy_cut(seqs, cmd, desired_output) :
	cutted_seqs = seqs.copy()

	for sp_loc,seq in seqs.items() :
		#print("\n", sp_loc)

		# check if desired output is obtained whithout the sequence of the specie
		tmp_seqs = {k:v for k,v in cutted_seqs.items() if k != sp_loc}
		if check_output(tmp_seqs, cmd, desired_output) :
			cutted_seqs = tmp_seqs
			print(cutted_seqs)
		
		# otherwise reduces the sequence
		else :
			cutted_seqs = dichotomy_cut_one_seq_iter(cutted_seqs, sp_loc, cmd, desired_output)
		
	return cutted_seqs


# returns the representation of a fasta file by a dictionnary where
# the key is the specie header and the location of the sequence
# and the value is the specie sequence
# for example : {("Fraise",0):"ATTCG", ("Pomme",0):"GGGGCTC"}
def parsing(filename) :
	try :
		with open(filename, 'r') as f :
			specie = None
			sequences = dict()

			for line in f :
				line = line.strip()
				if len(line) >= 1 : 

					if line[0] == '>' :
						specie = line[1:].strip()
						sequences[(specie, 1)] = ""

					elif specie != None : 
						sequences[(specie, 1)] += line # concatenate line to the previous string

		return sequences

	except IOError :
		print("File not found.")


def get_args() :
	filename = sys.argv[1]
	cmdline = sys.argv[2]
	returncode = int(sys.argv[3])
	return (filename, cmdline, (returncode, None, None))


if __name__=='__main__' :

	# TODO ? lancer une fois l'executable sur tout le fichier pour check que l'output est bien possible ?

	filename, cmdline, desired_output = get_args()
	shutil.copy(filename, TMP_FILENAME)

	print("Desired output : " + str(desired_output))

	seqs = parsing(filename)
	cutted_seqs = dichotomy_cut(seqs, cmdline, desired_output)
	print("Minimised sequences : \n" + str(cutted_seqs))
	seqs_to_file(cutted_seqs, RESULTS_DIRECTORY+"minimised.fasta")
	print("Done.")

	