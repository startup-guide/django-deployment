import json
import os.path
import StringIO

from fabric.api import cd, env, put, settings, sudo, task
from fabric.operations import prompt

from django_deployment.services.db import init_db, install_postgres
from django_deployment.services.nginx import install_nginx
from django_deployment.utils import cmd, file_from_template, install_packages, \
        prepare_enviroment, virtualenv

UBUNTU_PACKAGES = [
    # Python
    'python', 'python-setuptools', 'python-pip', 'python-virtualenv',

    # Utils
    'gcc', 'git', 'mc', 'htop',

    # Services
    # 'rabbitmq-server',

    # Memcached
    'memcached', 'libmemcached-dev',

    # Libraries
    'python-dev', 'libxml2-dev', 'libxslt-dev',
]

# TODO: settings to activate services and features

# TODO: close ports, activate firewall
#  'deluser --remove-home' to remove linux user
@task
def init():
    # Install libraries and applications
    sudo('aptitude -y update')
    sudo('aptitude -y upgrade')
    install_packages(*UBUNTU_PACKAGES)

    install_postgres()

    install_nginx()

    # Create user and make him sudoer
    sudo('useradd -s /bin/bash -d /home/%(user)s -m %(user)s -G sudo' % {
            'user': env.deploy_user, 'password': env.passwords[env.host_string]})

    sudo('passwd %s' % env.deploy_user)

    # Set default text editor
    cmd('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /home/%s/.selected_editor' % env.deploy_user)
    sudo('echo "SELECTED_EDITOR=\"/usr/bin/mcedit\"" > /root/.selected_editor')

    # Generate ssh key
    cmd('mkdir /home/%s/.ssh' % env.deploy_user)
    cmd('ssh-keygen -t rsa -f /home/%s/.ssh/id_rsa -N %s -C "%s"' % (
            env.deploy_user, env.conf['SSH_KEY_PASSPHRASE'], env.conf['GITHUB_EMAIL']))

    # Wait until user adds the key to github
    print "\033[92mCopy the following public key and add it to the list of deploy keys on github\033[0m"
    cmd('cat /home/%s/.ssh/id_rsa.pub' % env.deploy_user)

    res = prompt('Have you added the key? (type "yes"): ')
    while res != 'yes':
        res = prompt('Have you added the key? (type "yes"): ')

    # Test access to repo
    with settings(warn_only=True):
        cmd('ssh -T git@github.com')

    prompt('Have you seen "You\'ve successfully authenticated" message above?')

    # Allow developers to login with ssh keys
    cmd('echo "%s" >> /home/%s/.ssh/authorized_keys' % ('\n'.join(env.conf['developers_ssh_pubkey']), env.deploy_user))
    sudo('mkdir -p /root/.ssh')
    sudo('echo -e "%s" >> /root/.ssh/authorized_keys' % '\n'.join(env.conf['developers_ssh_pubkey']))

    # TODO: after blocking password access env.passwords shouldn't be set
    # Prohibit ssh password authentication
    sudo('echo -e "\n\nChallengeResponseAuthentication no\nPasswordAuthentication no\nUsePAM no" >> /etc/ssh/sshd_config')
    sudo('reload ssh')

def deploy_static_files():
    # TODO: minify static files
    virtualenv('python %s collectstatic -c --noinput' % env.manage_path)
    #virtualenv('cp %sfavicon.ico %sfavicon.ico' % (env.STATIC_ROOT, env.static_path))
    #virtualenv('cp %s %srobots.txt' % (
    #        os.path.join(env.code_path, 'grakon', 'templates', 'robots.txt'), env.static_path))

@task
def deploy():
    """
    cmd('mkdir -p %s %s %s %s' % (
            env.code_path, env.env_path, env.STATIC_ROOT, os.path.join(env.logs_path)))

    cmd('git clone %s %s' % (env.conf['repository'], env.code_path))

    # Provide data for Django settings
    # TODO: change the owner of this file
    put(StringIO.StringIO(json.dumps(env.conf, indent=4)),
            os.path.join(env.code_path, 'deployment', 'config.json'))

    # Create virtualenv
    cmd('virtualenv --no-site-packages %s' % env.env_path)

    virtualenv('pip install -r %s' % os.path.join(env.code_path, 'deployment', 'requirements.prod.txt'))

    # TODO: a hack until django 1.5 is released
    virtualenv('pip install --no-deps django-grappelli==2.4.3')

    # Create uwsgi settings and run the daemon
    file_from_template(os.path.join('..', 'templates', 'uwsgi.ini'),
            os.path.join(env.code_path, 'deployment', 'uwsgi.ini'), root=False)

    # TODO: use uWSGI Emperor
    file_from_template(os.path.join('..', 'templates', 'upstart'), '/etc/init/uwsgi.conf')

    # Nginx site configuration
    file_from_template(os.path.join('..', 'templates', 'nginx_website.conf'),
            '/etc/nginx/sites-available/%s' % env.conf['DOMAIN'])

    sudo('ln -s /etc/nginx/sites-available/%(domain)s /etc/nginx/sites-enabled/%(domain)s' % {
            'domain': env.conf['DOMAIN']})

    # Initialize database
    init_db()

    # TODO: supervisord config file

    deploy_static_files()

    """
    restart()

def restart():
    sudo('/etc/init.d/nginx restart')

    sudo('service uwsgi restart')

    # sudo('/etc/init.d/postgresql restart')
    sudo('/etc/init.d/memcached restart')

    # TODO: start supervisord if not started - env_python bin/supervisord -c ../source/deployment/supervisor.conf
    # TODO: restart celery (via supervisord?) - no root

# TODO: detect if requirements.txt was updated in git pull and run pip install -r requirements.txt (+ special command for it+upgrade)
@task
def update():
    # TODO: perform db backup
    with cd(env.code_path):
        cmd('git pull')
    virtualenv('python %s migrate' % env.manage_path)

    deploy_static_files()

    restart()

"""
def developer_init():
    code_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    env_path = os.path.abspath(os.path.join(code_path, '..', 'env'))

    packages = UBUNTU_PACKAGES + ['rabbitmq-server']
    local('sudo aptitude -y install %s' % ' '.join(packages))

    # Copy settings file
    local('cp %s %s' % (os.path.join(code_path, 'grakon', 'site_settings.py.example'),
            os.path.join(code_path, 'grakon', 'site_settings.py')))

    # Create virtualenv
    local('virtualenv --no-site-packages %s' % env_path)

    virtualenv_cmd = "/bin/bash -l -c 'source %s && %%s'" % \
            os.path.join(env_path, 'bin', 'activate')

    local(virtualenv_cmd % ('pip install -r %s' % os.path.join(code_path, 'deployment', 'requirements.txt')))

    # Copy database file
    local('cp %s %s' % (os.path.join(code_path, 'init_database.sqlite'),
            os.path.join(code_path, 'database.sqlite')))
"""
