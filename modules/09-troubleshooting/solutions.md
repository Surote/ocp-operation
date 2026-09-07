# Solutions

These solutions reveal the injected faults. Complete an evidence record before using them. The `Warning ...` fragments below are illustrative patterns, not captured output and not proof of validation on your cluster.

## 01 — Image pull failure

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. `oc -n 09-ts-lab get pods -l training.redhat.com/case=01` commonly shows `ErrImagePull` or `ImagePullBackOff`; `describe pod` shows image retrieval events. Prove the Pod was scheduled, inspect `status.containerStatuses`, and compare the current Deployment image with `manifests/01-image-pull/setup.yaml`. This rules out application crash and exposes a deliberately nonexistent tag in a reachable repository.

```bash
oc -n "09-ts-lab" get pods -l training.redhat.com/case=01 -o wide
oc -n "09-ts-lab" describe pod -l training.redhat.com/case=01
oc -n "09-ts-lab" get deploy app-01 -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

oc apply -f "manifests/01-image-pull/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-01 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --wait=true --timeout=180s
oc apply -f manifests/01-image-pull/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --wait=true --timeout=180s
```

The fixed manifest restores the approved image and waits for a Ready replica and Service request. A pull secret is the wrong repair unless evidence shows authentication failure; changing probes cannot make an image start.

## 02 — Process crash loop

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. The container is created, emits the lab error, exits with code 1, and accumulates restarts/backoff. Current logs can be empty during backoff; `--previous` targets the terminated instance.

```bash
oc -n "09-ts-lab" get pods -l training.redhat.com/case=02
oc -n "09-ts-lab" get pods -l training.redhat.com/case=02 -o jsonpath='{range .items[*]}{.metadata.name}{" restarts="}{.status.containerStatuses[0].restartCount}{" exit="}{.status.containerStatuses[0].lastState.terminated.exitCode}{" reason="}{.status.containerStatuses[0].lastState.terminated.reason}{"\n"}{end}'
oc -n "09-ts-lab" logs deploy/app-02 || true
oc -n "09-ts-lab" logs deploy/app-02 --previous
oc -n "09-ts-lab" get deploy app-02 -o yaml

oc apply -f "manifests/02-crash-loop/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-02 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --wait=true --timeout=180s
oc apply -f manifests/02-crash-loop/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=02 --wait=true --timeout=180s
```

The root cause is the injected exit command, and fixed YAML restores the normal Python server command. Image changes, readiness tuning, or deleting a Pod merely hide or recreate the same template fault.

## 03 — Readiness failure

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. The Pod phase remains Running while its Ready condition is false. Illustrative event text mentions an HTTP probe failure, and EndpointSlice `conditions.ready` is false. Restart count should not rise from a readiness failure alone.

```bash
oc -n "09-ts-lab" get pods -l training.redhat.com/case=03
oc -n "09-ts-lab" describe pod -l training.redhat.com/case=03
oc -n "09-ts-lab" get deploy app-03 -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet}{"\n"}'
oc -n "09-ts-lab" get endpointslice -l kubernetes.io/service-name=app-03 -o yaml

oc apply -f "manifests/03-readiness/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-03 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --wait=true --timeout=180s
oc apply -f manifests/03-readiness/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=03 --wait=true --timeout=180s
```

The injected readiness path does not return success. Fixed YAML restores `/` on port 8080. Increasing replicas or restarting Pods preserves the bad template; adding liveness can turn this into an unrelated restart failure.

## 04 — Unschedulable Pod

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. The Pod is Pending with no assigned node and scheduling evidence for unmatched node selection.

```bash
oc -n "09-ts-lab" get pods -l training.redhat.com/case=04 -o wide
oc -n "09-ts-lab" describe pod -l training.redhat.com/case=04
oc -n "09-ts-lab" get deploy app-04 -o jsonpath='{.spec.template.spec.nodeSelector}{"\n"}'
oc get nodes --show-labels

oc apply -f "manifests/04-scheduling/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-04 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --wait=true --timeout=180s
oc apply -f manifests/04-scheduling/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=04 --wait=true --timeout=180s
```

