"""
PostgreSQL users and databases
==============================

This module provides tools for creating PostgreSQL users and databases.

"""
from __future__ import with_statement

from fabric.api import cd, hide, run, settings, abort
from fabric.contrib.files import exists
from datetime import datetime as _date

def _run_as_pg(command):
    """
    Run command as 'postgres' user
    """
    with cd('~postgres'):
        return run('sudo -u postgres %s' % command)

def _port_option(port):
    """
    Return the option port if port passed
    """
    if port:
        return "-p %(port)s" % locals()
    else: 
        return ""
    
def user_exists(name, port=''):
    """
    Check if a PostgreSQL user exists.
    """
    port_option = _port_option(port)
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = _run_as_pg('''psql %(port_option)s -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%(name)s';"''' % locals())
    return (res == "1")


def create_user(name, password, superuser=False, createdb=False,
                createrole=False, inherit=True, login=True,
                connection_limit=None, encrypted_password=False, port=''):
    """
    Create a PostgreSQL user.

    Example::

        import fabtools

        # Create DB user if it does not exist
        if not fabtools.postgres.user_exists('dbuser'):
            fabtools.postgres.create_user('dbuser', password='somerandomstring')

        # Create DB user with custom options
        fabtools.postgres.create_user('dbuser2', password='s3cr3t',
            createdb=True, createrole=True, connection_limit=20)

    """
    options = [
        'SUPERUSER' if superuser else 'NOSUPERUSER',
        'CREATEDB' if createdb else 'NOCREATEDB',
        'CREATEROLE' if createrole else 'NOCREATEROLE',
        'INHERIT' if inherit else 'NOINHERIT',
        'LOGIN' if login else 'NOLOGIN',
    ]
    port_option = _port_option(port)
    if connection_limit is not None:
        options.append('CONNECTION LIMIT %d' % connection_limit)
    password_type = 'ENCRYPTED' if encrypted_password else 'UNENCRYPTED'
    options.append("%s PASSWORD '%s'" % (password_type, password))
    options = ' '.join(options)
    _run_as_pg('''psql %(port_option)s -c "CREATE USER %(name)s %(options)s;"''' % locals())


def database_exists(name, port=''):
    """
    Check if a PostgreSQL database exists.
    """
    port_option = _port_option(port)
    with settings(hide('running', 'stdout', 'stderr', 'warnings'),
                  warn_only=True):
        return _run_as_pg('''psql %(port_option)s -d %(name)s -c ""''' % locals()).succeeded


def create_database(name, owner, template='template0', encoding='UTF8',
                    locale='en_US.UTF-8', port=''):
    """
    Create a PostgreSQL database.

    Example::

        import fabtools

        # Create DB if it does not exist
        if not fabtools.postgres.database_exists('myapp'):
            fabtools.postgres.create_database('myapp', owner='dbuser')

    """
    port_option = _port_option(port)
    _run_as_pg('''createdb %(port_option)s --owner %(owner)s --template %(template)s \
                  --encoding=%(encoding)s --lc-ctype=%(locale)s \
                  --lc-collate=%(locale)s %(name)s''' % locals())


def create_schema(name, database, owner=None, port=''):
    """
    Create a schema within a database.
    """
    port_option = _port_option(port)
    if owner:
        _run_as_pg('''psql %(port_option)s %(database)s -c "CREATE SCHEMA %(name)s AUTHORIZATION %(owner)s"''' % locals())
    else:
        _run_as_pg('''psql %(port_option)s %(database)s -c "CREATE SCHEMA %(name)s"''' % locals())
        

def dump_database(database, path='/var/backups/postgres', filename='', format='plain', port=''):
    """
    Generate a dump database to a remote destination path
    Example::

        import fabtools

        fabtools.postgres.dump_database('myapp', path='/var/backups/postgres', filename='myapp-backup.sql')
        # If not filename specified will be saved with the date file format: database-201312010000.sql
        fabtools.postgres.dump_database('myapp', path='/var/backups/postgres') 
        # If not path specified will be saved at '/var/backups/postgres'
        fabtools.postgres.dump_database('myapp')
        # You can scpecify the pg_dump's custom format (able to restore with pg_restore)
        fabtools.postgres.dump_database('myapp', format='custom')

    """
    port_option = _port_option(port)
    if exists(path):
        if database_exists(database):
                date = _date.today().strftime("%Y%m%d%H%M")
                if not filename:
                    filename = '%(database)s-%(date)s.sql' % locals()
                _run_as_pg('''pg_dump %(port_option)s %(database)s --format=%(format)s --blobs --file="%(path)s/%(filename)s"''' % locals())
        else:
            abort('''Don\'t exists the database: %(database)s''' % locals())
    else:
        abort('''Don\'t exists the destination path: %(path)s''' % locals())


def restore_database(database, sqlfile='', port=''):
    """
    Restore a sql file to a database
    Example::

        import fabtools

        fabtools.postgres.restore_database('myapp', sqlfile='/var/backups/postgres/myapp-backup.sql')
    """
    port_option = _port_option(port)
    if exists(sqlfile):
        if database_exists(database):
            _run_as_pg('''psql %(port_option)s %(database)s < %(sqlfile)s''' % locals())
        else:
            abort('''Don\'t exists the database: %(database)s''' % locals())
    else:
        abort('''Don\'t exists the sql file: %(sqlfile)s''' % locals())