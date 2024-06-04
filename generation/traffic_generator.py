'''
# Maintainers: 
- Pepi Paraskevoulakou <e.paraskevoulakou@unipi.gr>
- Panagiotis Karamolegkos <pkaram@unipi.gr>
Copyright (c) 2023 University of Piraeus Research Centre (UPRC)
Licensed under the MIT License.
'''


# import numpy as np
import os, json, random
import requests
# import matplotlib.pyplot as plt
import networkx as nx
from kubernetes import client, config
from datetime import datetime, timedelta
import math
from collections import Counter, deque




########support outer functions########
def parse_graph_connections():
    with open(DATA_PATH, "r") as json_file:
        json_data = json.load(json_file)
        return json_data['connections'], json_data["node_names"]

def create_graph(no_nodes, connections):
    G = nx.Graph()
    G.add_nodes_from(range(no_nodes)) #define the network's nodes based on the input no of nodes
    # Add random edges

    for idx, element in enumerate(connections):
        for id,e in enumerate(element):

            if e ==1 and id!=idx:  # Probability of adding an edge
                G.add_edge(idx, id)
    return G

def get_links(name_node):
    connections, names = parse_graph_connections()
    count_ones=[]
    for idx, element in enumerate(names):
        if element == name_node:
            # print("Index is:", idx)
            break

    for idx_con, element in enumerate(connections[idx]):
        if element==1 and not idx_con==idx:
            count_ones.append(f"link_node_{names[idx_con]}")
        else:
            pass

    return str(count_ones)

def calculate_rate_of_change(data):
    # Initialize a list to store the results
    roc_results = []

    # Iterate through the data to calculate the rate of change
    for i in range(1, len(data)):
        delta = data[i] - data[i - 1]
        rate_of_change = delta / data[i - 1] if data[i - 1] != 0 else float('inf')
        
        if rate_of_change > 0:
            roc_results.append("Positive")
        elif rate_of_change < 0:
            roc_results.append("Negative")
        else:
            roc_results.append("Zero")

    return roc_results

def get_coordinates(names):
    coordinates=[]
    for i in range(len(names)):
        coordinates_list=random.choice([(39.074207,21.824312), (48.135124,11.581981), (41.385063,2.173404), (40.416775,-3.703790), (46.818188,8.227512)]) #(lat,lon)
        coordinates.append((coordinates_list[1]+random.uniform(-max_movement, max_movement), coordinates_list[0]+random.uniform(-max_movement, max_movement)))
    return coordinates

def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    r = 6371  # Radius of the Earth in kilometers. You can use 3958.8 for miles.
    distance = r * c

    return distance

def bfs(G, source):
    length_list = []
    visited = set()
    queue = deque()
    path_length = {}

    queue.append(source)
    visited.add(source)
    path_length[source] = 0

    while queue:
        node = queue.popleft()

        for neighbor in G[node]:
            if neighbor not in visited:
                queue.append(neighbor)
                visited.add(neighbor)
                path_length[neighbor] = path_length[node] + 1

    return path_length

#some attributes to be used in follwing functions
global cpu_spec
global ram_spec
global qos_class
global lon
global lat
global id_
global usergroup
global AZ_Zone
global coordinates_list
global max_movement

cpu_spec = int(random.choice([2,4,8]))
ram_spec = int(random.choice([1024,2048,4096,8192]))
qos_class = ['Guaranteed', 'Burstable', 'Besteffort']
lon, lat = 37.983810, 23.727539
id_ = random.randint(a=1, b=168)
usergroup = random.choice([1,2,3]) # stands for ["groupA", "groupB", "groupC"]
AZ_Zone = random.choice(["eu-west-1a", "eu-west-1b", "eu-west-1c"])
coordinates_list = random.choice([(39.074207,21.824312), (48.135124,11.581981), (41.385063,2.173404), (40.416775,-3.703790), (46.818188,8.227512)]) #(lat,lon)
max_movement  = 0.03



# global K8S_CLUSTER_IP
# global PROMETHEUS_PORT
# K8S_CLUSTER_IP = os.getenv("K8S_CLUSTER", "10.107.62.144")
# PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9090))
DATA_PATH = os.getenv("DATA_PATH", "./config.json")


#some global variables to be used in follwing functions within classes

global PROMETHEUS_URL
global G_ 

