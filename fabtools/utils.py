"""
Utilities
=========
"""

import os
import posixpath

from fabric.api import env, hide, run, sudo, settings


def run_as_root(command, *args, **kwargs):
    """
    Run a remote command as the root user.

    When connecting as root to the remote system, this will use Fabric's
    ``run`` function. In other cases, it will use ``sudo``.
    """
    if env.user == 'root':
        func = run
    else:
        func = sudo
    return func(command, *args, **kwargs)


def get_cwd(local=False):

    from fabric.api import local as local_run

    with hide('running', 'stdout'):
        if local:
            return local_run('pwd', capture=True)
        else:
            return run('pwd')


def abspath(path, local=False):

    path_mod = os.path if local else posixpath

    if not path_mod.isabs(path):
        cwd = get_cwd(local=local)
        path = path_mod.join(cwd, path)

    return path_mod.normpath(path)


def download(url, retry=10):
    from fabtools.require.curl import command as require_curl
    require_curl()
    run('curl --silent --retry %s -O %s' % (retry, url))


def kill_proc(name, use_sudo=False):
    func = use_sudo and run_as_root or run
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        func('killall %(name)s' % locals())

# vim: set expandtab:
