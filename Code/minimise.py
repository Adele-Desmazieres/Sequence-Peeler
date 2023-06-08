import sys
import string
import subprocess

TMP_FILENAME = "../tmp/tmp.fasta"
RESULTS_DIRECTORY = "../Results/"



# writes the sequences and their species in a fasta file
def seqs_to_file(seqs, filename) :
	f2 = open(filename, 'w')
	for header,seq in seqs.items() :
		f2.write("> " + str(header[0]) + ", position " + str(header[1]) + "\n" + seq + "\n")
	f2.close()


# check that the execution of exe with the sequences as input gives the desired output
# TODO : execute on the cluster
def check_output(seqs, exe, desired_output) :
	seqs_to_file(seqs, TMP_FILENAME)
	output = subprocess.run([exe, TMP_FILENAME], capture_output=True)

	#print("Sortie réelle : " + str((output.returncode, output.stdout, output.stderr)))
	
	checkreturn = desired_output[0] == None or desired_output[0] == output.returncode
	checkstdout = desired_output[1] == None or desired_output[1] == output.stdout
	checkstderr = desired_output[2] == None or desired_output[2] == output.stderr

	return (checkreturn and checkstdout and checkstderr)


# reduces the sequence by cutting begining or ending nucleotides
# cutting in half successively
# returns the new reduced sequence
def unequal_cut(seqs, sp_loc, exe, desired_output, imin, imax, flag_begining) :
	location = sp_loc[1]
	seq = seqs[sp_loc]
	tmp_seqs = seqs.copy()

	imid = (imin + imax) // 2
	print(seq, imin, imid, imax)

	if flag_begining :
		if imid == imin :
			return (seq[imin:], location+imin)
		tmp_seq = seq[imid:]
	else :
		if imid == imax :
			return (seq[:imax], location)
		tmp_seq = seq[:imid+1]
	
	tmp_seqs[sp_loc] = tmp_seq

	if (check_output(tmp_seqs, exe, desired_output)) :
		if flag_begining :
			return unequal_cut(tmp_seqs, sp_loc, exe, desired_output, imid, imax, flag_begining)
		else : 
			return unequal_cut(tmp_seqs, sp_loc, exe, desired_output, imin, imid+1, flag_begining)
	
	return (seq[imin:], location+imin) if flag_begining else (seq[:imax], location)


def strip_sequence(seqs, sp_loc, exe, desired_output, flag_begining) :

	seq = seqs[sp_loc]
	seq_ret = seq
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
		if imid == imin or imid == imax :
			found = True

		if flag_begining :
			seq1 = seq[imid:]
		else : 
			seq1 = seq[:imid]
		
		print(seq, imin, imid, imax)
		tmp_seqs[sp_loc] = seq1

		if check_output(tmp_seqs, exe, desired_output) :
			seq_ret = seq1
			if flag_begining :
				imin = imid
			else :
				imax = imid

		else :
			tmp_seqs[sp_loc] = seq
			if flag_begining :
				imax = imid
			else :
				imin = imid
		
	return seq_ret, sp_loc[1]




