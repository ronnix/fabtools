#!/usr/bin/python
# -*- coding: utf-8 -*-
from fabtools.vagrant import vagrant
from fabtools.user import home_directory

from fabric.api import task, run, sudo
from fabric.context_managers import prefix


@task
def require_virtualenvwrapper():
    """
    Test virtualenvwrapper setup and usage.
    """
    from fabtools import require
    from fabtools.files import is_dir, is_file

    # create virtualenvwrapper home directory for user vagrant
    require.python.virtualenvwrapper('/home/vagrant/env')

    assert is_dir('/home/vagrant/env')

    # create a virtualenv with virtualenvwrapper
    run('mkvirtualenv venv')

    assert is_dir('/home/vagrant/env/venv')

    # create virtualenvwrapper home directory for user test
    require.user('test', shell='/bin/bash')

    require.python.virtualenvwrapper('/home/test/env', user='test', use_sudo=True)

    assert is_dir('/home/test/env')

    #TODO: understand why we need to source .profile here
    # other possibilities could be changing user with settings(user='test')
    with prefix('source %s' % home_directory('test') + '/.profile'):
        sudo('mkvirtualenv venv', user='test')

    assert is_dir('/home/test/env/venv')
    assert is_file('/home/test/env/venv/bin/python')
