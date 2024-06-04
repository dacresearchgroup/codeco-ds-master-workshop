# Author: Panagiotis Karamolegkos (UPRC)
# chmod -R 777 .
# ./delete-controllers.sh

# Delete the ACM Controller
kubectl delete -f ./acm-controller/acm-controller-deployment.yaml
kubectl delete -f ./acm-controller/acm-role-binding.yaml
kubectl delete -f ./acm-controller/acm-role.yaml
kubectl delete -f ./acm-controller/acm-crd.yaml
kubectl delete namespace he-codeco-acm

# Delete the MDM Controller
kubectl delete -f ./mdm-controller/mdm-controller-deployment.yaml
kubectl delete -f ./mdm-controller/mdm-role-binding.yaml
kubectl delete -f ./mdm-controller/mdm-role.yaml
kubectl delete -f ./mdm-controller/mdm-crd.yaml
kubectl delete namespace he-codeco-mdm

# Delete the NetMA Controller
kubectl delete -f ./netma-controller/netma-controller-deployment.yaml
kubectl delete -f ./netma-controller/netma-role-binding.yaml
kubectl delete -f ./netma-controller/netma-role.yaml
kubectl delete -f ./netma-controller/netma-crd.yaml
kubectl delete namespace he-codeco-netma