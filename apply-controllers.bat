@echo off

:: Author: Panagiotis Karamolegkos (UPRC)
:: .\apply-controllers

:: Install the ACM Controller
kubectl "create" "namespace" "he-codeco-acm"
kubectl "apply" "-f" "%CD%\acm-controller\acm-crd.yaml"
kubectl "apply" "-f" "%CD%\acm-controller\acm-role.yaml"
kubectl "apply" "-f" "%CD%\acm-controller\acm-role-binding.yaml"
kubectl "apply" "-f" "%CD%\acm-controller\acm-controller-deployment.yaml"

:: Install the MDM Controller
kubectl "create" "namespace" "he-codeco-mdm"
kubectl "apply" "-f" "%CD%\mdm-controller\mdm-crd.yaml"
kubectl "apply" "-f" "%CD%\mdm-controller\mdm-role.yaml"
kubectl "apply" "-f" "%CD%\mdm-controller\mdm-role-binding.yaml"
kubectl "apply" "-f" "%CD%\mdm-controller\mdm-controller-deployment.yaml"

:: Install the NetMA Controller
kubectl "create" "namespace" "he-codeco-netma"
kubectl "apply" "-f" "%CD%\netma-controller\netma-crd.yaml"
kubectl "apply" "-f" "%CD%\netma-controller\netma-role.yaml"
kubectl "apply" "-f" "%CD%\netma-controller\netma-role-binding.yaml"
kubectl "apply" "-f" "%CD%\netma-controller\netma-controller-deployment.yaml"