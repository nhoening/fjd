fjd
===

``fjd`` makes it easy to run computational jobs on many CPUs.

There are several powerful tools for dispatching dynamic lists of computational jobs to multiple, possibly distributed CPUs. However, for simple use cases, the effort of installation and setup is often too high.


With ``fjd``, the hurdle to get started is very low. Installation is easy. Pushing jobs into the queue only requires to put an executable script in a directory. Per default, all CPUs on your computer are used. New computers can be added very easily, too. Plus, your jobs can be written in any language.

``fjd`` works under the assumption that all CPUs are in a local network and can access a shared home directory.


Usage
-------

You can call ``fjd`` directly::

    $ fjd --exe "mktemp XXX.tmp" --instances 4

This example creates four temporary files with random names. Each of the four job will be done by one CPU (if you have that many).

You can also supply a list with parameters::

    $ fjd --exe 'touch bla$1.txt' --parameters 1,2,3,4

This will create four files: ``bla1.txt, bla2.txt, bla3.txt, bla4.txt``.
Here, ``fjd`` will select itself how many CPUs on your machine it should use.
Note that if you use the placeholder ``$1``, use single quotes aorund the ``--exe`` command.

To use several computers, you can configure a number of hosts in your network and how many CPUs should be 
running on each (see an example of this below).

``fjd`` can also be controlled in more detail. For instance, you can first start one or more ``fjd-worker`` threads, like this::

    $ fjd-recruiter hire [<number of workers>]

Per default, this starts n-1 worker threads, where n is the number of CPUs on your machine. 

Now you can put jobs in the job queue. You do this by putting a file per job in a designated directory (e.g. ``~/.fjd/default/jobqueue``, where 'default' could be changed to a specific project name). Here is an example job, simply a bash file which ``fjd`` will run::

    #!/bin/bash
    ./do_something
    ./do_something_else

Then, start a dispatcher::

    $ fjd-dispatcher

Now the ``fjd-dispatcher`` assigns jobs to ``fjd-worker`` threads who are currently not busy, until the job queue is empty.

After I discuss installation, I'll show more examples that make use of ``fjd``'s configuration possibilities.


Installation
-------------

First, you need to have python 2.7, which the default python on almost all systems these days (note: python 3.x support is not there yet, but close; see issue 10 on github). Then::

    $ pip install fjd

If you do not have enough privileges (look for something like "Permission denied" in the output), install locally (for your user account only)::

    $ pip install fjd --user

