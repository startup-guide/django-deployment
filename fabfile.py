import json

from django_deployment.fabfile import *

# TODO: this file should be copied to the project
env.conf = json.load(open('/home/serg/data/startups/projects/startup-guide/deployment/config.json')) 
env.conf.update(json.load(open('/home/serg/data/startups/projects/startup-guide/deployment/config.prod.json')) )

prepare_enviroment()