config.load_incluster_config()
v1_windows = client.CoreV1Api()
namespace_windows = "monitoring"
pod_name_windows = "prometheus-k8s-0"
pod_windows = v1_windows.read_namespaced_pod(name=pod_name_windows, namespace=namespace_windows)
# PROMETHEUS_URL = "http://prometheus-k8s.monitoring.svc.cluster.local:9090"
PROMETHEUS_URL = f"http://{pod_windows.status.pod_ip}:9090"


if os.path.isfile(DATA_PATH):
    G_ = create_graph(len(parse_graph_connections()[1]), parse_graph_connections()[0])
# main function to run the generator 

class k8S_connection:
    def __init__(self) -> None:
        self.dummy = "dummy"
        self.config = None
        self.v1=None
        self.prometheus_url = None
    
    def k8s_establish_connection(self):
        try:
        #kubernetes configuration actions
            self.config = config.load_incluster_config() # action to create the configuration
            self.v1 = client.CoreV1Api() # actions to create a Kubernetes API client
        except Exception as e:
            pass
    
    def prometheus_connection(self):
        try:
            self.prometheus_url = PROMETHEUS_URL # Changed to get the URL in an automatic way
        except Exception as e:
            pass

class ACM_metrics(k8S_connection):

    def __init__(self, name_node) -> None:
        super().__init__()
        self.k8s_establish_connection()
        self.prometheus_connection()
        self.name = name_node
        self.CPU_value = None #str
        self.mem_value = None #int
        self.node_energy_value = None #string
        self.node_sec_value = None #int

    def get_CPU(self):
        try:
            query = f'sum(rate(container_cpu_usage_seconds_total{{node="{self.name}"}}[5m]))'
            response = requests.get(f'{self.prometheus_url}/api/v1/query', params={'query': query})
            data = response.json()
            if 'data' in data and 'result' in data['data']:
                result = data['data']['result'][0]
                self.cpu_utilization_value = str(result['value'][1])

        except Exception as e:
            print(e)
            self.CPU_value = "NaN"        
        
    def get_mem(self):
        try:
            prometheus_url = self.prometheus_url+"/api/v1/query"
            query = 'node_memory_MemAvailable_bytes{instance="'+self.name+'"}'
            params = {
                'query': query
            }
            
            data = requests.get(prometheus_url, params=params)
            data = data.json()
            
            result = data['data']['result'][0]
            available_memory_bytes = float(result['value'][1])

            # Convert the available memory to an integer (optional)
            self.mem_value = available_memory_bytes
            # print(data)
            # print(self.memory_consumption_value)

        except Exception as e:
            print(e)
            self.mem_value = "NaN"
        
        if self.mem_value !="NaN":
            self.mem_value = int(self.mem_value)
        else:
            self.mem_value = str(self.mem_value)
    
    def get_node_failure(self):
        try:
            prometheus_url = self.prometheus_url+"/api/v1/query"
            query = 'up{job="node-exporter", instance="'+self.name+'"}'
            params = {
                'query': query
            }
            
            data = requests.get(prometheus_url, params=params)
            data = data.json()
            
            if 'data' in data and 'result' in data['data'] and data['data']['result']:
                self.node_failure_value = int(data['data']['result'][0]['value'][1])
            else:
                self.node_failure_value="NaN"
            # print(self.resillience_value)

        except Exception as e:
            print(e)
            self.node_failure_value = "NaN"
        
        if self.node_failure_value != "NaN":
            self.node_failure_value = int(self.node_failure_value)
        else:
            self.node_failure_value = str(self.node_failure_value)  


    def get_node_energy(self):
        try:
            cpu_power_coefficient = 0.01+random.uniform(0.01, 0.03)  # watts per core
            memory_power_coefficient = 0.0001+random.uniform(0.0001, 0.0003)  # watts per byte
            # Calculate energy consumption
            cpu_energy = float(self.cpu_utilization_value) * cpu_power_coefficient
            memory_energy = float(self.mem_value) * memory_power_coefficient
            self.node_energy_value = str(cpu_energy + memory_energy)
            # print(self.energy_consumption_value)
        except Exception as e:
            print(e)
            self.energy_consumption_value = "NaN"


    def get_node_sec(self):
        try: 
            prometheus_url = self.prometheus_url+"/api/v1/query"
            received_query = 'sum(node_network_receive_bytes_total{instance="'+self.name+'", job="node-exporter"})'
            transmited_query = 'sum(node_network_transmit_bytes_total{instance="'+self.name+'", job="node-exporter"})'
            
            received_params = {
                'query': received_query
            }
            
            transmited_params = {
                'query': transmited_query
            }
            
            response_received = requests.get(prometheus_url, params=received_params)
            response_received_json = response_received.json()
            
            response_transmitted = requests.get(prometheus_url, params=transmited_params)
            response_transmitted_json = response_transmitted.json()
            
            diff_ = float(response_transmitted_json['data']['result'][0]['value'][1]) - float(response_received_json['data']['result'][0]['value'][1])
            # print(diff_)
            if diff_>=0:
                self.node_sec_value = "High"
            elif diff_<0 and diff_>-15:
                self.node_sec_value="Medium"
            elif diff_<=-15:
                self.node_sec_value="Low"
            # print(self.security_value)
        except Exception as e:
            print(e)
            self.node_sec_value = "NaN"

