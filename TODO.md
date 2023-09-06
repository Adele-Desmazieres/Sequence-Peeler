User interactions:
* Allow relative paths
* Control the number of subprocesses
* Move the -f before the input file
* Add -c for the command
* Add the possibility to have long/short command line names

Code optimisations:
* Create a task scheduler.
* Change static recursive calls with registrations to the task scheduler
* Implement a dependancy graph on executions. Will allow to abstract the jobs killing process.
