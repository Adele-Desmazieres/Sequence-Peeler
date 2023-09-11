from os import path, mkdir
from sys import stderr
from shutil import rmtree


class SequenceHolder:
	""" Remembers the absolute positions of a sequence in a file (in Bytes)
	"""
	def __init__(self, left, right):
		self.left = left # First byte of the sequence
		self.right = right # Last byte of the sequence

	def size(self):
		return self.right - self.left + 1

	def copy(self):
		return SequenceHolder(self.left, self.right)

	def __repr__(self):
		return f"({self.left} : {self.right})"


class FileManager:
	def __init__(self, filename):
		# Managing file absence
		if not path.isfile(filename):
			print(f"{filename} does not exists", file=stderr)
			raise FileNotFoundError(filename)

		# Transform file path to absolute
		self.filename = path.abspath(filename)
		self.index = None
		self.total_seq_size = 0
		self.verbose = False


	def __repr__(self):
		if self.verbose:
			s = f"FileManager({self.filename}):\n"
			s += '\n'.join([f"\t{header}: {str(self.index[header])}" for header in self.index])
			return s
		else:
			return f"FileManager({self.filename}): {len(self.index)} indexed sequences"


	def _index_sequence(self, header, seqstart, filepos):
		if header is not None:
			if header in self.index:
				# Multiple identical headers in the file
				print(f"WARNING: header {header} is present more than once in the file {filename}. Only hte last one have been kept", file=stderr)
				self.total_seq_size -= self.index[header].size()
			self.index[header] = SequenceHolder(seqstart, filepos-1)
			self.total_seq_size += self.index[header].size()


	def index_sequences(self):
		""" Index the positions of the sequences in the file.
			TODO: keep track of the sequence order
		"""
		self.index = {}

		with open(self.filename) as f:
			header = None
			seqstart = 0
			filepos = 0

			for line in f:
				# new header
				if line[0] == '>':
					# register previous seq
					self._index_sequence(header, seqstart, filepos)

					# set new seq values
					header = line[1:].strip()
					seqstart = filepos + len(line)
				
				filepos += len(line)

			# last sequence
			self._index_sequence(header, seqstart, filepos)


	def copy(self):
		copy = FileManager(self.filename)
		
		copy.index = None if self.index is None else {}
		if self.index is not None:
			for name in self.index:
				copy.index[name] = self.index[name].copy()

		copy.total_seq_size = self.total_seq_size
		other.verbose = self.verbose


class ExperimentContent:
	def __init__(self):
		self.input_files = {}
		self.output_files = {}

	def copy(self):
		copy = ExperimentContent()

		copy.input_files = {name: self.input_files[name].copy() for name in self.input_files}
		copy.output_files = {name: self.output_files[name] for name in self.output_files}

		return copy


class ExperimentDirectory:
	""" Experiment Directory manager. Will copy, erase and keep track of files for one experiment
	"""

	def next_dirname(parentpath):
		""" Return an available directory name for the directory parentpath (not thread safe)
		"""
		# verify existance of parent directory
		if not path.isdir(parentpath):
			raise FileNotFoundError(parentpath)
		
		idx = 0
		while True:
			if not path.exists(path.join(parentpath, str(idx))):
				return idx
			idx += 1


	def __init__(self, parentpath, dirname=None, delete_previous=True):
		if dirname is None:
			dirname = ExperimentDirectory.next_dirname(parentpath)

		# verify existance of parent directory
		if not path.isdir(parentpath):
			raise FileNotFoundError(parentpath)
		self.parentpath = path.abspath(parentpath)
		self.dirpath = path.join(self.parentpath, dirname)

		# Verify existance of directory
		if path.isdir(self.dirpath):
			if delete_previous:
				rmtree(self.dirpath)
			else:
				raise FileExistsError(self.dirpath)
		# create the experiment directory
		mkdir(self.dirpath)


	def clean(self):
		rmtree(self.dirpath)

			
