fjd
===

``fjd`` makes it easy to run computational jobs on many CPUs.

There are several powerful tools for dispatching dynamic lists of computational jobs to multiple, possibly distributed CPUs. However, for simple use cases, the effort of installation and setup is often too high.

With ``fjd``, the hurdle to get started is very low. Installation is easy. Pushing jobs into the queue only requires to put an executable script in a directory. Per default, all CPUs on your computer are used. Other computers can be used very easily, as well. Plus, your jobs can be written in any language.



Usage
-------

You can call ``fjd`` directly::

    $ fjd --exe "mktemp XXX.tmp" --repeat 5

This simple example creates five temporary files with random names. Each of the five jobs will be done on a different CPU (if you have that many).

You can also supply a list with parameters::

    $ fjd --exe 'touch bla$1.txt' --parameters 1,2,3,4

This will create four files: ``bla1.txt, bla2.txt, bla3.txt, bla4.txt``.
Here, ``fjd`` will select by itself how many CPUs on your machine it should use.
Note that if you use the placeholder ``$1``, use single quotes around the ``--exe`` command.

To use several computers, you can configure a number of hosts in your network and how many CPUs should be 
running on each (see an example of this below).

For illustration, here is the session output from the first example::

    $ fjd --exe "mktemp XXX.tmp" --repeat 5
    [fjd-recruiter] Hired 5 workers in project "default".
    [fjd-dispatcher] Started on project "default".
    [fjd-dispatcher] Job queue is empty and all jobs have finished.                                               
    [fjd-recruiter] Fired 5 worker(s) in project "default".



Advanced usage
-----------------

``fjd`` can also be controlled in more detail.

Most importantly, you can write an executable bash script for each job and put it in the queue. You have total freedom what each job is doing and when you put it in the queue. In the usual case your queue directory is ``~/.fjd/default/jobqueue`` (where ``default`` could be changed to a specific project name). Another option is to describe a job as a configuration file. We'll have an example below.

Then, you can start one or more ``fjd-worker`` threads, like this::

    $ fjd-recruiter hire [<number of workers>]

Per default, this starts n-1 worker threads, where n is the number of CPUs on your machine. 

Finally, start a dispatcher::

    $ fjd-dispatcher

Now the ``fjd-dispatcher`` assigns jobs to ``fjd-worker`` threads who are currently not busy, until the job queue is empty.

You can cancel the ``fjd-dispatcher`` process at any time (i.e. hit CTRL-C) and it will ask you if workers should be fired or not.
By the way, if screen sessions are running and you want them to stop,
then you can always fire workers by hand::

    $ fjd-recruiter fire

or, to fire only the ones running one specific project (more on that option below)::

    $ fjd-recruiter --project <my-project> fire

If you start a new dispatcher, it will first clean up ("fire") old screen sessions.



Installation
-------------

