'''
# Maintainer: 
- Panagiotis Karamolegkos <pkaram@unipi.gr>
Copyright (c) 2024 University of Piraeus Research Centre (UPRC)
Licensed under the MIT License.
'''

import time
from kubernetes import client, config
from traffic_generator import scrape_netma
import yaml

# Load the Kubernetes configuration from the default location
config.load_incluster_config()
v1 = client.CustomObjectsApi()

# Path to the YAML file
file_path = "netma-crd.yaml"        # Could become an environment variable

# Open the file and load the YAML data
with open(file_path, 'r') as file:
    yaml_data = yaml.load(file, Loader=yaml.FullLoader)

# Define the CR object details
cr_namespace = yaml_data["metadata"]["namespace"]       # Namespace where the CR object should be created
cr_plural = yaml_data["spec"]["names"]["plural"]        # Plural name of the CRD (CustomResourceDefinition)
cr_group = yaml_data["spec"]["group"]                   # Group of the CRD
cr_version = yaml_data["spec"]["versions"][0]["name"]   # Version of the CRD
cr_kind = yaml_data["spec"]["names"]["kind"]            # Kind of the CRD

# Define the component metrics
component_metrics = {}
properties = yaml_data["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]["properties"]

for property in properties:
    component_metrics[property] = None

while True:
    try:
        # Get the list of nodes in the cluster
        core_v1 = client.CoreV1Api()
        nodes = core_v1.list_node().items

        for node in nodes:
            # Get the values of this node
            node_name = node.metadata.name
            answer = scrape_netma(node_name)
            answer["node_name"] = node_name
            # print(answer["packetloss"])

            # Define the name of the CR object based on the node's name
            cr_name = f"{node_name}-object"
            
            # Define the CR object body with the new specifications
            cr_body = {
                "apiVersion": f"{cr_group}/{cr_version}",
                "kind": cr_kind,
                "metadata": {"name": cr_name, "namespace": cr_namespace},
                "spec": {}
            }

            # Fill the CR object body with the new specs
            for component_metric in component_metrics:
                cr_body["spec"][component_metric] = answer[component_metric]
            
            # Try to create or patch the CR object
            try:
                v1.create_namespaced_custom_object(
                    group=cr_group,
                    version=cr_version,
                    namespace=cr_namespace,
                    plural=cr_plural,
                    body=cr_body,
                )
                print(f"CR object '{cr_name}' created.")
            except client.rest.ApiException as e:
                if e.status == 409:
                    # If object already exists, patch it
                    v1.patch_namespaced_custom_object(
                        group=cr_group,
                        version=cr_version,
                        namespace=cr_namespace,
                        plural=cr_plural,
                        name=cr_name,
                        body=cr_body,
                    )
                    print(f"CR object '{cr_name}' patched.")
                else:
                    print(f"Error creating/patching CR object '{cr_name}': {e}")
        
        time.sleep(1)  # Wait for 1 second before the next iteration
        
    except KeyboardInterrupt:
        print("Exiting the loop.")
        break