If node reads are denied, use instructor evidence. The injected selector matches no node; fixed YAML removes only it. Never label a shared node, remove legitimate platform constraints, or add broad tolerations.

## 05 — Quota admission rejection

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. The Deployment requests two replicas under `lab-pods-05`, whose one-Pod limit is already used. The ReplicaSet reports `FailedCreate` with quota evidence; the rejected second Pod usually never appears, so this is not a Pending scheduling problem.

```bash
oc -n "09-ts-lab" get deploy,rs,pods,resourcequota -l training.redhat.com/case=05
oc -n "09-ts-lab" describe rs -l training.redhat.com/case=05
oc -n "09-ts-lab" get resourcequota lab-pods-05 -o yaml
oc -n "09-ts-lab" get deploy app-05 -o jsonpath='{.spec.replicas}{" desired, available="}{.status.availableReplicas}{"\n"}'

oc apply -f "manifests/05-quota/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-05 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --wait=true --timeout=180s
oc apply -f manifests/05-quota/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=05 --wait=true --timeout=180s
```

Fixed YAML restores one replica and the no-surge strategy. Historical warning events may remain; current desired/available state and quota usage determine success. Raising quota is an administrative capacity decision, while deleting the existing Pod creates downtime and does not satisfy a two-replica request.

## 06 — Service selector mismatch

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. Application Pods remain Ready, but `app-06` selects no matching backends. EndpointSlices may exist with no usable application endpoints.

```bash
oc -n "09-ts-lab" get pods -l training.redhat.com/case=06 --show-labels
oc -n "09-ts-lab" get svc app-06 -o jsonpath='{.spec.selector}{"\n"}'
oc -n "09-ts-lab" get endpointslice -l kubernetes.io/service-name=app-06 -o yaml
oc -n "09-ts-lab" exec deploy/diagnostic-client-06 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-06:8080/", timeout=3)' || true

oc apply -f "manifests/06-service-selector/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-06 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --wait=true --timeout=180s
oc apply -f manifests/06-service-selector/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=06 --wait=true --timeout=180s
```

Fixed YAML restores selector `app=troubleshooting-app-06`. Restarting healthy Pods, changing DNS, or opening NetworkPolicy does not repair selection.

## 07 — NetworkPolicy denial

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. DNS and ready endpoints remain correct, while a fresh bounded connection from `diagnostic-client-07` fails after `lab-deny-app-07` selects the server. Egress is untouched, avoiding a second DNS fault.

```bash
oc -n "09-ts-lab" get pods,svc,endpointslice,networkpolicy -l training.redhat.com/case=07 --show-labels
oc -n "09-ts-lab" get networkpolicy lab-deny-app-07 -o yaml
oc -n "09-ts-lab" exec deploy/diagnostic-client-07 -- python3.12 -c 'import socket; print(socket.gethostbyname("app-07"))'
oc -n "09-ts-lab" exec deploy/diagnostic-client-07 -- python3.12 -c 'import urllib.request; urllib.request.urlopen("http://app-07:8080/", timeout=3)' || true

oc apply -f "manifests/07-network-policy/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-07 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --wait=true --timeout=180s
oc apply -f manifests/07-network-policy/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=07 --wait=true --timeout=180s
```

Fixed YAML keeps `lab-deny-app-07` and adds `lab-allow-client-07`, allowing TCP/8080 only from Pods labeled `role=diagnostic-client`. The verifier also launches or uses an otherwise equivalent unlabeled client and requires denial. Policies are additive: removing the deny allows everyone, while a broad allow invalidates the negative control. Reset explicitly removes both policies.

## 08 — Pending PVC and replacement recovery