First, you need to have python 2.7, which the default python on almost all systems these days (note: python 3.x support is not there yet, but close; see issue #10 on github). Then::

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



Using several machines in your network
----------------------------------------------------------

We can tell ``fjd`` about other machines in the network and how many workers we'd like
to employ on them. To do that, we place a file called ``remote.conf`` in the project's
directory. Here is an example::

    [host1]
    name: localhost
    workers: 3

    [host2]
    name: hyuga.sen.cwi.nl
    workers: 5

There is an `advanced example <https://raw.github.com/nhoening/fjd/master/fjd/example/advanced>`_
in the github repo which you can run and inspect. Use the scripts ``run-example.sh`` or 
``run-remote-example.sh`` to execute.

**Note** - ``fjd`` works under the assumption that all CPUs are in a local network and can access a shared home directory.

**Note** - If you normally have to type in a password to login to a remote machine via SSH,
you'll have to do this here, as well. You can configure passwordless login by
putting a public key in ~/.ssh/authorized_keys. For the shared-home directory 
setting we use ``fjd`` for, this makes a lot of sense, as you stay within your LAN anyway.
In general, some SSH configuration can go a long way to ease your life,
e.g. by connection sharing through the ControlAuto option. Search the web or ask your local IT guy.



Inspecting the workers
-------------------------

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



Running several projects
-----------------------------------

Normally, the project directory is ``~/.fjd/default``. But you can tell ``fjd``
to use a different project identifier (this way, you could have several projects
running without them getting into each other's way, i.e. stopping one project 
wouldn't stop the workers of the other and you wouldn't override the first project 
if you start another). 

For instance, you'd recruite workers and dispatch jobs with the ``--project`` parameter::

    $ fjd-recruiter --project remote-example hire
    $ fjd-dispatcher --project remote-example

Or, if you call ``fjd`` from code::

    recruiter = Recruiter(project=project)
    recruiter.hire()
    Dispatcher(project=project)



Jobs as configuration files
----------------------------------

When a job is heavily parameterised, a bash script might not be convenient. I sometimes prefer a configuration file in such cases.
In this case, a job file should adhere to the general `INI-file standard <http://en.wikipedia.org/wiki/INI_file>`_.
You can write in there what you want - ``fjd`` only has one requirement. Add a ``fjd`` section, and specify which
command to execute. Here is an example::

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

The `advanced example <https://raw.github.com/nhoening/fjd/master/fjd/example/advanced>`_ also shows how this works.
You can use the script ``run-config-example.sh`` to run it.



FAQ
------------------------------------

I know an existing simple tool with comparable features: `Gnu Parallel <http://www.gnu.org/software/parallel>`_. How do you position ``fjd`` with respect to that?
    First off, Gnu Parallel is an awesome tool and very powerful. I found out about it just recently. It fits into the Unix workflow perfectly and you can do almost anything with it, if you're knowledgeable on the Unix command line (for instance if you use ``xargs`` a lot, you can become productive in Gnu parallel quickly). ``fjd`` delivers several functionalities that Gnu parallel delivers, but not all of them. I'd say there are three small aspects which are different in ``fjd`` - First, ``fjd`` is more explicit about worker processes (they are Unix screen sessions, which you can join live, but they also have their own log files each). Second, ``fjd`` lives in the Python ecosystem (which means you can edit it easier if you prefer Python over Perl and depend on it in Python programs you write). Third, jobs with many parameters can parametrised in config files, which I feel is quite convenient sometimes.
In addition, ``fjd`` has one interesting feature to offer: the queue of jobs can be sorted on the fly, which can be useful for some use cases where it is important to always perform the job first which is most likely to lead to positive outcomes (e.g. in an optimisation context). 
 
Can I pass more than one parameter per job with the ``--parameters`` option?
    Yes. Separate items in lists per job with ``#``, e.g. ``--parameters "'--my_param#1'"`` or ``--exe 'cp $1 $2' --parameters "a.txt#bckp/a.txt,b.txt#bckp/b.txt"``.
    If your ``--exe`` parameter contains the $-index (e.g. ``--exe 'echo $1' --parameters 'Hello!,Bye!'``), then the parameter will replace it (i.e. ``$1`` becomes ``Hello!`` for one job and ``Bye!`` for the second.

How would I use ``fjd`` on a computation cluster?
    I use ``fjd`` to great effect on a PBS cluster (a system many of them use). The computation nodes on this system all have access to a shread home directory, so ``fjd`` can work well there. All I do is fill the job queue and for each computation node I order, I issue a ``fjd-recruiter hire X`` command, where ``X`` is the number of cores that node has.
    For illustration, I have `an example script <https://raw.github.com/nhoening/fjd/master/fjd/example/runbrute.py>`_, which I use to run >600K small jobs (In order to run a brute-force benchmark). 

How does ``fjd`` work, in a nutshell?
    Small files in your home directory are used to indicate which jobs have to be done (these are created by you) and which workers are available (these are created automatically). Files are also used by ``fjd`` to assign workers to jobs.

    This simple file-based approach makes ``fjd`` very easy to use.

    For CPUs from several machines to work on your job queue, we make one necessary assumption: We assume that there  is a shared home directory for logged-in users, which all machines can access. This setting is very common now in universities and companies.

    A little bit more detail about the ``fjd`` internals: 
    The ``fjd-recruiter`` creates worker threads on one or more machines (a worker thread is a Unix screen session, which remains even if you log out).
    The ``fjd-worker`` processes announce themselves in the ``workerqueue`` directory. The ``fjd-dispatcher`` finds your jobs in the ``jobqueue`` directory and pairs a job with an available worker.
    It then removes those entries from the ``jobqueue`` and ``workerqueue`` directories and creates a new entry in ``jobpods``, where workers will pick up their assignments.

    Then, the dispatcher calls your executable script and passes the file that describes the job to it as parameter on the shell.
    Your script simply has to read the job file and act accordingly.

    All of these directories mentioned above exist in ``~/.fjd`` and will of course be created if they do not yet exist.


