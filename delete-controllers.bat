@echo off

:: Author: Panagiotis Karamolegkos (UPRC)
:: .\delete-controllers

:: Delete the ACM Controller
kubectl "delete" "-f" "%CD%\acm-controller\acm-controller-deployment.yaml"
kubectl "delete" "-f" "%CD%\acm-controller\acm-role-binding.yaml"
kubectl "delete" "-f" "%CD%\acm-controller\acm-role.yaml"
kubectl "delete" "-f" "%CD%\acm-controller\acm-crd.yaml"
kubectl "delete" "namespace" "he-codeco-acm"

:: Delete the MDM Controller
kubectl "delete" "-f" "%CD%\mdm-controller\mdm-controller-deployment.yaml"
kubectl "delete" "-f" "%CD%\mdm-controller\mdm-role-binding.yaml"
kubectl "delete" "-f" "%CD%\mdm-controller\mdm-role.yaml"
kubectl "delete" "-f" "%CD%\mdm-controller\mdm-crd.yaml"
kubectl "delete" "namespace" "he-codeco-mdm"

:: Delete the NetMA Controller
kubectl "delete" "-f" "%CD%\netma-controller\netma-controller-deployment.yaml"
kubectl "delete" "-f" "%CD%\netma-controller\netma-role-binding.yaml"
kubectl "delete" "-f" "%CD%\netma-controller\netma-role.yaml"
kubectl "delete" "-f" "%CD%\netma-controller\netma-crd.yaml"
kubectl "delete" "namespace" "he-codeco-netma"