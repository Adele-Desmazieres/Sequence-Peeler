import sys
import string
import subprocess

TMP_FILENAME = "../tmp/tmp.fasta"


def seqs_to_file(seqs) :
	f2 = open(TMP_FILENAME, 'w')
	for specie,seq in seqs.items() :
		f2.write("> " + specie + "\n" + seq)
	f2.close()

def check_output(seqs, exe, desired_output) :
	seqs_to_file(seqs)
	output = subprocess.run([exe, TMP_FILENAME], capture_output=True)
	#print("Sortie capturée : " + str(output))
	rcode = output.returncode
	return rcode == desired_output

def dichotomy_cut_one_seq(seqs, specie, seq, icut, exe, desired_output) :
	print(seqs, icut)
	if (icut == 0) :
		return seqs
	tmp_seqs = seqs.copy()

	begining = seq[:icut]
	end = seq[icut:]

	tmp_seqs[specie] = begining
	if check_output(tmp_seqs, exe, desired_output) :
		return dichotomy_cut_one_seq(tmp_seqs, specie, begining, len(begining)//2, exe, desired_output)

	else :
		tmp_seqs[specie] = end
		if check_output(tmp_seqs, exe, desired_output) :
			return dichotomy_cut_one_seq(tmp_seqs, specie, end, len(end)//2, exe, desired_output)

		else : # TODO : CAS SPECIAL A MODIFIER PLUS TARD
			return seqs
		

def dichotomy_cut(seqs, exe, desired_output) :
	cutted_seqs = seqs.copy()

	for specie,seq in seqs.items() :
		print(specie)
		# tester si la sortie désirée persiste sans la séquence
		tmp_seqs = {k:v for k,v in cutted_seqs.items() if k != specie}
		if check_output(tmp_seqs, exe, desired_output) :
			cutted_seqs = tmp_seqs
		
		# il existe au moins un fragment de la séquence qui donne la sortie désirée
		else :
			cutted_seqs = dichotomy_cut_one_seq(cutted_seqs, specie, seq, len(seq)//2, exe, desired_output)
		
	return cutted_seqs


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
						sequences[specie] += line # concaténation de line avec le string précédent
		return sequences

	except IOError :
		print("Fichier introuvable.")


if __name__=='__main__' :
	filename = "../Data/example.fasta" # TODO : permettre l'execution depuis n'importe ou
	executablename = "../Data/dist/executable/executable"
	desired_output = 1
	print("Sortie désirée : " + str(desired_output))

	seqs = parsing(filename)
	cutted_seqs = dichotomy_cut(seqs, executablename, desired_output)
	print("Input minimisé : " + str(cutted_seqs))