#!/bin/sh

# Where to find AristaLibrary and pyeapi
export PYTHONPATH=../AristaLibrary

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

check_prereqs () {
    for exe in ${@}; do
        which ${exe} >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "  ERROR: Unable to find ${exe} executable. Aborting test."
            exit 1
        fi
    done
}

check_prereqs ${REQS}

# Adjust the port forward prefix in the Vagrantfile
#   node.vm.network "forwarded_port", guest: 80, host: "208#{i}"
#   node.vm.network "forwarded_port", guest: 443, host: "244#{i}"
export HTTP_PORT_PREFIX
export HTTPS_PORT_PREFIX
sed -i '' \
    -e "s/guest: 80.*\$/guest: 80, host: \"${HTTP_PORT_PREFIX}#{i}\"/" \
    -e "s/guest: 443.*\$/guest: 443, host: \"${HTTPS_PORT_PREFIX}#{i}\"/" \
    Vagrantfile

# Start vagrant boxes
time vagrant up --destroy-on-error --parallel

if [ $? -ne 0 ]; then
    echo "Failed to start VMs with 'vagrant up'"
    exit 1
fi

echo "vEOS VMs are up.   Starting Robot Framework tests..."

pybot \
    --variable TRANSPORT:${TEST_TRANSPORT} \
    --variable SW1_PORT:${HTTP_PORT_PREFIX}0 \
    --variable SW2_PORT:${HTTP_PORT_PREFIX}1 \
    --noncritical new \
    unittest.txt
#    --pythonpath=../AristaLibrary

vagrant destroy --force
