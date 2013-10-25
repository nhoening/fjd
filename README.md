fjd
===

File-based job distribution on Unix-PCs. A straightforward pull-model for computational tasks,
working with the assumption that all CPUs/cores can access a shared home directory.


Usage
-------

  * Start one or more ``fjd-worker`` threads, like this::

    $ fjd-recruiter hire <number of workers>

  * Put jobs in the queue. You do this by putting a configuration file per job in the ``jobqueue`` directory. I'll talk about the details of these job files below and there is an example. 

  * Then, start a dispatcher::

    $ fjd-dispatcher

Now the ``fjd-dispatcher`` assigns jobs to ``fjd-worker`` threads who are currently not busy. This goes on until the job queue is empty.


Installation
-------------

::

    $ pip install fjd

If you do not have enough privileges (look for something like "Permission denied" in the output), install locally (for your user account only)::

    $ pip install fjd --user
    
If you do not have ``pip`` installed (I can't wait for everyone running Python 3.4), I made a `small script <https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL>`_. which should help to install all needed things. Download it and make it executable::
    
    $ wget https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL
    $ chmod +x INSTALL
    
Now you can install system-wide::
    
    $ ./INSTALL

or, if you do not have enough privileges, you can also install locally::
    
    $ source INSTALL --user
 
::
    
    If you installed locally, this should be added to your ``~/.bashrc`` or ``~/.profile`` file::

    export PATH=~/.local/bin:$PATH


How does fjd work, in a nutshell?
-----------------------------------

Small files in your home directory are used to indicate which jobs have to be done (these are created by you)
and which workers are available (these are created automatically). Files are also used by ``fjd`` to assign workers
to jobs.

This simple file-based approach makes ``fjd`` very easy to use.

For CPUs from several machines to work on your job queue, we make one necessary assumption: We assume that there 
is a shared home directory for logged-in users, which all machines can access. This setting is very common now
in universities and companies.

A little bit more detail about the ``fjd`` internals: 
The ``fjd-recruiter`` creates worker threads on one or more machines. The ``fjd-worker`` processes announce themselves in the
``workerqueue`` directory. The ``fjd-dispatcher`` finds your jobs in the ``jobqueue`` directory and pairs a job with an available worker.
It then removes those entries from the ``jobqueue`` and ``workerqueue`` directories and creates a new entry in ``jobpods``, where workers will
pick up their assignments. 

All of these directories exist in ``~/.fjd`` and will of course be created if they do not yet exist.


Job files
------------

A job file should adhere to the general configuration file standard, where ``fjd``
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
------------------------------------

You can see how it all comes together by looking at the simple example in the ``example``
directory where there is one script that represents a job (`example/ajob.py <https://raw.github.com/nhoening/fjd/master/fjd/example/ajob.py>`_) 
and one that creates ten jobs similar to the one we saw above and puts them in
the queue (`example/create_jobs.py <https://raw.github.com/nhoening/fjd/master/fjd/example/create_jobs.py>`_).

To run this example, create jobs using the second script, recruit some workers 
and start a dispatcher. Then, lean back and observe. We have a script that does
all of this in ``run-example.sh``::

    #/bin/bash

    python create_jobs.py
    fjd-recruiter hire 4
    fjd-dispatcher

And this is output similar to what you should see::

    $ cd fjd/example
    $ ./run-example.sh 
    [FJD] No workers busy in project "default" on localhost.
    [FJD] Hired 4 workers in project "default" on localhost.
    [FJD] Dispatcher started on project "default"
    [FJD] Found 10 jobs and 4 workers. Dispatching ...
    [FJD] Found 6 jobs and 1 workers. Dispatching ...
    [FJD] Found 5 jobs and 3 workers. Dispatching ...
    [FJD] Found 2 jobs and 1 workers. Dispatching ...
    [FJD] Found 1 jobs and 1 workers. Dispatching ...
    [FJD] No (more) jobs to dispatch.
    [FJD] Fired 4 workers in project "default" on localhost.


Note that the Dispatcher is started after jobs are created because per default, 
it will fire workers (kill screen sessions) and terminate itself once it finds 
the queue of jobs being empty. This behaviour can be overwritten with a parameter
if needed and then you could have the dispacther running and push jobs in the 
queue whenever you like.

And you'll see the results, the log files written by our example jobs::

    $ ls logfiles/
    job0.dat	job2.dat	job4.dat	job6.dat	job8.dat
    job1.dat	job3.dat	job5.dat	job7.dat	job9.dat

Workers are Unix screen sessions, you can see them by typing

    $ screen -ls

and inspect them if you want. By the way, you can always fire workers by hand:

    $ fjd-recruiter fire

Here is the log from a screen session of a worker if you're interested::

    $ fjd-worker --project default
    [FJD] Worker with ID nics-macbook.fritz.box_1382522062.31 started.
    [FJD] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [FJD] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.
    [FJD] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [FJD] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.


An example (using several machines in your network)
-----------------------------------------------------
TODO
