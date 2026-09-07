# Student guide

Run one exercise at a time from this module. Every setup file creates the shared `09-ts-lab` namespace if it is absent, plus that case's complete healthy state; cases coexist there and are told apart by the `training.redhat.com/case` label and the case suffix on every resource name. Before applying YAML, run `oc config current-context` and `oc whoami`. Record scope, timeline, hypotheses, evidence, root cause, repair, verification, and prevention in [diagnostics/evidence-template.md](diagnostics/evidence-template.md).

`setup.yaml` carries the case's whole healthy state; `broken.yaml` and `fixed.yaml` carry only the objects that change and are always applied on top of it. Every exercise follows this lifecycle: apply `setup.yaml`; prove health; apply `broken.yaml`; diagnose; apply `fixed.yaml`; prove the stated success conditions; reset by deleting the case's objects by label and reapplying setup; then inspect what that label selects before deleting it for cleanup. Never delete the `09-ts-lab` namespace itself: it holds every other case. Deletion is irreversible; storage data is disposable.

`oc get events` is namespace-wide and therefore shows every case at once; read it against your own case's object names.

## 01 — Rollout cannot start (30 minutes)

Determine why a replacement Pod cannot start and distinguish a bad image reference from authentication or registry reachability.

```bash
oc apply -f manifests/01-image-pull/setup.yaml
oc -n 09-ts-lab rollout status deployment/app-01 --timeout=120s
oc apply -f manifests/01-image-pull/broken.yaml
oc -n 09-ts-lab get pods -l training.redhat.com/case=01
oc -n 09-ts-lab describe pod -l training.redhat.com/case=01
oc -n 09-ts-lab get events --sort-by=.metadata.creationTimestamp
oc apply -f manifests/01-image-pull/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-01 --timeout=120s
oc -n 09-ts-lab exec deploy/diagnostic-client-01 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-01:8080/",timeout=8).status)'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --wait=true --timeout=180s
oc apply -f manifests/01-image-pull/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --wait=true --timeout=180s
```

Evidence: waiting reason/event and declared image. Success: intended image, Ready replica, HTTP 200.

## 02 — Container repeatedly restarts (30 minutes)

Determine why a process starts and exits. Record restart count, exit code, and current/previous logs.

```bash
oc apply -f manifests/02-crash-loop/setup.yaml
oc apply -f manifests/02-crash-loop/broken.yaml
oc -n 09-ts-lab get pods -l training.redhat.com/case=02
oc -n 09-ts-lab describe pod -l training.redhat.com/case=02
oc -n 09-ts-lab logs deploy/app-02
oc -n 09-ts-lab logs deploy/app-02 --previous
oc apply -f manifests/02-crash-loop/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-02 --timeout=120s
oc -n 09-ts-lab exec deploy/diagnostic-client-02 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-02:8080/",timeout=8).status)'
oc -n 09-ts-lab get pods -l training.redhat.com/case=02
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --wait=true --timeout=180s
oc apply -f manifests/02-crash-loop/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --wait=true --timeout=180s
```

Success: Ready and HTTP 200 with no restart-count increase during a short observation.

## 03 — Running application gets no traffic (30 minutes)

Show that readiness failed without restarting the process and inspect EndpointSlice readiness.

```bash
oc apply -f manifests/03-readiness/setup.yaml
oc apply -f manifests/03-readiness/broken.yaml
oc -n 09-ts-lab get pods -l training.redhat.com/case=03
oc -n 09-ts-lab describe pod -l training.redhat.com/case=03
oc -n 09-ts-lab get endpointslice -l kubernetes.io/service-name=app-03 -o yaml
oc apply -f manifests/03-readiness/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-03 --timeout=120s
oc -n 09-ts-lab get endpointslice -l kubernetes.io/service-name=app-03 -o yaml
oc -n 09-ts-lab exec deploy/diagnostic-client-03 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-03:8080/",timeout=8).status)'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --wait=true --timeout=180s
oc apply -f manifests/03-readiness/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --wait=true --timeout=180s
```

## 04 — Pod remains Pending (30 minutes)

Compare Pod placement requirements with node labels. Use instructor output if cluster reads are denied; never label a shared node.

```bash
oc apply -f manifests/04-scheduling/setup.yaml
oc apply -f manifests/04-scheduling/broken.yaml
oc -n 09-ts-lab get pods -l training.redhat.com/case=04 -o wide
oc -n 09-ts-lab describe pod -l training.redhat.com/case=04
oc -n 09-ts-lab get deployment app-04 -o yaml
oc get nodes --show-labels
oc apply -f manifests/04-scheduling/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-04 --timeout=120s
oc -n 09-ts-lab exec deploy/diagnostic-client-04 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-04:8080/",timeout=8).status)'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --wait=true --timeout=180s
oc apply -f manifests/04-scheduling/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --wait=true --timeout=180s
```

## 05 — Scale request is rejected (30 minutes)

This case has no diagnostic Pod. A quota-rejected Pod may never exist; find `FailedCreate` at the ReplicaSet rather than looking for a Pending Pod.

```bash
oc apply -f manifests/05-quota/setup.yaml
oc apply -f manifests/05-quota/broken.yaml
oc -n 09-ts-lab get deploy,rs,pods,resourcequota -l training.redhat.com/case=05
oc -n 09-ts-lab describe rs -l training.redhat.com/case=05
oc -n 09-ts-lab describe resourcequota lab-pods-05
oc apply -f manifests/05-quota/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-05 --timeout=120s
oc -n 09-ts-lab get deploy,pods,resourcequota -l training.redhat.com/case=05
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --wait=true --timeout=180s
oc apply -f manifests/05-quota/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --wait=true --timeout=180s
```

Success: one desired/available Pod within quota and no current replica deficit.

