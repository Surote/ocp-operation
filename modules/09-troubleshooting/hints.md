# Progressive hints

Use one hint at a time. Return to the evidence template after each hint and state what the new evidence supports or rules out.

## 01

1. Locate the earliest failing layer between scheduling and container start.
2. Inspect Pod status/events and the Deployment Pod template: `oc -n 09-ts-lab describe pod -l training.redhat.com/case=01` and `oc -n 09-ts-lab get deploy app-01 -o yaml`.
3. Compare `spec.template.spec.containers[].image` with the image declared in `setup.yaml`; decide whether the reference, authentication, or registry access is wrong.

## 02

1. Determine whether the runtime ever starts the process.
2. Inspect restart counts, `lastState.terminated`, current logs, and `oc logs --previous`.
3. Compare the container command/args in setup and current Deployment; exit code 1 plus the recognizable lab message identifies the injected process failure.

## 03

1. Separate process health from traffic eligibility.
2. Inspect Pod readiness/events and EndpointSlice endpoint conditions.
3. Compare the HTTP readiness `path` and `port` with the verified health endpoint. A readiness failure removes ready backends but does not itself restart the container.

## 04

1. Look at placement before application behavior.
2. Read the Pending Pod's scheduling events and the Deployment's placement constraints; inspect node labels only if authorized.
3. Compare `nodeSelector` keys and values with actual node labels. Remove only the injected impossible selector; do not relabel shared nodes.

## 05

1. Look before scheduling: can the controller create the desired object?
2. Describe the ReplicaSet and ResourceQuota, then compare desired replicas with actual Pods.
3. Find ReplicaSet `FailedCreate` evidence and quota `hard`/`used`. A quota-rejected Pod may never exist, so a Pending-Pod search can be empty.

## 06

1. Trace the virtual Service to selected backends.
2. Compare `oc get svc app-06 -o yaml`, Pod labels, and EndpointSlices labeled `kubernetes.io/service-name=app-06`.
3. Match every Service selector key/value against Pod labels. Repairing the selector should not require a Pod restart.

## 07

1. If DNS and ready endpoints are correct, inspect controls on the connection path.
2. List NetworkPolicies and the labels on server, approved client, and unapproved client Pods.
3. NetworkPolicy allows are additive. Retain the deny-by-default state and add ingress for only the approved client selector and application TCP port.

## 08

1. Inspect provisioning and attachment before debugging the application.
2. Describe the Pending PVC and its consumer; list StorageClasses if authorized.
3. Compare `storageClassName` with the preflight-selected class and its binding mode. Create a new recovery PVC because this field is immutable; then update the consumer.

## 08b

1. Determine whether the process starts or configuration prevents container creation.
2. Describe the Pod and compare the Deployment's `configMapKeyRef` with ConfigMap data keys.
3. Restore the referenced key name. Previous logs may not exist because no application process ran; environment values also require a new container to refresh.

## 09

1. Diagnose in dependency order: running Pod, selected backend, permitted connection.
2. Inspect Deployment/Pod events first, then Service/EndpointSlice, then NetworkPolicies and client labels.
3. Restore the approved image, restore the Service selector, and retain denial while adding a narrow allow for the approved client and application port. Re-test after each layer because earlier failures mask later ones.
