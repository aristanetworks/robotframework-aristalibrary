#!/bin/sh

# Where to find AristaLibrary and pyeapi
p1=${PYTHONPATH:=..}
export PYTHONPATH

# Default vagrant box to use for tests
v1=${VM_BOX:=vEOS-lab-4.20.0-EFT2}  # see `vagrant box list`

# These can be overriden so multiple tests do not stomp on each other.
#   Range: 103 - 6553   (gives actual starting ports of 1030-65530)
#   Example: HTTP_PORT_PREFIX=123 ./run_robot_tests_veos.sh
a1=${TEST_TRANSPORT:=http}
a2=${HTTP_PORT_PREFIX:=208}   # ports 2080 and 2081
a3=${HTTPS_PORT_PREFIX:=244}  # ports 2440 and 2441

# The following executables MUST be available
REQS="vagrant
      VBoxManage
      pybot"

start_vagrant () {
    sed -i '' \
        -e "s/guest: 80.*\$/guest: 80, host: \"${HTTP_PORT_PREFIX}#{i}\"/" \
        -e "s/guest: 443.*\$/guest: 443, host: \"${HTTPS_PORT_PREFIX}#{i}\"/" \
        Vagrantfile

    # Start vagrant boxes
    export VM_BOX
    export VM_BOX_URL
    time vagrant up --destroy-on-error --parallel

    if [ $? -ne 0 ]; then
        echo "Failed to start VMs with 'vagrant up'"
        exit 1
    fi

    echo "vEOS VMs are up."
}

vagrant_cmd () {
    sed -i '' \
        -e "s/guest: 80.*\$/guest: 80, host: \"${HTTP_PORT_PREFIX}#{i}\"/" \
        -e "s/guest: 443.*\$/guest: 443, host: \"${HTTPS_PORT_PREFIX}#{i}\"/" \
        Vagrantfile

    # Start vagrant boxes
    export VM_BOX
    export VM_BOX_URL
    echo "Running: time vagrant ${VAGRANT_CMD} $@"
    time vagrant "${VAGRANT_CMD}" "$@"

    if [ $? -ne 0 ]; then
        echo "Failed to run 'vagrant ${VAGRANT_CMD}'"
        exit 1
    fi
}

start_pybot () {
    echo "Starting Robot Framework tests..."

    if [ ! -d results ]; then
        mkdir results
    fi

    time pybot \
        --outputdir results \
        --variable TRANSPORT:${TEST_TRANSPORT} \
        --variable SW1_PORT:${HTTP_PORT_PREFIX}0 \
        --variable SW2_PORT:${HTTP_PORT_PREFIX}1 \
        --noncritical new \
        AristaLibrary/
}

stop_vagrant () {
    vagrant destroy --force
}

check_prereqs () {
    for exe in ${@}; do
        which ${exe} >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "  ERROR: Unable to find ${exe} executable. Aborting test."
            exit 1
        fi
    done
}

usage () {
    echo
    echo "Usage:"
    echo "    ${0} <options>"
    echo "        -h\tShow this help info"
    echo "        -b <box>\tVagrant box image to test.  Use 'vagrant box list' for values"
    echo "        -u\tBringup vagrant boxes and exit"
    echo "        -r\tRun Robot tests and exit"
    echo "        -d\tDestroy vagrant boxes and exit"
    echo
    echo "    ENV variables:"
    echo "        PYTHONPATH\tInclude location of AristaLibrary and pyeapi"
    echo "        VM_BOX\tThe name of a vagrant box to test. -b <box> will override this."
    echo "        VM_BOX_URL\tThe URL to a vagrant box to test"
    echo "        TEST_TRANSPORT=[http|https]"
    echo "        HTTP_PORT_PREFIX=208\tports 2080 and 2081"
    echo "        HTTPS_PORT_PREFIX=244\tports 2440 and 2441"
    echo "                  Range: 103 - 6553   (gives actual starting ports of 1030-65530)"
    echo
    echo "    Examples:"
    echo "        HTTP_PORT_PREFIX=123 ${0}"
    echo "        VM_BOX=vEOS_4.14.6M ${0}"
    echo
}

START_VAGRANT=1
START_PYBOT=1
STOP_VAGRANT=1

while getopts ":hb:c:urd" opt; do
    case $opt in
        h)
            usage
            exit 1
            ;;
        b)
            echo "Running tests with box image: ${OPTARG}"
            export VM_BOX=${OPTARG}
            ;;
        c)
            export VAGRANT_CMD=${OPTARG}
            START_VAGRANT=0
            START_PYBOT=0
            STOP_VAGRANT=0
            ;;
        u)
            echo "Starting vagrant boxes only."
            START_VAGRANT=1
            START_PYBOT=0
            STOP_VAGRANT=0
            ;;
        r)
            echo "Running Robot acceptance tests only."
            START_VAGRANT=0
            START_PYBOT=1
            STOP_VAGRANT=0
            ;;
        d)
            echo "Destroying vagrant boxes only."
            START_VAGRANT=0
            START_PYBOT=0
            STOP_VAGRANT=1
            ;;
        \?)
            echo "Invalid option: -${OPTARG}" >&2
            usage
            exit 1
            ;;
    esac
done
shift $((OPTIND -1))

check_prereqs ${REQS}

# Adjust the port forward prefix in the Vagrantfile
#   node.vm.network "forwarded_port", guest: 80, host: "208#{i}"
#   node.vm.network "forwarded_port", guest: 443, host: "244#{i}"
export HTTP_PORT_PREFIX
export HTTPS_PORT_PREFIX

# Run each section if enabled
if [ ${START_VAGRANT} -gt 0 ]; then
    start_vagrant
fi
if [ ${START_PYBOT} -gt 0 ]; then
    start_pybot
fi
if [ ${STOP_VAGRANT} -gt 0 ]; then
    stop_vagrant
fi
if [ "X${VAGRANT_CMD}" != "X" ]; then
    vagrant_cmd
fi