# NOT USED ANYMORE
# returns the new sequences dict with the reduced sequenced of the specified specie
# use recursive dichotomy
def dichotomy_cut_one_seq(seqs, specie, seq, exe, desired_output) : # TODO suppr seq
	icut = len(seq)//2
	print(seqs, icut)

	# if theres no more nucleotide in the sequence, returns it
	if (len(seq) == 0) :
		return seqs
	tmp_seqs = seqs.copy()

	begining = seq[:icut]
	end = seq[icut:]

	# case where the target fragment is in the first half
	tmp_seqs[specie] = begining
	if check_output(tmp_seqs, exe, desired_output) :
		return dichotomy_cut_one_seq(tmp_seqs, specie, begining, exe, desired_output)

	# case where the target fragment is in the second half
	tmp_seqs[specie] = end
	if check_output(tmp_seqs, exe, desired_output) :
		return dichotomy_cut_one_seq(tmp_seqs, specie, end, exe, desired_output)
	
	# case where the desired output is not obtained in previous cases
	# whether there is two target sequences in co-factor
	del tmp_seqs[specie]
	specie0 = specie+"0"
	specie1 = specie+"1"
	tmp_seqs[specie0] = begining
	tmp_seqs[specie1] = end
	if check_output(tmp_seqs, exe, desired_output) :
		tmp_seqs = dichotomy_cut_one_seq(tmp_seqs, specie0, begining, exe, desired_output)
		tmp_seqs = dichotomy_cut_one_seq(tmp_seqs, specie1, end, exe, desired_output)
		return tmp_seqs

	#del tmp_seqs[specie0]
	#del tmp_seqs[specie1]

	# whether the target sequence is on both sides of the cut
	tmp_seq = unequal_cut(seqs, specie, exe, desired_output, 0, len(seq)//2, True)
	seqs[specie] = tmp_seq # cuts the begining
	tmp_seq = unequal_cut(seqs, specie, exe, desired_output, 0, len(tmp_seq), False)
	seqs[specie] = tmp_seq # cuts the end
	return seqs


# returns the new sequences dict with the reduced sequenced of the specified specie
# use iterativ dichotomy
def dichotomy_cut_one_seq_iter(seqs, sp_loc, exe, desired_output) : 

	specie = sp_loc[0]
	location = sp_loc[1]
	location_tmp = location
	found = False

	while not found :
		print(seqs)

		seq = seqs[(specie, location)]

		seq0 = seq[:len(seq)//2]
		seqs[(specie, location)] = seq0
		if seq0 != seq and check_output(seqs, exe, desired_output) :
			print("case 1")
			continue
		else :
			del seqs[(specie, location)]

		seq1 = seq[len(seq)//2:]
		location_tmp += len(seq)//2
		seqs[(specie, location_tmp)] = seq1
		if seq1 != seq and check_output(seqs, exe, desired_output) :
			print("case 2")
			location = location_tmp
			continue
		else :
			del seqs[(specie, location_tmp)]

		sp0 = (specie, location)
		sp1 = (specie, location + len(seq)//2)
		seqs[sp0] = seq0
		seqs[sp1] = seq1
		if check_output(seqs, exe, desired_output) :
			print("case 3")
			seqs = dichotomy_cut_one_seq_iter(seqs, sp0, exe, desired_output)
			seqs = dichotomy_cut_one_seq_iter(seqs, sp1, exe, desired_output)
			break
		else : 
			del seqs[sp0]
			del seqs[sp1]

		print("case 4")
		seq3 = seq
		loc3 = location
		seqs[(specie, loc3)] = seq3
		seq3, loc3 = strip_sequence(seqs, (specie, loc3), exe, desired_output, True)
		seqs[(specie, loc3)] = seq3
		seq3, loc3 = strip_sequence(seqs, (specie, loc3), exe, desired_output, False)
		seqs[(specie, loc3)] = seq3
		location = loc3
		found = True
	
	return seqs


# returns every reduced sequences
def dichotomy_cut(seqs, exe, desired_output) :
	cutted_seqs = seqs.copy()

	for sp_loc,seq in seqs.items() :
		print("\n", sp_loc)
		# check if desired output is obtained whithout the sequence of the specie
		tmp_seqs = {k:v for k,v in cutted_seqs.items() if k != sp_loc}
		if check_output(tmp_seqs, exe, desired_output) :
			cutted_seqs = tmp_seqs
			print(cutted_seqs)
		
		# otherwise reduces the sequence
		else :
			cutted_seqs = dichotomy_cut_one_seq_iter(cutted_seqs, sp_loc, exe, desired_output)
		
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
	executablename = sys.argv[2]
	returncode = int(sys.argv[3])
	return (filename, executablename, (returncode, None, None))


if __name__=='__main__' :

	filename, executablename, desired_output = get_args()

	print("Desired output : " + str(desired_output))

	seqs = parsing(filename)
	cutted_seqs = dichotomy_cut(seqs, executablename, desired_output)
	print("\nMinimised sequences : \n" + str(cutted_seqs))
	seqs_to_file(cutted_seqs, RESULTS_DIRECTORY+"minimized.fasta")
	print("Done.")

	