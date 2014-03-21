#/bin/bash

./create_config_jobs.py
fjd-recruiter hire 4
fjd-dispatcher --end_when_jobs_are_done
