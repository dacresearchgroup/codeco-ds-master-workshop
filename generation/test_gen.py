'''
# Maintainer: 
- Panagiotis Karamolegkos <pkaram@unipi.gr>
Copyright (c) 2024 University of Piraeus Research Centre (UPRC)
Licensed under the MIT License.
'''

# Library for Dummy Monitoring Functionality
from random import randint

# This is a Dummy Response of the ACM Monitoring Functionality
def scrape_acm(node_name):
    return {
        "cpu"           : str(randint(1, 10)),
        "mem"           : str(randint(1, 10)),
        "node_failure"  : randint(1, 10),
        "node_energy"   : str(randint(1, 10)),
        "node_sec"      : str(randint(1, 10))
    }

# This is a Dummy Response of the MDM Monitoring Functionality
def scrape_mdm(node_name):
    return {
        "freshness"     : str(randint(1, 100)),
        "compliance"    : str(randint(11, 100)),
        "portability"   : str(randint(11, 100))
    }

# This is a Dummy Response of the NetMA Monitoring Functionality
def scrape_netma(node_name):
    return {
        "link_id"           : str(randint(101, 200)),
        "link_failure"      : randint(101, 200),
        "node_net_failure"  : randint(101, 200),
        "ebw"               : str(randint(101, 200)),
        "ibw"               : str(randint(101, 200)),
        "latency"           : str(randint(101, 200)),
        "uid_visits"        : str(randint(101, 200)),
        "uid_location"      : str(randint(101, 200)),
        "zone"              : str(randint(101, 200)),
        "node_degree"       : str(randint(101, 200)),
        "path_length"       : str(randint(101, 200)),
        "link_energy"       : str(randint(101, 200)),
        "node_net_energy"   : str(randint(101, 200))
    }