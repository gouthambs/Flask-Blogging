# http://stackoverflow.com/questions/2720014/upgrading-all-packages-with-pip
import pip
from subprocess import call

for dist in pip.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)
