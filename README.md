fjd
===

File-based job distribution. A straightforward pull-model for computational tasks,
working with the assumption that all CPUs/cores can access a shared home directory.

Installation
-------------

    $ pip install fjd


Usage
-------

Start one or more workers, like this::

    $ recruiter.py hire <number of workers>

These will sit in Unix screen sessions and wait for job assignments.

Then, start a dispatcher::

    $ dispatcher.py

Now the dispatcher waits for jobs in the ``jobqueue`` directory.
Workers announce themselves in the ``workerqueue`` directory, where the dispatcher will
find them.
(These working directories will be created if they do not yet exist.)

All you have to do now is to put jobs in the queue. You do this by putting
a file per job in the ``jobqueue`` directory. The file should adhere to the
general configuration file standard. Here is an example::

    [control]
    executable: python test/ajob.py
    logfile: data/job0.dat 

    [params]
    param1: value0

Where you specify which command to execute and where results should go.

Your executable (the "job") gets this configuration file passed as a command line argument.
This way, it can see for itself in which logfile to write to.

Take care to get the relative paths correct (or simply make them absolute):
If the paths are relative, the path to the executable should be relative to the workers
working directory, whereas the path to the logfile should be relative to the jobs
working directory.

In addition, you can put other job-specific configuration in there for the executable
to see, as I did here in the ``[params]``-section (in fact, only the ``[control]``-section
is ``fjd``-specific).

You can see how it all comes together by looking at the simple example in the ``example``
directory where there is one script that represents a job and one that creates ten jobs
and puts them in the queue.

To run this example, run a script that creates the jobqueue. Recruit some workers
 and start a dispatcher. Then, lean back and observe. We have a script that does
all of this in `run-example.sh´::

    #/bin/bash

    python create_jobs.py
    recruiter.py hire 4
    dispatcher.py

And this is the output you should see::

    $ cd example
    $ ./run-example.sh 
    [FJD] Hired 4 workers on localhost.
    [FJD] Dispatcher started.
    [FJD] Found some jobs to dispatch
    [FJD] Found some jobs to dispatch
    [FJD] Found some jobs to dispatch
    [FJD] No more jobs to dispatch.

It does not matter in which order you do these three things - create jobs, hire workers and dispatch.
The workers patiently wait for jobs and the dispatcher waits for workers.

When all jobs are done (the dispatcher in the examnple quit because there were
none left), you can "fire" the workers::

    $ recruiter.py fire

And you'll see the results, the log files written by our example jobs::

    $ ls data/
    job0.dat	job2.dat	job4.dat	job6.dat	job8.dat
    job1.dat	job3.dat	job5.dat	job7.dat	job9.dat

