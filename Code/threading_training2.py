import subprocess
import multiprocessing
import os

assert os.uname == 'posix', "Fonctionn eseulement sur Linux"

'''
def run_subprocess(cmd, i, return_codes):
	print("begin", str(i)) 
	return_codes[i] = -2
	
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	
	p.wait()
	stdout = p.communicate()[0]
	stdout = stdout.decode().rstrip()
	print("cmd", i, ":", stdout)
	
	r = ("0" in stdout)
	if r :
		print(True)
		return_codes[i] = 1
	else :
		return_codes[i] = 0
		
	print("end", str(i)) 
		
	return r


def main():
	# List of commands to execute in parallel
	commands = [
		"ls -r  > /dev/null && date '+%N'",
		"ls -r  > /dev/null && date '+%N'",
		"ls -r  > /dev/null && date '+%N'", 
		"ls -r  > /dev/null && date '+%N'", 
		"ls -r  > /dev/null && date '+%N'", 
		"ls -r  > /dev/null && date '+%N'", 
		"ls -r  > /dev/null && date '+%N'",
		"ls -r  > /dev/null && date '+%N'",
		"ls -r  > /dev/null && date '+%N'",
		"ls -r  > /dev/null && date '+%N'"
	]

	# Create a list to store the subprocess objects
	processes = []
	n = len(commands)
	manager = multiprocessing.Manager()
	return_codes = manager.dict()
	for i in range(n) :
		return_codes[i] = -3

	# Launch the subprocesses
	for i in range(n):
		process = multiprocessing.Process(target=run_subprocess, args=(commands[i], i, return_codes))
		process.start()
		processes.append(process)

	# Flag to track if a process with the desired return code has finished
	finished_with_return_code = False
	first_process = None
	
	# Check if any process has finished with the desired return code
	i = 0
	while not finished_with_return_code :
		process = processes[i]
		#process.join()
		if not process.is_alive() and return_codes[i] :
			first_process = process
			finished_with_return_code = True
		i = (i + 1) % n

	# Terminate the remaining processes if needed
	for i in range(n):
		process = processes[i]
		if process.is_alive():
			print("terminating", i)
			process.terminate()

	print("One of the processes has finished with the desired return code.")
	print(first_process)
	for k,v in return_codes.items() :
		print("process", k, "state:", v)
'''

subprocesses = []
subprocesses.append(subprocess.Popen(['/usr/bin/sleep', '2']))
subprocesses.append(subprocess.Popen(['/usr/bin/sleep', '1']))
subprocesses.append(subprocess.Popen(['/usr/bin/sleep', '3']))
subprocesses = {sp.id:sp for sp in subprocesses}


while subprocesses :

	pid, status = os.waitpid(-1)
	del subprocess[pid]

	if status :
		pass



if __name__ == "__main__":
	main()