class NetMa_metrics(k8S_connection):
    def __init__(self, name_node):
        super().__init__()
        self.k8s_establish_connection()
        self.prometheus_connection()
        self.name = name_node
        self.id_ = id_
        self.link_id = get_links(name_node)
        self.coordinates = get_coordinates(parse_graph_connections()[1])
        self.name_nodes = parse_graph_connections()[1]
        self.no_nodes = len(parse_graph_connections()[1])
        self.link_failure=[]
        self.node_failure=None
        self.edge_connections = parse_graph_connections()[0]
        self.G = create_graph(self.no_nodes, self.edge_connections)
        self.ebw_value = None
        self.ibw_value = None
        self.packetloss_value = None
        self.Zone_value = AZ_Zone
        self.UID_visit_value = None
        self.node_degree_value = None
        self.latency_value=None
        self.pathlength_value=None
        self.node_net_energy_value = None
        self.energy_efficiency_value = None
        self.active_neighbors = None
        self.list_info = []
        self.node_net_failure_value = 0


    def get_link_failure(self):
        packetloss = []
        try: 
            prometheus_url = self.prometheus_url+"/api/v1/query"
            query = 'avg(100 * (node_network_receive_drop_total{instance="'+self.name+'"}+node_network_transmit_drop_total{instance="'+self.name+'"} ) / (node_network_receive_packets_total{instance="'+self.name+'"} + node_network_transmit_packets_total{instance="'+self.name+'"}))'
            params = {
            'query': query
            }
            for i in range(10):
                response = requests.get(prometheus_url, params=params)
                response = response.json()
                # print(response)
                packetloss.append(float(response['data']['result'][0]['value'][0]))
                packetloss_elements_window = calculate_rate_of_change(packetloss)
                # Use Counter to count element frequencies
                packetloss_rate_of_change_counts = Counter(packetloss_elements_window)
            
            if packetloss_rate_of_change_counts['Positive']> packetloss_rate_of_change_counts['Negative']:
                if packetloss_rate_of_change_counts['Positive']>=8:
                    percentage = 0.55
                    index = int(len(self.link_id) * percentage)
                    self.link_failure_value = random.randint(1,index)
                    self.active_neighbors = len(self.link_id) - self.link_failure_value
                elif packetloss_rate_of_change_counts['Positive']>=5 and packetloss_rate_of_change_counts['Positive']<8:
                    percentage = 0.35
                    index = int(len(self.link_id) * percentage)
                    self.link_failure_value = random.randint(1,index)
                    self.active_neighbors = len(self.link_id) - self.link_failure_value

                elif packetloss_rate_of_change_counts['Positive']<5 and packetloss_rate_of_change_counts['Positive']>=2:
                    percentage = 0.10
                    index = int(len(self.link_id) * percentage)
                    self.link_failure_value = random.randint(1,index)
                    self.active_neighbors = len(self.link_id) - self.link_failure_value

                elif packetloss_rate_of_change_counts['Positive']<=1:
                    self.link_failure_value = 0
                    self.active_neighbors = len(self.link_id) - self.link_failure_value
            else:
                self.link_failure_value = 0
                self.active_neighbors = len(self.link_id) - self.link_failure_value

        except Exception as e:
            print(e)
            self.link_failure_value = "NaN"
            self.active_neighbors = 0

    
    def get_node_net_failure(self):
        if self.link_failure == "NaN":
            self.link_failure = 0.000000001
        self.node_net_failure_value += self.node_net_failure_value+ self.link_failure_value


    def get_ebw(self):
        try:
            query =  'sum(rate(node_network_transmit_bytes_total{instance="'+self.name+'"}[1m]))'
            params = {
                'query': query
            }
            
            response = requests.get(self.prometheus_url+"/api/v1/query", params=params)
            response = response.json()
            # print(response)
            self.ebw_value = str(response['data']['result'][0]['value'][1])
            # print(self.ebw_value)
        except Exception as e:
            print(e)
            self.ebw_value = "NaN"

    def get_ibw(self):
        try:
            # query = 'node_network_transmit_bytes_total'
            query =  'sum(node_network_receive_bytes_total{instance="'+self.name+'"})-sum(node_network_transmit_bytes_total{instance="'+self.name+'"})'
            params = {
                'query': query
            }
            
            response = requests.get(self.prometheus_url+"/api/v1/query", params=params)
            response = response.json()
            # print(response)
            self.ibw_value = str(response['data']['result'][0]['value'][1])
            # print(self.ibw_value)
        except Exception as e:
            print(e)
            self.ibw_value = "NaN"

    #calculated by node_network_receive_errors_total/total samples collected
    def get_latency(self):
        try:
            prometheus_url = self.prometheus_url+"/api/v1/query"
            query = 'kubelet_http_requests_duration_seconds_count{node="'+self.name+'"}'

            # Define any additional query parameters, such as time range
            params = {
                'query': query
            }
            
            response = requests.get(prometheus_url, params=params)
            if response.status_code ==200:
                data = response.json()
                result = data['data']['result']
                
                if result:
                    self.latency = result[0]['value'][1]
                else:
                    self.latency = 0.0

            else:
                print("Response status code:", response.status_code)
                self.latency = "NaN"
        except Exception as e:
            #print("Failed to fetch data from Prometheus related to latency")
            print("Error:", e)
            self.latency = "NaN"


    def get_UID_visits(self):
        # uniform_samples = np.random.uniform(0, 1, self.no_nodes)
        uniform_samples = [round(random.uniform(0, 1), 7) for i in range(self.no_nodes)]    # Better for many architectures
        list_with_nodes = parse_graph_connections()[1]
        adj_matrices_list = parse_graph_connections()[0]

        try:
            idx_ = list_with_nodes.index(self.name)
            for id_,element in enumerate(uniform_samples):
                if element>=0.5:
                    adj_matrices_list[idx_][id_]+=1
                else:
                    pass
            self.UID_visit_value = adj_matrices_list[idx_]

        except Exception as e:
            self.UID_visit_value = adj_matrices_list[idx_]
    
    def get_uid_location(self):
        info = {"id": self.name+"-codeco-node"}
        info["lon"] = coordinates_list[1]
        info["lat"] = coordinates_list[0]
        info['lon'] = info['lon']+random.uniform(-max_movement, max_movement)
        info['lat'] = info['lat']+random.uniform(-max_movement, max_movement)
        self.list_info.append((info['lon'], info['lat']))
        return str(info['lat']) + ";" + str(info['lon']) 

    def get_zone(self):
        pass
        #already provided in the __init__

    def get_node_degree(self):
        pass
        #already provided as the attribut self.active_neighbors
    
    def get_pathlength(self):
        range_start = 0  # Start of the range (inclusive)
        range_end =  self.no_nodes # End of the range (exclusive)
        num_unique_elements = self.active_neighbors # Number of unique random integers
        if self.active_neighbors !=0:
            length_list=[]
            # Create a list of unique random integers
            active_nodes = random.sample(range(range_start, range_end), min(range_end, num_unique_elements))
            sorted_nodes = active_nodes.sort()

            path_lengths = bfs(G_,self.name_nodes.index(self.name))
            for target_node,length in path_lengths.items():
                length_list.append(length)
            self.pathlength_value  = str(sum(length_list)/len(length_list))
        else:
            self.pathlength_value = "NaN"

    
    def get_link_energy_expediture(self):
        graph=[]
        for name in self.name_nodes:
            graph_node_list=[]
            node_coordinates= self.coordinates[self.name_nodes.index(name)]

            distances = []
            for idx_,element in enumerate(self.edge_connections[self.name_nodes.index(name)]):
                if element==1:
                    distances.append(round(haversine_distance(node_coordinates[0], node_coordinates[1], self.coordinates[idx_][0], self.coordinates[idx_][1]),2))
                else:
                    distances.append(-999)

            for element in distances:
                if element ==0 or element==-999:
                    graph_node_list.append(0)

                else:
                    if element == max(distances):
                        graph_node_list.append(120)
                    else:

                        graph_node_list.append(random.choice([80,100]))
            graph.append(graph_node_list)

        # Initialize a list to store the energy per link for each node
        energy_per_node = [0] * len(graph)

        # Calculate the energy per link for each node
        for node in range(len(graph)):
            for neighbor in range(len(graph)):
                if node != neighbor:
                    energy_per_node[node] += graph[node][neighbor]
        self.link_energy_expediture_value = float(energy_per_node[self.name_nodes.index(self.name)]*self.active_neighbors)
        return str(self.link_energy_expediture_value)


    def get_node_net_energy(self):
        energy_efficiency=[]
        try:
            tests = 31  # Can be changed
            for i in range(tests):
                energy_effciency_query = 'rate(node_network_transmit_bytes_total{instance="'+self.name +'"}[5m])'
                response = requests.get(self.prometheus_url+"/api/v1/query", params={'query': energy_effciency_query})
                energy_efficiency_data = response.json()
                energy_efficiency_data_result = energy_efficiency_data['data']['result']
                
                found = False
                for res in energy_efficiency_data_result:
                    if res["metric"]["device"] == "cni0":
                        found = True
                        energy_efficiency.append(float(res["value"][1]))
                
                if not found:
                    energy_efficiency.append(0)
            
            filtered_energy_efficiency_list = [x for x in energy_efficiency if x != 0]
            final_filtered_energy_eff_list = calculate_rate_of_change(filtered_energy_efficiency_list)
            energy_efficiency_list_counts = Counter(final_filtered_energy_eff_list)
            # print(energy_efficiency_list_counts)

            if not "Zero" in energy_efficiency_list_counts.keys():
                energy_efficiency_list_counts["Zero"] = 0
            if not "Positive" in energy_efficiency_list_counts.keys():
                energy_efficiency_list_counts["Positive"] = 0
            if not "Negative" in energy_efficiency_list_counts.keys():
                energy_efficiency_list_counts["Negative"] = 0
                
            del energy_efficiency_list_counts['Zero']

            if energy_efficiency_list_counts['Positive']> energy_efficiency_list_counts['Negative']:
                self.node_net_energy_value = 70+random.uniform(-30, 20)
            else:
                self.node_net_energy_value = 70+random.uniform(-10, 30)

        except Exception as e:
            print(e)
            self.node_net_energy_value = "NaN"
        
        if self.node_net_energy_value!= "NaN":
            self.node_net_energy_value = float(self.node_net_energy_value)
        else:
            self.node_net_energy_value = str(self.node_net_energy_value)


