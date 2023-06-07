import sys
import string
import subprocess

TMP_FILENAME = "../tmp/tmp.fasta"
RESULTS_DIRECTORY = "../Results/"



# writes the sequences and their species in a fasta file
def seqs_to_file(seqs, filename) :
	f2 = open(filename, 'w')
	for specie,seq in seqs.items() :
		f2.write("> " + specie + "\n" + seq + "\n")
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
def unequal_cut(seqs, specie, seq, exe, desired_output, imin, imax, flag_begining) :
	tmp_seqs = seqs.copy()
	imid = (imin + imax) // 2

	#print(seq, imin, imid, imax)

	if flag_begining :
		if imid == imin :
			return seq[imin:]
		tmp_seq = seq[imid:]
	else :
		if imid == imax :
			return seq[:imax]
		tmp_seq = seq[:imid+1]
	
	tmp_seqs[specie] = tmp_seq

	if (check_output(tmp_seqs, exe, desired_output)) :
		if flag_begining :
			return unequal_cut(tmp_seqs, specie, seq, exe, desired_output, imid, imax, flag_begining)
		else : 
			return unequal_cut(tmp_seqs, specie, seq, exe, desired_output, imin, imid+1, flag_begining)
	
	return seq[imin:] if flag_begining else seq[:imax]


# returns the new sequences dict with the reducded sequenced of the specified specie
def dichotomy_cut_one_seq(seqs, specie, seq, exe, desired_output) : # TODO suppr seq des args
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
	tmp_seq = unequal_cut(seqs, specie, seq, exe, desired_output, 0, len(seq)//2, True)
	seqs[specie] = tmp_seq # cuts the begining
	tmp_seq = unequal_cut(seqs, specie, tmp_seq, exe, desired_output, 0, len(tmp_seq), False)
	seqs[specie] = tmp_seq # cuts the end
	return seqs


# returns every reduced sequences
def dichotomy_cut(seqs, exe, desired_output) :
	cutted_seqs = seqs.copy()

	for specie,seq in seqs.items() :
		print(specie)
		# check if desired output is obtained whithout the sequence of the specie
		tmp_seqs = {k:v for k,v in cutted_seqs.items() if k != specie}
		if check_output(tmp_seqs, exe, desired_output) :
			cutted_seqs = tmp_seqs
			print(cutted_seqs)
		
		# otherwise reduces the sequence
		else :
			cutted_seqs = dichotomy_cut_one_seq(cutted_seqs, specie, seq, exe, desired_output)
		
	return cutted_seqs

# returns the representation of a fasta file by a dictionnary where
# the key is the specie header, and the value is the specie sequence
# for example : {"Fraise":"ATTCG", "Pomme":"GGGGCTC"}
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
						sequences[specie] = ""
					elif specie != None : 
						sequences[specie] += line # concatenate line to the previous string
		return sequences

	except IOError :
		print("File not found.")


def get_args() :
	filename = sys.argv[1]
	executablename = sys.argv[2]
	returncode = int(sys.argv[3])
	return (filename, executablename, (returncode, None, None))


if __name__=='__main__' :
	#filename = "../Data/example2.fasta" 
	#executablename = "../Data/dist/executable/executable"

	#returncode = 1
	#stdout = None
	#stderr = None
	#desired_output = (returncode, stdout, stderr)

	filename, executablename, desired_output = get_args()

	print("Desired output : " + str(desired_output))

	seqs = parsing(filename)
	cutted_seqs = dichotomy_cut(seqs, executablename, desired_output)
	print("\nMinimised sequences : \n" + str(cutted_seqs))
	seqs_to_file(cutted_seqs, RESULTS_DIRECTORY+"minimized.fasta")
	print("Done.")

	