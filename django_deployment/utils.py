import os.path
import StringIO

from fabric.api import env, prefix, put, sudo

def cmd(command):
    """ Shortcut for running a command in user enviroment """
    # TODO: solve 'mesg: /dev/pts/1: Operation not permitted' issue
    return sudo(command, user=env.deploy_user)

def virtualenv(command):
    """ Shortcut for running a command inside virtualenv enviroment """
    with prefix('source %s' % os.path.join(env.env_path, 'bin', 'activate')):
        cmd(command)

def install_packages(*packages):
    sudo('aptitude -y install %s' % ' '.join(packages))

def file_from_template(rel_template_path, dest_path, root=True):
    """ Generate file from a template """
    template = open(os.path.normpath(os.path.join(os.path.abspath(__file__), rel_template_path))).read()
    put(StringIO.StringIO(template % env.conf), dest_path)

    if not root:
        pass # TODO: change the owner of this file

# TODO: use fabric django integration?
def prepare_enviroment():
    """ The dictionary env.conf must be set before calling this method """
    env.hosts = [env.conf['host']]

    # TODO: should be commented after ssh key login is set up
    env.passwords = {env.conf['host']: env.conf['password']}

    env.deploy_user = env.conf['username']

    # Paths
    proj_path = env.conf['path'] = os.path.join('/home/%s' % env.deploy_user, env.conf['path']+'/') # project dir
    env.code_path = env.conf['code_path'] = os.path.join(proj_path, 'source/') # source code dir
    env.env_path = env.conf['env_path'] = os.path.join(proj_path, 'env/') # virtualenv dir
    env.manage_path = os.path.join(env.code_path, 'manage.py') # path to manage.py

    env.logs_path = env.conf['logs_path'] = os.path.join(proj_path, 'logs/')

    # Static files
    env.static_path = env.conf['static_path'] = os.path.join(proj_path, 'static/')
    env.STATIC_ROOT = env.conf['STATIC_ROOT'] = os.path.join(env.static_path, 'static/')
