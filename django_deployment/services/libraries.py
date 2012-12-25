import os.path

from fabric.api import env, sudo
from fabric.contrib.files import sed

from django_deployment.utils import virtualenv

# TODO: use http://pypi.python.org/pypi/Pillow/ instead?
def install_pil():
    """ Custom PIL installation to activate JPEG support """
    # Install required packages
    packages = ['libjpeg8', 'libjpeg8-dev', 'libfreetype6', 'libfreetype6-dev', 'zlib1g-dev']
    sudo('aptitude -y install %s' % ' '.join(packages))

    # PIL requires custom installation to activate JPEG support
    virtualenv('pip install -I pil --no-install')
    sed(os.path.join(env.env_path, 'build', 'pil', 'setup.py'),
            '# standard locations',
            'add_directory(library_dirs, "/usr/lib/x86_64-linux-gnu")')
    virtualenv('pip install -I pil --no-download')
