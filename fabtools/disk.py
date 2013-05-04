"""
Disk Tools
==========
"""
from fabric.api import hide, settings, abort
from fabtools.utils import run_as_root

import re


def partitions(device=""):
    """
    Get a partition list for all disk or for selected device only

    Example::

        from fabtools.disk import partitions

        spart = {'Linux': 0x83, 'Swap': 0x82}
        parts = partitions()
        # parts =  {'/dev/sda1': 131, '/dev/sda2': 130, '/dev/sda3': 131}
        r = parts['/dev/sda1'] == spart['Linux']
        r = r and parts['/dev/sda2'] == spart['Swap']
        if r:
            print("You can format these partitions")
    """
    # scan partition
    partitions = {}
    with settings(hide('running', 'stdout')):
        res = run_as_root('sfdisk -d %(device)s' % locals())

        spart = re.compile(r'(?P<pname>^/.*) : .* Id=(?P<ptypeid>[0-9a-z]+)' %
                           locals())
        lines = res.splitlines()
        for l in lines:
            m = spart.search(l)
            if m:
                partitions[m.group('pname')] = int(m.group('ptypeid'), 16)

    return partitions


def mount(device, mountpoint):
    """
    Mount a partition

    Example::

        from fabtools.disk import mount

        mount('/dev/sdb1', '/mnt/usb_drive')
    """
    if not ismounted(device):
        run_as_root('mount %(device)s %(mountpoint)s' % locals())


def swapon(device):
    """
    Active swap partition

    Example::

        from fabtools.disk import swapon

        swapon('/dev/sda1')
    """
    if not ismounted(device):
        run_as_root('swapon %(device)s' % locals())


def ismounted(device):
    """
    Check if partition is mounted

    Example::

        from fabtools.disk import ismounted

        if ismounted('/dev/sda1'):
           print ("disk sda1 is mounted")
    """
    # Check filesystem
    with settings(hide('running', 'stdout')):
        res = run_as_root('mount')
    lines = res.splitlines()
    for l in lines:
        m = re.search('^%(device)s ' % locals(), l)
        if m:
            return True

    # Check swap
    with settings(hide('running', 'stdout')):
        res = run_as_root('swapon -s')
    lines = res.splitlines()
    for l in lines:
        m = re.search('^%(device)s ' % locals(), l)
        if m:
            return True

    return False


def mkfs(device, ftype):
    """
    Format filesystem

    Example::

        from fabtools.disk import mkfs

        mkfs('/dev/sda2', 'ext4')
    """
    if not ismounted('%(device)s' % locals()):
        run_as_root('mkfs.%(ftype)s %(device)s' % locals())
    else:
        abort("Partition is mounted")


def mkswap(device):
    """
    Format swap partition

    Example::

        from fabtools.disk import mkswap

        mkswap('/dev/sda2')
    """
    if not ismounted(device):
        run_as_root('mkswap %(device)s' % locals())
    else:
        abort("swap partition is mounted")