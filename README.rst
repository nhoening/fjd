fjd
===

File-based distribution of jobs to CPUs on Unix-PCs (idle workers "pull" new jobs).
As assignments works via files, the hurdle to install and use should be very low.
Works under the assumption that all CPUs can access a shared home directory.


Usage
-------

* Start one or more ``fjd-worker`` threads, like this::

    $ fjd-recruiter hire <number of workers>

* Put jobs in the queue. You do this by putting a configuration file per job in the ``jobqueue`` directory. I'll talk about the details of these job files below and there is an example. 

* Then, start a dispatcher::

    $ fjd-dispatcher

Now the ``fjd-dispatcher`` assigns jobs to ``fjd-worker`` threads who are currently not busy. This goes on until the job queue is empty.

You can configure a number of hosts in your network and how many workers should be 
running on each (see an example of this below).


Installation
-------------

::

    $ pip install fjd

If you do not have enough privileges (look for something like "Permission denied" in the output), install locally (for your user account only)::

    $ pip install fjd --user
    
If you do not have ``pip`` installed (I can't wait for everyone running Python 3.4), I made a `small script <https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL>`_, which should help to install all needed things. Download it and make it executable::
    
    $ wget https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL
    $ chmod +x INSTALL
    
Now you can install system-wide::
    
    $ ./INSTALL

or, if you do not have enough privileges, you can also install locally::
    
    $ source INSTALL --user

**Note** - If you installed locally, this should be added to your ``~/.bashrc`` or ``~/.profile`` file::

    export PATH=~/.local/bin:$PATH

**Note** - Installing locally could be the better choice, because it might save you from installing ``fjd`` on each machine you want to use.
If they all share the home directory, they will all know about ``fjd`` once you are logged in. 


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
    [fjd-recruiter] Hired 4 workers in project "default".
    [fjd-dispatcher] Started on project "default"
    [fjd-dispatcher] Found 10 job(s) and 4 worker(s)...
    [fjd-dispatcher] Found 6 job(s) and 1 worker(s)...
    [fjd-dispatcher] Found 5 job(s) and 2 worker(s)...
    [fjd-dispatcher] Found 3 job(s) and 1 worker(s)...
    [fjd-dispatcher] Found 2 job(s) and 3 worker(s)...
    [fjd-dispatcher] No (more) jobs.
    [fjd-recruiter] Fired 4 workers in project "default".


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

and inspect them if you want (a feature is planned to give easy access to 
log output from the screen sessions).

Here is the log from a screen session of a worker if you're interested::

    $ fjd-worker --project default
    [fjd-worker] Started with ID nics-macbook.fritz.box_1382522062.31.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.

By the way, if screen sessions are running and you want them to stop (maybe
because you aborted the dispatcher before he could tell the recruiter to clean
up), then you can always fire workers by hand::

    $ fjd-recruiter fire



Another example (using several machines in your network and a custom project name)
------------------------------------------------------------------------------------

We can tell ´´fjd´´ about other machines in the network and how many workers we'd like
to employ on them. To do that, we place a file called ´´remote.conf´´in the project's
directory. Here is my file ´´example/remote.conf´´: If you run this example, 
you'll have to fill in names of machines in your particular network, of course::

    [host1]
    name: localhost
    workers: 3

    [host2]
    name: hyuga.sen.cwi.nl
    workers: 5


Normally, that directory is ~/.fjd/default. In this example, we tell ´´fjd´´ to
use a different project identifier (this way, you could have several projects
running without them getting into each other's way, i.e. stopping one project 
wouldn't stop the workers of the other and you wouldn't override the first project 
if you start another). Here is ``run-remote-example.sh``, using the project
identifier ´´remote-example´´::

    #/bin/bash

    python create_jobs.py remote-example
    cp remote.conf ~/.fjd/remote-example/remote.conf
    fjd-recruiter --project remote-example hire
    fjd-dispatcher --project remote-example 
 
If you run this example, the output you'll see should be similar to this:
 
    $ cd fjd/example
    $ ./run-remote-example.sh 
    [fjd-recruiter] Hired 3 workers in project "remote-example".
    [fjd-recruiter] Host hyuga.sen.cwi.nl: [fjd-recruiter] Hired 5 workers in project "remote-example".
    [fjd-dispatcher] Started on project "remote-example"
    [fjd-dispatcher] Found 10 job(s) and 8 worker(s)...
    [fjd-dispatcher] Found 2 job(s) and 4 worker(s)...
    [fjd-dispatcher] No (more) jobs.
    [fjd-recruiter] Fired 3 workers in project "remote-example".
    [fjd-recruiter] Host hyuga.sen.cwi.nl: [fjd-recruiter] Fired 5 workers in project "remote-example".

**Note** - If you normally have to type in a password to login to a remote machine via SSH,
you'll have to do this here, as well. Some SSH configuration can go a long way to ease your life,
e.g. by key management or the ControlAuto option. Ask your local IT guy. 