If you do not have ``pip`` installed (I can't wait for everyone running Python 3.4), I made a `small script <https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL>`_, which should help to install all needed things. Download it and make it executable::

    $ wget https://raw.github.com/nhoening/fjd/master/fjd/scripts/INSTALL
    $ chmod +x INSTALL

Now you can install system-wide::

    $ ./INSTALL

or, if you do not have root privileges, you can also install locally::

    $ source INSTALL --user

**Note** - If you installed locally, this should be added to your ``~/.bashrc`` or ``~/.profile`` file::

    export PATH=~/.local/bin:$PATH

**Note** - Installing locally could be the better choice, actually, because it might save you
from installing ``fjd`` on each machine you want to use.
If they all share the home directory, they will all know about ``fjd`` once you are logged in. 



Job files
------------

A job file should adhere to the general `INI-file standard <http://en.wikipedia.org/wiki/INI_file>`_.
``fjd`` only has some requirements for the ``control`` section, in which you specify which
command to execute and where results should go. Here is an example::

    [fjd]
    executable: python example/ajob.py

    [params]
    logfile: logfiles/job0.dat 
    my_param: value0

Your executable script gets this configuration file passed as a command line argument, so this would be called on the shell::

    python example/ajob.py <absolute path to the job file>

In addition, you can put other job-specific configuration in there for the executable
to see, as I did here in the ``[params]``-section (I repeat: only the ``[fjd]``-section
is required by ``fjd``).

Take care to get relative paths correct (or simply make them absolute):
If paths are relative, they should be relative to the directory in which you
start the ``fjd-dispatcher``.

To add this job to the job queue, we would place that file into ``~/.fjd/default/jobqueue``
and the ``fjd-dispatcher`` will find it there.

**Note** You can specify a project name (example below) and then "default" would be replaced by that.


An example (on your local machine)
------------------------------------

You can see how it all comes together by looking at the simple example in the ``example``
directory on github. There is one script that represents a job (`example/ajob.py <https://raw.github.com/nhoening/fjd/master/fjd/example/ajob.py>`_) 
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


You can cancel the ``fjd-dispatcher`` process now (i.e. hit CTRL-C).

And you'll see the results, the log files written by our example jobs::

    $ ls logfiles/
    job0.dat	job2.dat	job4.dat	job6.dat	job8.dat
    job1.dat	job3.dat	job5.dat	job7.dat	job9.dat

Workers are Unix screen sessions, you can see them by typing::

    $ screen -ls

and inspect them if you want. As attaching to screen sessions is cumbersome
and ``fjd`` can also close them before you have a chance to see what went wrong
(this is an option you can set, see next example below),
``fjd`` logs screen output to ``~/.fjd/<project>/screenlogs`` (each worker has
its own log file).

Here is an example log from a screen session of a worker::

    $ fjd-worker --project default
    [fjd-worker] Started with ID nics-macbook.fritz.box_1382522062.31.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: I found a job.
    [fjd-worker] Worker nics-macbook.fritz.box_1382522062.31: Finished my job.

By the way, if screen sessions are running and you want them to stop,
then you can always fire workers by hand::

    $ fjd-recruiter fire

or::

    $ fjd-recruiter --project <my-project> fire

If you start a new dispatcher, it will first clean up ("fire") old screen sessions.



Another example (using several machines in your network and a custom project name)
------------------------------------------------------------------------------------

We can tell ``fjd`` about other machines in the network and how many workers we'd like
to employ on them. To do that, we place a file called ``remote.conf`` in the project's
directory. Here is my file ``example/remote.conf``: If you run this example, 
you'll have to fill in names of machines in your particular network, of course::

    [host1]
    name: localhost
    workers: 3

    [host2]
    name: hyuga.sen.cwi.nl
    workers: 5


Normally, that directory is ``~/.fjd/default``. In this example, we tell ``fjd`` to
use a different project identifier (this way, you could have several projects
running without them getting into each other's way, i.e. stopping one project 
wouldn't stop the workers of the other and you wouldn't override the first project 
if you start another). Here is the content of ``run-remote-example.sh``, using the project
identifier ``remote-example``::

    #/bin/bash

    python create_jobs.py remote-example
    cp remote.conf ~/.fjd/remote-example/remote.conf
    fjd-recruiter --project remote-example hire
    fjd-dispatcher --project remote-example --end_when_jobs_are_done

If you run this example, the output you'll see should be similar to this::

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


**Note**  Unlike in the previous example, this time I told the ``fjd-dispatcher`` process
to fire workers (kill screen sessions) and terminate itself once it finds 
that all jobs are finished (via ``--end_when_jobs_are_done``).

**Note** - If you normally have to type in a password to login to a remote machine via SSH,
you'll have to do this here, as well. You can configure passwordless login by
putting a public key in ~/.ssh/authorized_keys. For the shared-home directory 
setting we use ``fjd`` for, this makes a lot of sense, as you stay within your LAN anyway.
In general, some SSH configuration can go a long way to ease your life,
e.g. by connection sharing through the ControlAuto option. Search the web or ask your local IT guy.



FAQ
------------------------------------

* I know a simple tool with comparable features: Gnu Parallel? What can ``fjd`` do better?:

    First off, Gnu Parallel is awesome, but sadly not known enough. I found out about it just recently. ``fjd`` is better at managing a dynamic queue, more demanding use cases (e.g. cluster environments, optimisation, many parameters). ``fjd`` is usable in Python programs. workers can be inspected live. TODO: formulate whoel sentences.

* Can I pass more than one parameter per job with the ``--paramters`` option?:

    Yes. Separate items in lists per job with ``#``, e.g. ``--parameters "'--my_param#1'"`` or ``--exe 'cp $1 $2' --parameters "a.txt#bckp/a.txt,b.txt#bckp/b.txt"``.
    If your ``--exe`` parameter contains the $-index (e.g. ``--exe 'echo $1' --parameters 'Hello!,Bye!'``), then the parameter will replace it (i.e. ``$1`` becomes ``Hello!`` for one job and ``Bye!`` for the second.

* How does ``fjd`` work, in a nutshell?:

Small files in your home directory are used to indicate which jobs have to be done (these are created by you)
and which workers are available (these are created automatically). Files are also used by ``fjd`` to assign workers
to jobs.

This simple file-based approach makes ``fjd`` very easy to use.

For CPUs from several machines to work on your job queue, we make one necessary assumption: We assume that there 
is a shared home directory for logged-in users, which all machines can access. This setting is very common now
in universities and companies.

A little bit more detail about the ``fjd`` internals: 
The ``fjd-recruiter`` creates worker threads on one or more machines (a worker thread is a Unix screen session, which remains even if you log out).
The ``fjd-worker`` processes announce themselves in the ``workerqueue`` directory. The ``fjd-dispatcher`` finds your jobs in the ``jobqueue`` directory and pairs a job with an available worker.
It then removes those entries from the ``jobqueue`` and ``workerqueue`` directories and creates a new entry in ``jobpods``, where workers will
pick up their assignments.

Then, the dispatcher calls your executable script and passes the file that describes the job to it as parameter on the shell.
Your script simply has to read the job file and act accordingly.

All of these directories mentioned above exist in ``~/.fjd`` and will of course be created if they do not yet exist.