class MDM_metrics(k8S_connection):
    list_with_coordinates = []
    eu_dist = []

    def __init__(self, name_node):
        super().__init__()
        self.k8s_establish_connection()
        self.prometheus_connection()
        self.name = name_node
        self.freshness_value = None
        self.compliance_value = 0
        self.portability_value = None
        self.zone = AZ_Zone
        self.former_latency_cost= 20+random.uniform(-0.9,0.9)
        self.now_latency_cost = None
        self.eu_dist = []
    
    def get_freshness(self): #str
        try:
            freshness_query = f'rate(node_network_receive_bytes_total{{instance="{self.name}"}}[1m])'
            response = requests.get(f'{self.prometheus_url}/api/v1/query', params={'query': freshness_query})
            if response.status_code == 200:
                freshness_data = response.json()
                freshness_result = freshness_data.get('data', {}).get('result', [])

            if freshness_result:
                self.freshness_value = str(freshness_result[0]['value'][1])
            else:
                self.freshness_value = None

        except Exception as e:
            print(e)
            self.freshness_value = "NaN"

    # dummy logic, thigher values indicate better adherence to regulations and policies for the corresponding zone and application
    def get_compliance(self):
        list_woth_Zones = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
        value = self.zone
        if value == list_woth_Zones[0]:
            lat_, lon_ = 53.349805, -6.26031
        if value == list_woth_Zones[1]:
            lat_, lon_ = 52.520008, 13.404954
        else:
            lat_, lon_ = 52.379189, 4.899431
        
        ue_coord_lat, ue_coord_lon = lat_+random.uniform(-max_movement, max_movement), lon_+random.uniform(-max_movement, max_movement)
        MDM_metrics.list_with_coordinates.append([ue_coord_lat, ue_coord_lon])
        # print(MDM_metrics.list_with_coordinates)
        
        if len(MDM_metrics.list_with_coordinates)>1:
            euc_dist = euclidean_distance(MDM_metrics.list_with_coordinates[-2], MDM_metrics.list_with_coordinates[-1])
            MDM_metrics.eu_dist.append(euc_dist)
            if len(MDM_metrics.eu_dist)>1:
                if MDM_metrics.eu_dist[-1]>MDM_metrics.eu_dist[-2]:
                    self.compliance_value = self.compliance_value+random.uniform(-0.8, 0.8)
                else:
                    self.compliance_value = self.compliance_value+random.uniform(-0.01, 1.18)
            else:
                self.compliance_value = 0
        else:
            self.compliance_value= 0 # no more that one

    #calculated by node_network_receive_errors_total/total samples collected
    def get_latency(self):
        try:
            prometheus_url = self.prometheus_url+"/api/v1/query"
            query = 'kubelet_http_requests_duration_seconds_count{node="'+self.name+'"}'

            # Define any additional query parameters, such as time range
            params = {
                'query': query
            }
            
            response = requests.get(prometheus_url, params=params)
            if response.status_code ==200:
                data = response.json()
                result = data['data']['result']
                if result:
                    return result[0]['value'][1]
                else:
                    return 0.0

            else:
                print("Response status code:", response.status_code)
                return "NaN"
        except Exception as e:
            #print("Failed to fetch data from Prometheus related to latency")
            print("Error:", e)
            return "NaN"

    #to be fixed
    def get_portability(self): 
        try:
            self.now_latency_cost = float(self.get_latency())
            self.portability_value = str(self.now_latency_cost - self.former_latency_cost)

        except Exception as e:
            print(e)
            self.portability_value = "NaN"

