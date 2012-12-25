from fabric.api import env, sudo

from django_deployment.utils import install_packages, virtualenv

# TODO: configure db backups
# Use 'sudo su postgres', 'dropdb %s' and 'dropuser %s' to clean db
def install_postgres():
    install_packages('postgresql', 'postgresql-client', 'postgresql-server-dev-all')

    # Create postgres user and database
    sudo('createuser -l -E -S -D -R %s' % env.conf['database.USER'], user='postgres')
    sudo('createdb -O %s %s' % (env.conf['database.USER'], env.conf['database.NAME']), user='postgres')

    # Database settings recommended by Django
    postgres_conf = {
        'client_encoding': "'UTF8'",
        'default_transaction_isolation': "'read committed'",
        'timezone': "'UTC'",
    }

    for param, value in postgres_conf.iteritems():
        sudo('echo "ALTER ROLE %s in DATABASE %s SET %s = %s;" | psql' % (
                env.conf['database.USER'], env.conf['database.NAME'], param, value), user='postgres')

    sudo('echo "ALTER USER %s WITH PASSWORD \'%s\';" | psql' % (
            env.conf['database.USER'], env.conf['database.PASSWORD']), user='postgres')

def init_db():
    virtualenv('python %s syncdb --noinput --all' % env.manage_path)
    virtualenv('python %s migrate --fake' % env.manage_path)
    virtualenv('python %s createsuperuser' % env.manage_path)
