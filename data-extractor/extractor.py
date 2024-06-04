'''
# Maintainer: 
- Panagiotis Karamolegkos <pkaram@unipi.gr>
Copyright (c) 2024 University of Piraeus Research Centre (UPRC)
Licensed under the MIT License.
'''

from kubernetes import client, config
import time
from datetime import datetime
import sys
import yaml

""" Mode Check """
# Check if mode is write or append
if len(sys.argv) != 2:
    print("Usage: python extractor.py mode=<mode>")
    sys.exit(1)
elif not sys.argv[1].startswith("mode="):
    print("Usage: python extractor.py mode=<mode>")
    sys.exit(1)
else:
    mode = sys.argv[1].split("=")[1]
    if mode != "write" and mode != "append":
        print("Error: Mode can only be write or append")
        sys.exit(1)

# Keep only the first letter of the mode
mode = mode[0]

# Path to the YAML files
acm_path = "./../acm-controller/acm-crd.yaml"
mdm_path = "./../mdm-controller/mdm-crd.yaml"
netma_path = "./../netma-controller/netma-crd.yaml"

# Open the file and load the YAML data
with open(acm_path, 'r') as file:
    acm_data = yaml.load(file, Loader=yaml.FullLoader)

# Open the file and load the YAML data
with open(mdm_path, 'r') as file:
    mdm_data = yaml.load(file, Loader=yaml.FullLoader)

# Open the file and load the YAML data
with open(netma_path, 'r') as file:
    netma_data = yaml.load(file, Loader=yaml.FullLoader)

""" CRD Definition """
group = acm_data["spec"]["group"]                       # Group of the CRD
version = acm_data["spec"]["versions"][0]["name"]       # Version of the CRD
acm_namespace = acm_data["metadata"]["namespace"]       # Namespace where the CR object should be created
mdm_namespace = mdm_data["metadata"]["namespace"]       # Namespace where the CR object should be created
netma_namespace = netma_data["metadata"]["namespace"]       # Namespace where the CR object should be created
acm_plural = acm_data["spec"]["names"]["plural"]        # Plural name of the CRD (CustomResourceDefinition)
mdm_plural = mdm_data["spec"]["names"]["plural"]        # Plural name of the CRD (CustomResourceDefinition)
netma_plural = netma_data["spec"]["names"]["plural"]    # Plural name of the CRD (CustomResourceDefinition)

""" All the metrics """
metrics = []

acm_properties = acm_data["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]["properties"]
mdm_properties = mdm_data["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]["properties"]
netma_properties = netma_data["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]["properties"]

for property in acm_properties:
    metrics.append(property) if property not in metrics else metrics

for property in mdm_properties:
    metrics.append(property) if property not in metrics else metrics

for property in netma_properties:
    metrics.append(property) if property not in metrics else metrics

metrics.remove("node_name")

""" K8s Config """
config.load_kube_config()
crd_client = client.CustomObjectsApi()

""" Data Extraction """
file = open("data.csv", mode)

# Append Headers if mode is write
if mode == "w":
    # Create the first line with the headers
    line = "time" + "," + "node_name" + ","
    for metric in metrics:
        line += metric + ","

    # Remove the last comma
    line = line[:-1]

    # Add the newline character
    line += "\n"

    file.write(line)

while True:
    nodes = {}

    # Wait for 5 seconds
    time.sleep(2)

    # Fetch the CRD instance
    acm_instances = crd_client.list_namespaced_custom_object(
        group=group,
        version=version,
        namespace=acm_namespace,
        plural=acm_plural
    )
    mdm_instances = crd_client.list_namespaced_custom_object(
        group=group,
        version=version,
        namespace=mdm_namespace,
        plural=mdm_plural
    )
    netma_instances = crd_client.list_namespaced_custom_object(
        group=group,
        version=version,
        namespace=netma_namespace,
        plural=netma_plural
    )

    # Extract ACM data
    for acm_obj in acm_instances["items"]:
        nodes[acm_obj["spec"]["node_name"]] = {}
        
        for spec in acm_obj["spec"]:
            if spec == "node_name":
                continue
            nodes[acm_obj["spec"]["node_name"]][spec] = acm_obj["spec"][spec]

    # Extract MDM data
    for mdm_obj in mdm_instances["items"]:
        for spec in mdm_obj["spec"]:
            if spec == "node_name":
                continue
            nodes[mdm_obj["spec"]["node_name"]][spec] = mdm_obj["spec"][spec]

    # Extract NetMA data
    for netma_obj in netma_instances["items"]:
        for spec in netma_obj["spec"]:
            if spec == "node_name":
                continue
            nodes[netma_obj["spec"]["node_name"]][spec] = netma_obj["spec"][spec]

    # Get the datetime
    timestamp = datetime.now().timestamp()
    time_object = str(datetime.fromtimestamp(timestamp))

    # Write the data to the file
    for node_name in nodes:
        # Create the string to write to the file
        line = time_object + "," + node_name + ","
        for metric in metrics:
            line += str(nodes[node_name][metric]).replace("," , ";").replace("'", "") + "," # Bug Fix

        # Remove the last comma
        line = line[:-1]

        # Add the newline character
        line += "\n"

        file.write(line)
