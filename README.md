fjd
===

File-based job distribution. A straightforward pull-model for computational tasks,
working with the assumption that all CPUs/cores can access a shared home directory.

Installation
-------------

    $ pip install fjd


Usage
-------

  * Start one or more workers, like this::

    $ fjd-recruiter hire <number of workers>


  * Put jobs in the queue. You do this by putting a file per job in the ``jobqueue``directory. I'll talk about the details of thesejob files in a minute. 

  * Then, start a dispatcher::

    $ fjd-dispatcher

Now the dispatcher assigns jobs to workers until all jobs are done.

A little bit more detailled: The dispacther finds jobs in the ``jobqueue`` directory.
Workers announce themselves in the ``workerqueue`` directory. The dispatcher 
pairs a job with a worker, removes those entries from ``jobqueue``
and ``workerqueue`` and creates a new entry in ``jobpods``, where workers will
pick up their assignments.
Of course, these working directories will be created if they do not yet exist.


Job files
------------

A job file should adhere to the general configuration file standard, where fjd
only has some requirements for the ``control`` section, where you specify which
command to execute and where results should go. Here is an example::

    [control]
    executable: python example/ajob.py
    logfile: logfiles/job0.dat 

    [params]
    param1: value0


Your executable (the "job") gets this configuration file passed as a command line argument.
This way, it can see for itself in which logfile to write to.

Take care to get the relative paths correct (or simply make them absolute):
If the paths are relative, the path to the executable should be relative to the workers
working directory, whereas the path to the logfile should be relative to the jobs
working directory.

In addition, you can put other job-specific configuration in there for the executable
to see, as I did here in the ``[params]``-section (in fact, only the ``[control]``-section
is ``fjd``-specific).


An example (on your local machine)
---------------------------------

You can see how it all comes together by looking at the simple example in the ``example``
directory where there is one script that represents a job and one that creates ten jobs
similar to the one we saw above and puts them in the queue.

To run this example, create jobs using the script, recruit some workers 
and start a dispatcher. Then, lean back and observe. We have a script that does
all of this in ``run-example.sh``::

    #/bin/bash

    python create_jobs.py
    fjd-recruiter hire 4
    fjd-dispatcher

And this is the output you should see::

    $ cd fjd/example
    $ ./run-example.sh 
    [FJD] Hired 4 workers on localhost.
    [FJD] Dispatcher started.
    [FJD] Found 10 jobs and 4 workers. Dispatching ...
    [FJD] Found 6 jobs and 4 workers. Dispatching ...
    [FJD] Found 2 jobs and 4 workers. Dispatching ...
    [FJD] No (more) jobs to dispatch.
    [FJD] Fired 4 workers on localhost.


Note that the Dispatcher is started after jobs are created because per default, 
it will fire workers and terminate itself once it finds the queue of jobs being empty.
This behaviour can be overwritten with a parameter if needed and then you could 
have the dispacther running and push jobs in the queue whenever you like.

And you'll see the results, the log files written by our example jobs::

    $ ls logfiles/
    job0.dat	job2.dat	job4.dat	job6.dat	job8.dat
    job1.dat	job3.dat	job5.dat	job7.dat	job9.dat

Workers are Unix screen sessions, you can see them by typing

    $ screen -ls

and inspect them if you want. By the way, you can always fire workers by hand:

    $ fjd-recruiter fire


An example (using several machines in your network)
-----------------------------------------------------
TODO