def scrape_acm(node):
    acm_node = ACM_metrics(node)
    acm_node.get_CPU()
    acm_node.get_mem()
    acm_node.get_node_failure()
    acm_node.get_node_energy()
    acm_node.get_node_sec()
    return {
        "cpu":          str(acm_node.cpu_utilization_value),
        "mem":          str(acm_node.mem_value),
        "node_failure": int(acm_node.node_failure_value),
        "node_energy":  str(acm_node.node_energy_value),
        "node_sec":     str(acm_node.node_sec_value)
    }


def scrape_netma(name_node):
    netma_node = NetMa_metrics(name_node)
    netma_node.get_link_failure()
    netma_node.get_node_net_failure()
    netma_node.get_ebw()
    netma_node.get_ibw()
    netma_node.get_latency()
    netma_node.get_UID_visits()
    netma_node.get_pathlength()
    netma_node.get_link_energy_expediture()
    netma_node.get_node_net_energy()

    return {
        "link_id":          str(netma_node.link_id[2:-2]),
        "link_failure":     int(netma_node.link_failure_value),
        "node_net_failure": int(netma_node.node_net_failure_value),
        "ebw":              str(netma_node.ebw_value),
        "ibw":              str(netma_node.ibw_value),
        "latency":          str(netma_node.latency),
        "uid_visits":       str(';'.join(map(str, netma_node.UID_visit_value))),
        "uid_location":     str(netma_node.get_uid_location()),
        "zone":             str(netma_node.Zone_value),
        "node_degree":      str(netma_node.active_neighbors),
        "path_length":      str(netma_node.pathlength_value), #str
        "link_energy":      str(netma_node.link_energy_expediture_value), #str
        "node_net_energy":  str(netma_node.node_net_energy_value)
    }
    

def scrape_mdm(name_node,):
    mdm = MDM_metrics(name_node)
    mdm.get_freshness()
    mdm.get_portability()
    mdm.get_compliance()
    return {
        "freshness":    str(mdm.freshness_value),
        "compliance":   str(mdm.compliance_value),
        "portability":  str(mdm.portability_value) #all the features defined as str based on codeco parameters new annex
    }

# print(scrape_acm("k8s-master"))
# for i in range(5):
#     print(scrape_mdm("k8s-master"))
# for i in range(10):
#     print(scrape_netma("k8s-master"))