fjd
===

File-based job distribution. A straightforward pull-model for computational tasks,
working with the assumption that all CPUs/cores can access a shared home directory.


Usage
-------

First, start a dispatcher:
``python <path-to-fjd>/dispatcher.py``

Them start one or more workers like this:
``python <path-to-fjd>/worker.py``

Now the dispatcher waits for jobs in the ``jobqueue`` directory (which it creates if 
it does not yet exist).
Workers announce themselves in the ``workerqueue`` directory, where the dispatcher will
find them.

All you have to do now is to put jobs in the queue. You do this by putting
a file per job in the ``jobqueue`` directory. The file should adhere to the
general configuration file standard. Here is an example:

    [meta]
    executable: python test/ajob.py
    logfile:data/job0.dat 

    [params]
    param1:value0

Where you specify which command to execute and where results should go
(note: if the path to the executable is relative, it should be relative to the worker,
 while the logfile should be relative to the job).

Your executable gets this configuration file passed as a command line parameters,
so it can access in which logfile to write to and which parameters it needs
to adhere to (only the ``[meta]`` - section is ``fjd``-specific, actually).

You can see how that works by the simple example in the ``test`` directory.



