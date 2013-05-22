"""
Python environments and packages
================================

This module includes tools for using `virtual environments`_
and installing packages using `pip`_.

.. _virtual environments: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/

"""
import posixpath

from fabric.api import run, sudo
from fabric.contrib.files import append

from fabtools.files import is_file
from fabtools.python import (
    install,
    install_pip,
    install_requirements,
    is_installed,
    is_pip_installed,
)
from fabtools.python_distribute import (
    install_distribute,
    is_distribute_installed,
)
from fabtools.system import distrib_family
from fabtools.user import home_directory


DEFAULT_PIP_VERSION = '1.3.1'


def distribute():
    """
    Require `distribute`_ to be installed.

    .. _distribute: http://packages.python.org/distribute/
    """

    from fabtools.require.deb import packages as require_deb_packages
    from fabtools.require.rpm import packages as require_rpm_packages

    family = distrib_family()

    if family == 'debian':
        require_deb_packages([
            'curl',
            'python-dev',
        ])

    elif family == 'redhat':

        require_rpm_packages([
            'curl',
            'python-devel',
        ])

    if not is_distribute_installed():
        install_distribute()


def pip(version=None):
    """
    Require `pip`_ to be installed.
    """
    distribute()
    if not is_pip_installed(version):
        install_pip()


def package(pkg_name, url=None, **kwargs):
    """
    Require a Python package.

    If the package is not installed, it will be installed
    using the `pip installer`_.

    ::

        from fabtools.python import virtualenv
        from fabtools import require

        # Install package system-wide
        require.python.package('foo', use_sudo=True)

        # Install package in an existing virtual environment
        with virtualenv('/path/to/venv'):
            require.python.package('bar')

    .. _pip installer: http://www.pip-installer.org/
    """
    pip(DEFAULT_PIP_VERSION)
    if not is_installed(pkg_name):
        install(url or pkg_name, **kwargs)


def packages(pkg_list, **kwargs):
    """
    Require several Python packages.
    """
    pip(DEFAULT_PIP_VERSION)
    pkg_list = [pkg for pkg in pkg_list if not is_installed(pkg)]
    if pkg_list:
        install(pkg_list, **kwargs)


def requirements(filename, **kwargs):
    """
    Require Python packages from a pip `requirements file`_.

    .. _requirements file: http://www.pip-installer.org/en/latest/requirements.html
    """
    pip(DEFAULT_PIP_VERSION)
    install_requirements(filename, **kwargs)


def virtualenv(directory, system_site_packages=False, python=None,
               use_sudo=False, user=None, clear=False, prompt=None):
    """
    Require a Python `virtual environment`_.

    ::

        from fabtools import require

        require.python.virtualenv('/path/to/venv')

    .. _virtual environment: http://www.virtualenv.org/
    """
    package('virtualenv', use_sudo=True)
    if not is_file(posixpath.join(directory, 'bin', 'python')):
        options = ['--quiet']
        if system_site_packages:
            options.append('--system-site-packages')
        if python:
            options.append('--python=%s' % python)
        if clear:
            options.append('--clear')
        if prompt:
            options.append('--prompt="%s"' % prompt)
        options = ' '.join(options)
        command = 'virtualenv %(options)s "%(directory)s"' % locals()
        if use_sudo:
            sudo(command, user=user)
        else:
            run(command)


def virtualenvwrapper(directory, use_sudo=False, user=None):
    """
    Require `virtualenvwrapper`_ and set your virtualenv home directory.

    ::

        from fabtools import require

        require.python.virtualenvwrapper('/path/to/venv_home')

    As the directory will be exported in the user .profile, you can use other
    environment variables such as '$HOME'

    Once virtualenv are created in the `venv_home` directory, you can activate
    and cd to then using the virtualenvwrapper `workon` command.

    ::

        from fabric.context_managers import prefix

        with prefix('workon venv'):
            run('./manage.py syncdb')

    .. _virtual environment: http://www.virtualenv.org/
    .. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
    """
    package('virtualenv', 'virtualenvwrapper', use_sudo=True)

    profile_conf = '%s.profile' % (home_directory(user) + '/' if user else '')

    append(profile_conf, 'export WORKON_HOME=%s' % directory, use_sudo=use_sudo)
    append(profile_conf, 'source /usr/local/bin/virtualenvwrapper.sh',
           use_sudo=use_sudo)

    # Source the user .profile for creating the directory
    if user:
        sudo('source %s' % profile_conf, user=user)
