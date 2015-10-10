#!/usr/bin/env python
# encoding: utf-8

"""
This Script queries a Infoblox (IPAM) database via API and extracts a list of the configured networks including all it's
extended Attributes (extattrs).
It then builds a list of objects in the form of "network attribute", e.g. "10.0.0.0/24 Berlin", converts it in JSON format
and uploads it into a Riverbed SteelCentral Profiler in the Group "ByLocation" (or whatever you specify in the value
list below.

Using a config file type declaration was preferred over ArgumentParser as this script will probably run via
a cronjob.


"""

__author__ = 'Andre Dieball (andre@dieball.net)'
__copyright__ = 'Copyright (c) 2015 Andre Dieball'
__license__ = 'GPLv3'
__vcs_id__ = '$'
__version__ = '1.0.0'


def main():

    import base64
    import httplib
    import json
    import sys

    ################ Variables #########################################################################
    ip_ipam = '192.168.158.136'                         # IP or FQDN of IPAM
    ip_rvbd = '10.17.0.81'                              # IP or FQDN of Riverbed SteelCentral Profiler
    hostgroup = 'ByLocation'                            # Name or ID of Hostgrouptype to use
    auth_ipam = 'admin:infoblox'                        # username:password of IPAM
    auth_rvbd = 'admin:password'                      # username:password of SteelCentral Profiler
    extattrs = 'Location'                               # Extattr to use (default: Location)

    ################ STOP EDITING ANYTHING BELOW #######################################################

    # Get the Data from the InfoBlox Unit specified in the arguments
    if sys.version_info >= (2,7,9):
        import ssl
        conn = httplib.HTTPSConnection(ip_ipam, 443, context=ssl._create_unverified_context())
    else:
        conn = httplib.HTTPSConnection(ip_ipam, 443)

    headers = {"Authorization"  : "Basic %s" % base64.b64encode(auth_ipam),
               "Content-Type"   : "application/json"}

    url="https://" + ip_ipam + "/wapi/v1.2/network?_return_fields%2b=extattrs"

    conn.request('GET', url, headers=headers)
    response = conn.getresponse()

    if response.status == 200:
        print "Download was successful, converting data ........"
    elif response.status == 401:
            print "Something is wrong with your Authentication credentials"
    else:
        print "Something went wrong dude!"
        print response.reason

    net_loc = []
    resp_d = json.loads(response.read())
    for obj in resp_d:
        net_loc.append ({"cidr": obj["network"], "name": obj["extattrs"][extattrs]["value"]})

    conn.close()


    # Constructiong the RVBD API Header, Body and URL Request

    print ""
    print "Uploading you IPAM export to Riverbed SteelCentral Profiler now ...." \
    print "please be patient ...."
    print ""
    body = json.dumps(net_loc)

    if sys.version_info >= (2,7,9):
        import ssl
        conn = httplib.HTTPSConnection(ip_rvbd, 443, context=ssl._create_unverified_context())
    else:
        conn = httplib.HTTPSConnection(ip_rvbd, 443)



    headers = {"Authorization"  : "Basic %s" % base64.b64encode(auth_rvbd),
               "Content-Type"   : "application/json"}

    uploadurl = "https://" + ip_rvbd + "/api/profiler/1.4/host_group_types/" + hostgroup + "/config/"

    # Pushing the created List to the Profiler via API
    conn.request('PUT', uploadurl, body=body, headers=headers)
    response = conn.getresponse()

    if response.status == 204 and response.reason == "No Content":
        print "Upload was successful, please double check HostGroup in Profiler now!"
    elif response.status == 401:
            print "Something is wrong with your Authentication credentials"
    else:
        print "Something went wrong dude!"
        print response.reason



if __name__ == '__main__':
    main()

