import jsonrpclib

def create_rpc(url):
    eapi = jsonrpclib.Server(url)
    return eapi

def connect_to(node, proto="https", port="443", username="admin", passwd="admin"):
    """Try to connect to an EOS node over JSONRPC"""

    url = "%s://%s:%s@%s:%s/command-api" % (proto, username, passwd, node, port)
    eapi = jsonrpclib.Server(url)

    try:
      result = eapi.runCmds(1, ["show version"])
      return url
    except jsonrpclib.ProtocolError as e:
      errorResponse = jsonrpclib.loads(jsonrpclib.history.response)
      print "Failed:", errorResponse["error"]["data"][0]["errors"][-1]

def eos_version_is(version,url):
    """Checks if EOS software version equals specified value"""

    eapi = create_rpc(url)

    try:
      result = eapi.runCmds(1, ["show version"])
    except jsonrpclib.ProtocolError as e:
      errorResponse = jsonrpclib.loads(jsonrpclib.history.response)
      print "Failed:", errorResponse["error"]["data"][0]["errors"][-1]

    result = result[0]
    nodeVersion = result["version"]
    if nodeVersion != version:
      raise AssertionError('Incorrect Software version found')

def extension_installed(name, version, available, installed, url):
    """Checks if an extension has the right values"""

    eapi = create_rpc(url)

    try:
      result = eapi.runCmds(1, ["show extensions"], "text")
    except jsonrpclib.ProtocolError as e:
      errorResponse = jsonrpclib.loads(jsonrpclib.history.response)
      print "Failed:", errorResponse["error"]["data"][0]["errors"][-1]

    result = result[0]['output']
    lines = [i for i in result.split('\n')]

    del lines[0]
    del lines[0]
    del lines[-1]
    del lines[-1]
    del lines[-1]
    rpms = []

    for line in lines:
        rpmParts = [i for i in line.split()]
        if len(rpmParts) > 3:
            d = {
              'name':rpmParts[0],
              'version':rpmParts[1],
              'available':rpmParts[2].replace(",",""),
              'installed':rpmParts[3],
              'rpms':rpmParts[4]
            }
            rpms.append(d)

    extFound = False
    success = False
    for rpm in rpms:
        if rpm['name'] == name:
            extFound = True
            success = True
            log = "\nName is a match: %s == %s" % (rpm['name'], name)
            r = rpm
            if rpm['version'] != version:
                success = False
                log += "\nVersion is NOT a match: %s != %s" % (rpm['version'], version)

            if rpm['available'] != available:
                success = False
                log += "\nAvailable is NOT a match: %s != %s" % (rpm['available'], available)

            if rpm['installed'] != installed:
                success = False
                log += "\nInstalled is NOT a match: %s != %s" % (rpm['installed'], installed)
    if success:
        return True
    elif extFound:        raise AssertionError("Extension found but with params:%s\n" % log)
    else:
        raise AssertionError("Extension not found in returned in eAPI command\n"
                             "RawOutput:\n%s" % result)

def mlag_state_is(state,url):
    """Checks if MLAG is in the proper state"""

    eapi = create_rpc(url)

    try:
      result = eapi.runCmds(1, ["show mlag"])
    except:
      raise AssertionError('Cannot connect to EOS node')

    result = result[0]
    mlagState = result['state']
    if mlagState != state:
      raise AssertionError('Incorrect Software version found')

def node_env_cooling_between(min,max,url):
    """Checks if Node has cooling values between min and max"""

    eapi = create_rpc(url)
    try:
      result = eapi.runCmds(1, ["show environment cooling"])
    except jsonrpclib.ProtocolError as e:
      errorResponse = jsonrpclib.loads(jsonrpclib.history.response)
      print "Failed:", errorResponse["error"]["data"][0]["errors"][-1]

    min = int(min)
    max = int(max)

    result = result[0]
    for traySlot in result["fanTraySlots"]:
        for fan in traySlot["fans"]:
            if (fan["configuredSpeed"] not in range(min, max) or
                fan["actualSpeed"] not in range(min, max)):
                raise AssertionError('Value found not in range:%s to %s'
                                     'reported value:%s %s' %
                                     (min, max, fan["configuredSpeed"],
                                      fan["actualSpeed"]))