Apply setup only after an instructor validates default dynamic provisioning. `invalid-data-08` requests an explicitly nonexistent class and remains Pending; `storage-consumer-08` cannot mount it. A real `WaitForFirstConsumer` class can legitimately wait until scheduling, so compare the exact class and events.

```bash
oc -n "09-ts-lab" get pvc,pods -l training.redhat.com/case=08
oc -n "09-ts-lab" describe pvc invalid-data-08
oc -n "09-ts-lab" describe pod -l app=storage-consumer-08
oc get storageclass

oc apply -f "manifests/08-storage/fixed.yaml"
oc -n "09-ts-lab" delete pvc invalid-data-08 --ignore-not-found
oc -n 09-ts-lab rollout status deployment/storage-consumer-08 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --wait=true --timeout=180s
oc apply -f manifests/08-storage/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08 --wait=true --timeout=180s
```

Fixed YAML creates `recovery-data-08` using the default class and updates the no-surge consumer to mount it. The verifier requires Bound, Ready, and a mounted write/read check. `storageClassName` is immutable: do not patch `invalid-data-08`. No data is recovered from the unbound claim. Reset scales/stops the consumer before deleting disposable claims and recreates baseline `lab-data-08`. Cleanup can delete lab data; for a `Retain` reclaim policy, instructors must dispose of the released lab PV according to site procedure without touching shared PVs.

## 08b — Missing ConfigMap key

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. Pod events commonly show `CreateContainerConfigError`; the Deployment references a missing required key while `app-settings-08b` remains present. The application process never starts, so previous logs may not exist.

```bash
oc -n "09-ts-lab" get pods,configmap -l training.redhat.com/case=08b
oc -n "09-ts-lab" describe pod -l training.redhat.com/case=08b
oc -n "09-ts-lab" get deploy app-08b -o jsonpath='{.spec.template.spec.containers[0].env}{"\n"}'
oc -n "09-ts-lab" get configmap app-settings-08b -o yaml

oc apply -f "manifests/08b-configuration/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-08b --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --wait=true --timeout=180s
oc apply -f manifests/08b-configuration/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=08b --wait=true --timeout=180s
```

Fixed YAML restores the existing key reference. Restarting without fixing the Pod template repeats the error; crash-loop tuning is irrelevant because no process ran. ConfigMap-derived environment values are captured when a container starts and do not refresh inside an already running container.

## 09 — Capstone

Apply that section’s `setup.yaml`, confirm the healthy baseline, then apply `broken.yaml` to reproduce the fault. Three independent faults are present: the Deployment has a nonexistent image tag, Service `app-09` has a mismatched selector, and `lab-deny-app-09` lacks the narrow approved-client allowance. Diagnose in that order because a non-running Pod masks backend and network tests.

```bash
oc -n "09-ts-lab" get deploy,rs,pods,svc,endpointslice,networkpolicy -l training.redhat.com/case=09 --show-labels
oc -n "09-ts-lab" describe pod -l training.redhat.com/case=09
oc -n "09-ts-lab" get events --sort-by=.metadata.creationTimestamp
oc -n "09-ts-lab" get deploy app-09 -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
oc -n "09-ts-lab" get svc app-09 -o jsonpath='{.spec.selector}{"\n"}'
oc -n "09-ts-lab" get networkpolicy -l training.redhat.com/case=09 -o yaml

oc apply -f "manifests/09-capstone/fixed.yaml"
oc -n 09-ts-lab rollout status deployment/app-09 --timeout=120s
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --wait=true --timeout=180s
oc apply -f manifests/09-capstone/setup.yaml
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=09 --wait=true --timeout=180s
```

Fixed YAML restores the approved image, selector `app=troubleshooting-app-09`, and the deny-plus-scoped-allow state. Verification requires Ready replicas, ready selected endpoints, approved-client success, and unapproved-client denial. Applying only one correction cannot prove full recovery; removing all policies fails the negative control.
