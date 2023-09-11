# User interactions

* Allow relative paths [In progress]
* Control the number of subprocesses
* Move the -f before the input file
* Create a -m option for multiple file reduction
* Add -c for the command
* Verify presence of input files

# Code optimisations
* Create a task scheduler.
* Change static recursive calls with registrations to the task scheduler
* Implement a dependancy graph on executions. Will allow to abstract the jobs killing process.

# Documentation
* Explicit the long/short command line names

# Tests
* introduce pytests
* tests commandes:
	* 1 file in 0 out
	* 1 file in 1 out
	* fof in 0 out
	* fof in 1 out

# Functionalities
* Debug for paired reads (2 input files linked)