The quota carries `scopes: [BestEffort]`, so it counts only Pods that declare no CPU or memory requests. This case's Pods are the only BestEffort ones in the lab, so the one-Pod cap applies to this exercise alone rather than to the shared namespace.

## 06 — Healthy Pods, broken Service (30 minutes)

Compare Service selector and Pod labels, EndpointSlices, a direct Pod-IP request, and the Service request.

```bash
oc apply -f manifests/06-service-selector/setup.yaml
oc apply -f manifests/06-service-selector/broken.yaml
oc -n 09-ts-lab get pods -l training.redhat.com/case=06 -o wide --show-labels
oc -n 09-ts-lab get service app-06 -o yaml
oc -n 09-ts-lab get endpointslice -l kubernetes.io/service-name=app-06 -o yaml
oc -n 09-ts-lab exec deploy/diagnostic-client-06 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-06:8080/",timeout=3)' || true
oc apply -f manifests/06-service-selector/fixed.yaml
oc -n 09-ts-lab get endpointslice -l kubernetes.io/service-name=app-06 -o yaml
oc -n 09-ts-lab exec deploy/diagnostic-client-06 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-06:8080/",timeout=8).status)'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --wait=true --timeout=180s
oc apply -f manifests/06-service-selector/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --wait=true --timeout=180s
```

Repairing the selector must not restart the healthy application Pod.

## 07 — NetworkPolicy denial (30 minutes)

Prove DNS and ready backends before policy. Policies are additive: retain denial and allow only `role=diagnostic-client` on TCP/8080.

```bash
oc apply -f manifests/07-network-policy/setup.yaml
oc apply -f manifests/07-network-policy/broken.yaml
oc -n 09-ts-lab get pods,svc,endpointslice,networkpolicy -l training.redhat.com/case=07 --show-labels
oc -n 09-ts-lab exec deploy/diagnostic-client-07 -- python3.12 -c 'import socket; print(socket.gethostbyname("app-07"))'
oc -n 09-ts-lab exec deploy/diagnostic-client-07 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-07:8080/",timeout=3)' || true
oc apply -f manifests/07-network-policy/fixed.yaml
oc -n 09-ts-lab exec deploy/diagnostic-client-07 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-07:8080/",timeout=8).status)'
oc -n 09-ts-lab exec deploy/unapproved-client-07 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-07:8080/",timeout=3)' || true
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --wait=true --timeout=180s
oc apply -f manifests/07-network-policy/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --wait=true --timeout=180s
```

## 08 — Pending PVC (30 minutes)

Use only after default dynamic provisioning is validated; otherwise use 08b. The invalid class is intentional. Do not patch immutable `storageClassName` or claim recovery from an unbound PVC.

```bash
oc apply -f manifests/08-storage/setup.yaml
oc apply -f manifests/08-storage/broken.yaml
oc -n 09-ts-lab get pvc,pods -l training.redhat.com/case=08
oc -n 09-ts-lab describe pvc invalid-data-08
oc -n 09-ts-lab describe pod -l app=storage-consumer-08
oc get storageclass
oc apply -f manifests/08-storage/fixed.yaml
oc -n 09-ts-lab delete pvc invalid-data-08 --ignore-not-found
oc -n 09-ts-lab rollout status deployment/storage-consumer-08 --timeout=120s
oc -n 09-ts-lab exec deploy/storage-consumer-08 -- sh -c 'printf lab-ok >/data/probe; test "$(cat /data/probe)" = lab-ok'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --wait=true --timeout=180s
oc apply -f manifests/08-storage/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --wait=true --timeout=180s
```

Storage data is disposable. Never delete shared PVs or change the default StorageClass.

## 08b — Missing configuration key (30 minutes)

Show `CreateContainerConfigError`, compare `configMapKeyRef` with `app-settings-08b`, and explain why no previous application log is expected.

```bash
oc apply -f manifests/08b-configuration/setup.yaml
oc apply -f manifests/08b-configuration/broken.yaml
oc -n 09-ts-lab get pods,configmap -l training.redhat.com/case=08b
oc -n 09-ts-lab describe pod -l training.redhat.com/case=08b
oc -n 09-ts-lab get deployment app-08b -o yaml
oc -n 09-ts-lab get configmap app-settings-08b -o yaml
oc apply -f manifests/08b-configuration/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-08b --timeout=120s
oc -n 09-ts-lab exec deploy/diagnostic-client-08b -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-08b:8080/",timeout=8).status)'
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --wait=true --timeout=180s
oc apply -f manifests/08b-configuration/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --wait=true --timeout=180s
```

## 09 — Capstone (45 minutes)

Restore the approved client path and preserve unapproved-client denial. Work from Pod lifecycle to Service selection to policy, re-testing after each layer because earlier faults mask later ones.

```bash
oc apply -f manifests/09-capstone/setup.yaml
oc apply -f manifests/09-capstone/broken.yaml
oc -n 09-ts-lab get deploy,rs,pods,svc,endpointslice,networkpolicy -l training.redhat.com/case=09 --show-labels
oc -n 09-ts-lab get events --sort-by=.metadata.creationTimestamp
oc apply -f manifests/09-capstone/fixed.yaml
oc -n 09-ts-lab rollout status deployment/app-09 --timeout=120s
oc -n 09-ts-lab get endpointslice -l kubernetes.io/service-name=app-09 -o yaml
oc -n 09-ts-lab exec deploy/diagnostic-client-09 -- python3.12 -c 'import urllib.request; print(urllib.request.urlopen("http://app-09:8080/",timeout=8).status)'
oc -n 09-ts-lab exec deploy/unapproved-client-09 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-09:8080/",timeout=3)' || true
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --wait=true --timeout=180s
oc apply -f manifests/09-capstone/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --wait=true --timeout=180s
```
