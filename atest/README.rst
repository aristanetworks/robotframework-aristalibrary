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

Advanced acceptance test running
--------------------------------

`<run_atests_veos.sh>`__ accepts numerous ENV variables and CLI options
to customize the test process::

    Usage:
    ./run_atests_veos.sh <options>
        -h  Show this help info
        -b <box>    Vagrant box image to test.  Use 'vagrant box list' for values
        -u  Bringup vagrant boxes and exit
        -r  Run Robot tests and exit
        -d  Destroy vagrant boxes and exit

    ENV variables:
        PYTHONPATH  Include locatoin of AristaLibrary and pyeapi
        VM_BOX  The name of a vagrant box to test. -b <box> will override this.
        VM_BOX_URL  The URL to a vagrant box to test
        TEST_TRANSPORT=[http|https]
        HTTP_PORT_PREFIX=208    ports 2080 and 2081
        HTTPS_PORT_PREFIX=244   ports 2440 and 2441
                  Range: 103 - 6553   (gives actual starting ports of 1030-65530)

    Examples:
        HTTP_PORT_PREFIX=123 ./run_atests_veos.sh
        VM_BOX=vEOS_4.14.6M ./run_atests_veos.sh


You can use the VM_BOX and VM_BOX_URL options to tell the test runner to use
arbitrary vEOS images either by name or by a URL to boxes stored in a central
repository::

    VM_BOX=vEOS_4.14.6M ./run_atests_veos.sh
    # OR
    ./run_atests_veos.sh -b vEOS_4.14.6M
    # OR
    VM_BOX_URL="http://server.example.com/vagrant/vEOS_4.14.3F_virtualbox.box" ./run_atests_veos.sh

When developing or troubleshooting tests, one might wish to setup the VMs once,
then perform multiple Robot test runs before destroying them.  The cli options
fully support this process::

    # Up the desired version VMs
    ./run_atests_veos.sh -b vEOS_4.14.6M -u

    # Run Robot test suites
    ./run_atests_veos.sh -r
    # edit tests...
    ./run_atests_veos.sh -r
    ...

    # Destroy the VMs
    ./run_atests_veos.sh -d

