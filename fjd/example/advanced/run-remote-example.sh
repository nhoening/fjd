#/bin/bash

python create_jobs.py remote-example
cp remote.conf ~/.fjd/remote-example/remote.conf
fjd-recruiter --project remote-example hire
fjd-dispatcher --project remote-example --end_when_jobs_are_done
