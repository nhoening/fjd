fjd
===

File-based job distribution. A straightforward pull-model for computational tasks,
working with the assumption that all CPUs/cores can access a shared home directory.


Usage
-------

First, start a dispatcher:
``python <path-to-fjd>/dispatcher.py``

Then, start one or more workers, like this:
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
 whereas the path to the logfile should be relative to the job).

Your executable gets this configuration file passed as a command line argument.
This way, it can see for itself in which logfile to write to.

In addition, you can put other job-specific configuration in there for the exeuctable
to see, as I did here in the ``[params]``-section (in fact, only the ``[meta]``-section
is ``fjd``-specific).

You can see how it all comes together by looking at the simple example in the ``test``
directory where there is one script that represents a job and one that creates ten jobs
and puts them in the queue.

