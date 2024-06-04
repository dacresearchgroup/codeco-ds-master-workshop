# Prerequisites
To use this code you should have the following:
- A Kubernetes Cluster (You can use [kind](https://kind.sigs.k8s.io/) for testing)
   - For this you will need a Container Engine like [Docker](https://www.docker.com/).
- Prometheus Installed in the Kubernetes Cluster (it is mandatory - there is an installation guide below)
- Be the Admin of the cluster, with access to the `default` Service Account.
- Python3 Installed

The following guide is describing the installation on Windows. To do the same for linux, it is advised to follow [this](https://gitlab.eclipse.org/eclipse-research-labs/codeco-project/experimentation-framework-and-demonstrations/data-generators-and-datasets/synthetic-data-generator) documentation. To learn more for the code, you should read the documentation in the previous hyperlink.

## Download Repo
To download this repo use the following command:
```
git clone https://github.com/dacresearchgroup/codeco-ds-master-workshop.git

cd codeco-ds-master-workshop
```

## Kind Installation
To test the code you can use kind. To make the installation you can follow the commands describe in the [Docker documentation](https://docs.docker.com/engine/install/) & [kind documentation](https://kind.sigs.k8s.io/docs/user/quick-start).

Open you Docker Engine and run the following to create a cluster:
```
kind create cluster --config config.txt --name sonem
```

The above command will use the `config.txt` file to create a 3 node cluster using `Docker` and `Kind`. The cluster will be named as `sonem`.

You can view your nodes with the following command:
```
kubectl get nodes
```

Your output should be something like the following:
```
NAME                  STATUS   ROLES           AGE   VERSION
sonem-control-plane   Ready    control-plane   8h    v1.30.0
sonem-worker          Ready    <none>          8h    v1.30.0
sonem-worker2         Ready    <none>          8h    v1.30.0
```

### Delete cluster
To delete your cluster you can use the following command:
```
kind delete cluster --name sonem
```

## Prometheus Installation
Use the following commands on the Kubernetes Master to install prometheus:
```
# Get in the Prometheus Repo
cd kube-prometheus

# Apply the following lines
kubectl apply --server-side -f manifests/setup
kubectl wait --for condition=Established --all CustomResourceDefinition --namespace=monitoring
kubectl apply -f manifests/
```

### Remove Prometheus
To Remove Prometheus that is installed, use following commands:
```
kubectl delete --ignore-not-found=true -f manifests/ -f manifests/setup
```

## Install the Synthetic Data Generator

While having a cluster and Prometheus within the cluster, run the following in the master node:
```
apply-controllers
```

## How to Uninstall the Controllers
Run the following commands to use the deletion script:
```
delete-controllers
```

## Get Information without the Extractor Script
If you want to test in a fast way the controllers, try running the following for the ACM Controller. Just fill in one of your node names in the `<node-name>` field.
```
kubectl get acm-mons <node-name>-object -o=jsonpath='{.spec.node_name}:{.spec.cpu}:{.spec.mem}:{.spec.node_failure}:{.spec.node_energy}:{.spec.node_sec} -n he-codeco-acm'
# kubectl get acm-mons sonem-worker-object -o=jsonpath='{.spec.node_name}:{.spec.cpu}:{.spec.mem}:{.spec.node_failure}:{.spec.node_energy}:{.spec.node_sec} -n he-codeco-acm
```
You can test MDM and NetMA controllers as well with the following commands:
```
kubectl get mdm-mons <node-name>-object -o=jsonpath='{.spec.node_name}:{.spec.freshness}:{.spec.compliance}:{.spec.portability} -n he-codeco-mdm
kubectl get netma-mons <node-name>-object -o=jsonpath='{.spec.node_name}:{.spec.link_id}:{.spec.link_failure}:{.spec.node_net_failure}:{.spec.ebw}:{.spec.ibw}:{.spec.latency}:{.spec.uid_visits}:{.spec.uid_location}:{.spec.zone}:{.spec.node_degree}:{.spec.path_length}:{.spec.link_energy}:{.spec.node_net_energy} -n he-codeco-netma

# kubectl get mdm-mons sonem-worker-object -o=jsonpath='{.spec.node_name}:{.spec.freshness}:{.spec.compliance}:{.spec.portability} -n he-codeco-mdm
# kubectl get netma-mons sonem-worker-object -o=jsonpath='{.spec.node_name}:{.spec.link_id}:{.spec.link_failure}:{.spec.node_net_failure}:{.spec.ebw}:{.spec.ibw}:{.spec.latency}:{.spec.uid_visits}:{.spec.uid_location}:{.spec.zone}:{.spec.node_degree}:{.spec.path_length}:{.spec.link_energy}:{.spec.node_net_energy} -n he-codeco-netma
```

# Execute the Extractor
To Execute the extractor and gather results, follow the commands below:
```
cd data-extractor
pip install -r requirements.txt
python extractor.py mode=<mode>
# python extractor.py mode=write
# python extractor.py mode=append

# To uninstall the requirements.txt
pip uninstall -r requirements.txt -y
```

# Flow Diagram

<img src="images/synthetic-generator.png" alt="Alt Text" width="400" height="300"/>

# Authors:
- Panagiotis Karamolegkos (UPRC)
- Pepi Paraskevoulakou (UPRC)