AristaLibrary acceptance tests
==============================

Introduction
------------

Acceptance tests for AristaLibrary are written in Robot and rely on 
`pyeapi<https://pypi.python.org/pypi/pyeapi>` (`GitHub<https://github.com/arista-eosplus/pyeapi>`).
As these tests perform end-to-end communications with Arista EOS, they expect
two working EOS nodes configured for eAPI.

Initial Setup
-------------

In order for the acceptance tests to run, you need to setup the following
in your environment prior to executing them.   Every effort has been made
to automate as much as possible.

Requirements:

* pyeapi - ``pip install [--upgrade] pyeapi``
* Arista EOS - 
    The included script expects a box image of vEOS with eAPI pre-configured
    which will be launched by vagrant.  However, ``pybot`` may be manually
    executed to utilize other vEOS VMs or physical switches.

Running acceptance tests
------------------------

The AristaLibrary acceptance tests are run with `<run_atests_veos.sh>`__.  This
will use vagrant to launch 2 VirtualBox vEOS VMs, connect their Ethernet 1
interfaces, and setup port-forwarding to access eAPI. Next, it will execute
pybot, passing it connection information to each EOS node.   Finally, it will
destroy the vEOS VMs.


EOS pre-configuration expectations
----------------------------------

There are 2 ways the tests can access EOS via eAPI:

* EOS on a physical switch
* vEOS - a virtual machine running EOS

Using vEOS, the VMs can be setup manually or via automation using 
`packer`, `VirtualBox`, and managed by `vagrant`.

In either case, in addition to at least 1 interface with a reachable IP
address and Ethernet 1 one each switch connected to the other,
the Robot testcases expect the following config to be present
on each switch prior to starting ``pybot``::

    username vagrant privilege 15 role network-admin secret vagrant
    !
    management api http-commands
       no shutdown


