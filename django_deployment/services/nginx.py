import os.path

from fabric.api import env, put, sudo

from django_deployment.utils import file_from_template, install_packages

def install_nginx():
    install_packages('nginx')

    sudo('pip install uwsgi')

    # Global configuration
    sudo('cp /etc/nginx/nginx.conf /etc/nginx/nginx-prev.conf')

    nginx_conf = open(os.path.normpath(
        os.path.join(os.path.abspath(__file__), '..', '..', 'templates', 'nginx.conf')
    ))
    put(nginx_conf, '/etc/nginx/nginx.conf')

    sudo('rm -f /etc/nginx/sites-enabled/default')
