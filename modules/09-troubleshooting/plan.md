# OpenShift Day-2 Operations Troubleshooting Lab — Implemented Design

## 1. Agreed scope

Design a six-hour, hands-on lab for OpenShift administrators who already understand Pods, Deployments, Services, and basic `oc` commands. Use a shared training cluster, with injected faults confined to dedicated learner namespaces. Node and cluster-operator investigations are read-only.

The learner receives symptoms first, progressive hints, and separate complete solutions. Eight exercises lead into a combined incident. Instructions are in English and use `oc` as the primary interface.

This module now includes the complete teaching material and directly applicable YAML for all exercises. Static validation is complete; cluster lifecycle validation has not been run. Nothing in this document claims that runtime behavior has been proven on a training cluster.

Target the installed OpenShift 4.x release. Record the exact server/client versions and verify required capabilities during preflight. Do not claim compatibility with every OpenShift 4.x release. No additional Operators are required.

## 2. Learning outcomes

By the end, learners should be able to:

- Establish cluster and namespace health before changing anything.
- Distinguish admission, scheduling, image retrieval, startup, readiness, service discovery, network-policy, and storage failures.
- Use events, current and previous container logs, object conditions, selectors, and EndpointSlices to test a hypothesis.
- Apply a narrowly scoped repair and prove that the original symptom is resolved.
- Record evidence, explain the root cause, and reset or clean up lab resources safely.

## 3. Six-hour agenda

Breaks are additional to the six hours of hands-on time.

1. **00:00–00:30 — Preflight and healthy baseline:** confirm access and capabilities, identify lab resources, and demonstrate a working request.
2. **00:30–01:00 — Cluster health triage:** inspect nodes, cluster operators, cluster version, MachineConfigPools, and relevant events; decide whether a symptom is platform-wide or workload-specific.
3. **01:00–01:30 — Exercise 01:** image pull failure.
4. **01:30–02:00 — Exercise 02:** application crash loop.
5. **02:00–02:30 — Exercise 03:** readiness probe failure.
6. **02:30–03:00 — Exercise 04:** unschedulable Pod.
7. **03:00–03:30 — Exercise 05:** quota admission rejection.
8. **03:30–04:00 — Exercise 06:** Service selector mismatch.
9. **04:00–04:30 — Exercise 07:** NetworkPolicy denial.
10. **04:30–05:00 — Exercise 08:** pending PVC, or the configuration alternative if storage provisioning is unavailable.
11. **05:00–05:45 — Capstone:** recover an application with several independent faults.
12. **05:45–06:00 — Debrief and cleanup:** submit evidence, explain repairs, and verify resource removal.

Each 30-minute exercise reserves roughly five minutes for the symptom and evidence, fifteen for investigation and repair, and ten for verification, explanation, and reset.

## 4. Environment and preflight contract

### Access and isolation

- Use the single dedicated namespace `09-ts-lab` for every case. Every `setup.yaml` creates that Namespace with lab ownership labels, and names and labels each case's objects with its case suffix so the cases coexist.
- An instructor provisions namespaces and namespace-scoped access when learners cannot create projects themselves. Do not grant cluster-admin merely to complete this lab.
- Verify permissions for the actual namespaced resources used, including Deployments, Pods, Pod logs/exec, Services, ConfigMaps, ResourceQuotas, NetworkPolicies, and PVCs. Check Route access when the ingress demonstration is enabled.
- Check cluster-read permissions separately. Provide sanitized instructor-captured diagnostic output when learners cannot inspect cluster-scoped objects; clearly label captured output and its timestamp/version.
- Run one exercise at a time and provide an instructor capacity estimate from the final manifest requests and expected concurrent learners.
- Do not mutate shared nodes, SCCs, cluster RBAC, Operators, DNS, ingress controllers, MachineConfigPools, or StorageClasses. Do not inject faults into existing workloads.

### Required capabilities

- Record `oc version`, cluster network information when readable, and the baseline cluster health report. Existing cluster incidents must be resolved or distinguished from lab symptoms before starting.
- Verify `quay.io/rh_ee_swongpai/fast-localtime-check` under the cluster's normal restricted security policy and record the resolved digest before a taught run. The manifests override the baked-in command to run `uvicorn` on port 8080 with readiness path `/`; the application code is baked into the image, not ConfigMap-mounted.
- Verify `registry.access.redhat.com/ubi9/python-312:latest` in the diagnostic-client and unapproved-client roles; this image is distinct from the app image because diagnostic requests need a shell and Python's standard library, which the app image does not provide.
- Establish a healthy Deployment, ClusterIP Service, ready EndpointSlice backend, and successful request from a diagnostic Pod before fault injection.
- Verify that the network implementation enforces the intended NetworkPolicy behavior with a temporary lab-only test. Check for policies that would interfere with the scenario. An unenforced policy is a preflight failure for the hands-on network exercise.
- Discover and test the cluster's default StorageClass, with a consumer Pod if binding waits for a consumer. The healthy and recovery claims omit `storageClassName`; the broken claim explicitly names `lab-storage-class-does-not-exist`. If default dynamic provisioning is unavailable, use exercise `08b` for the scheduled slot.
- Use Service traffic for core checks. An optional Route may demonstrate external access when wildcard DNS and ingress are available; let OpenShift allocate the hostname instead of hardcoding a private domain.
- Require only `oc` on the administrator workstation. No renderer, shell script, package manager, Helm, or Kustomize step is part of the lab.

### Version and capability record

Record tested OpenShift and `oc` versions, test date, image digests, networking behavior, and the selected storage provisioner/binding mode alongside the instructor's run notes. Keep cluster addresses, credentials, and sensitive output out of committed artifacts.

## 5. Implemented package

Follow the repository's `README.md` and `manifests/` conventions, with separate learner and instructor material:

```text
09-troubleshooting/
  plan.md
  README.md
  student-guide.md
  hints.md
  solutions.md
  instructor-guide.md
  manifests/
    common/
      namespace.yaml
      application.yaml
      diagnostic-client.yaml
      route.yaml                      # optional ingress demonstration
    01-image-pull/{setup,broken,fixed}.yaml
    02-crash-loop/{setup,broken,fixed}.yaml
    03-readiness/{setup,broken,fixed}.yaml
    04-scheduling/{setup,broken,fixed}.yaml
    05-quota/{setup,broken,fixed}.yaml
    06-service-selector/{setup,broken,fixed}.yaml
    07-network-policy/{setup,broken,fixed}.yaml
    08-storage/{setup,broken,fixed}.yaml
    08b-configuration/{setup,broken,fixed}.yaml
    09-capstone/{setup,broken,fixed}.yaml
  diagnostics/
    cluster-triage.md
    evidence-template.md
    sample-output/                    # sanitized, explicitly labeled captures
```

The brace notation above represents three real files per exercise. The package contains 34 YAML files: 30 exercise lifecycle files and four common examples. It requires no new CRDs.

### Manifest and lifecycle rules

- Ship all manifests required to run and repair every exercise, including the storage alternative and capstone. Learners must not need to invent missing resources or build an application image.
- `setup.yaml` creates the dedicated Namespace and defines the complete healthy scenario. `broken.yaml` declares the affected resources with the intended fault. `fixed.yaml` declares the repaired resources.
- Common files are reference/bootstrap inputs. Keep scenario files self-contained and check that copied baseline definitions remain consistent.
- Keep setup, fault injection, and solution application as separate steps. Never recursively apply the entire `manifests/` directory because it contains conflicting lifecycle states.
- Every file contains concrete values and is usable with `oc apply -f <file>`. There are no placeholders or generation dependencies.
- Use explicit resource requests/limits and portable security settings: no privileged containers, fixed root UID requirement, host networking, host paths, or unnecessary capabilities.
- Wait for a healthy baseline before injecting a fault. Wait for observable broken-state evidence before declaring injection successful. Use bounded waits with diagnostic output on failure.
- Checks must validate conditions and request results, not exact human-readable event text or fixed sleep durations.
- Reset is manual and case-specific. Delete scenario-only objects absent from the baseline before reapplying `setup.yaml`; this is required for NetworkPolicy and storage cases.
- Cleanup uses the exact namespace stated in the exercise after confirming its three ownership labels. Never delete by a prefix or target a namespace that was not created by that setup file.
- Document any storage deletion, reclaim policy, and data consequences explicitly. Storage data in this lab is disposable; never use an existing claim or dataset.

## 6. Exercise specifications and solutions

### 01 — Image pull failure

- **Healthy setup:** one working application Deployment and Service using the verified image reference.
- **Broken YAML:** change the Deployment image to a deliberately nonexistent tag in the same reachable repository.
- **Symptoms:** replacement Pod cannot start; image events show retrieval failure, commonly progressing from `ErrImagePull` to `ImagePullBackOff`.
- **Investigation:** inspect Pod status and events, then compare the declared image with the approved baseline. Distinguish the intended missing tag from registry authentication or connectivity problems.
- **Solution:** apply `fixed.yaml` restoring the verified image reference and wait for the rollout.
- **Pass condition:** the desired replica is Ready, the Pod uses the intended image, and a Service request succeeds.
- **Reset:** restore the healthy image and clean up the failed rollout state through the Deployment lifecycle.

### 02 — Application crash loop

- **Healthy setup:** verified application with its normal startup command.
- **Broken YAML:** override startup with a tested command that prints a recognizable lab error and exits with code 1. Select an image supporting that command during implementation.
- **Symptoms:** repeated container termination and restart backoff. The container starts before failing.
- **Investigation:** inspect restart count, termination exit code/reason, current logs, and `oc logs --previous`. Explain why this differs from an image pull or configuration admission/startup failure.
- **Solution:** apply `fixed.yaml` restoring the application's normal startup command.
- **Pass condition:** successful rollout and HTTP response; the repaired Pod remains Ready with no restart-count increase during a documented observation period.
- **Reset:** restore the baseline command and wait for its rollout.

### 03 — Readiness probe failure

- **Healthy setup:** application with a verified working HTTP readiness path.
- **Broken YAML:** change only the readiness probe to a path confirmed to return an unsuccessful probe response. Keep liveness unchanged.
- **Symptoms:** application container runs but is not Ready; probe failures appear in events and ready Service backends are unavailable.
- **Investigation:** compare the probe path/port with actual application behavior. Inspect EndpointSlice endpoint readiness conditions, not just the presence of addresses.
- **Solution:** apply `fixed.yaml` restoring the healthy probe.
- **Pass condition:** Pod Ready, a ready Service backend, and a successful request through the Service.
- **Teaching point:** readiness failure alone does not restart the container. Do not describe it as a crash loop.
- **Reset:** restore the baseline probe and verify readiness.

### 04 — Unschedulable Pod

- **Healthy setup:** an application that schedules with the namespace's normal placement constraints.
- **Broken YAML:** add a lab-specific `nodeSelector` value that preflight confirmed matches no node.
- **Symptoms:** Pod remains Pending with `FailedScheduling` evidence.
- **Investigation:** inspect Pod events, selector requirements, and node labels if permissions permit. Contrast selector mismatch with insufficient resources or taints.
- **Solution:** apply `fixed.yaml` removing the injected selector while preserving any legitimate baseline constraints. Do not repair this by labeling a shared node.
- **Pass condition:** Pod is assigned a node, becomes Ready, and serves requests.
- **Reset:** restore the baseline Deployment placement configuration.

### 05 — ResourceQuota admission rejection

- **Healthy setup:** a dedicated namespace with a quota permitting one Pod and a one-replica Deployment. Do not create a diagnostic Pod in this namespace. Use a rollout strategy that avoids a surge Pod during this scenario.
- **Broken YAML:** request two replicas without changing the one-Pod quota.
- **Symptoms:** the Deployment exists, but the ReplicaSet cannot create its additional Pod. Expect `FailedCreate`/quota evidence; the rejected Pod may never exist.
- **Investigation:** inspect Deployment and ReplicaSet conditions/events, quota hard/used values, and actual Pod count. Explain why the scheduler cannot resolve an admission rejection.
- **Solution:** apply `fixed.yaml` restoring the intended one replica. Discuss quota adjustment as an alternative only when capacity and policy justify it.
- **Pass condition:** one desired/available replica, quota usage within bounds, and no outstanding replica deficit. Historical events may remain and are not by themselves a failure.
- **Reset:** restore the one-replica Deployment and its lab quota without depending on a surge rollout.

### 06 — Service selector mismatch

- **Healthy setup:** ready application Pods and a working Service.
- **Broken YAML:** change only the Service selector to a label value that matches no application Pod.
- **Symptoms:** Pods are healthy but Service traffic fails; no usable application backends are selected.
- **Investigation:** compare Service selectors and Pod labels, inspect EndpointSlices using `kubernetes.io/service-name`, and compare a direct Pod request with a Service request.
- **Solution:** apply `fixed.yaml` restoring the Service selector to the application labels.
- **Pass condition:** expected ready endpoints are selected and repeated Service requests succeed.
- **Reset:** restore the original selector without restarting otherwise healthy application Pods.

### 07 — NetworkPolicy denial

- **Healthy setup:** labeled server and diagnostic client Pods with successful client-to-Service traffic; confirm no other policy permits the intended denied traffic.
- **Broken YAML:** create an ingress-deny NetworkPolicy selecting only this exercise's server Pods. Leave egress untouched to avoid a second DNS fault.
- **Symptoms:** server Pods remain Ready and Service endpoints remain correct, but fresh client connections time out or fail.
- **Investigation:** prove DNS resolution and backend selection, inspect policy selectors, and compare server health with a bounded client request. Avoid localhost and host-network paths as the primary test.
- **Solution:** apply `fixed.yaml` retaining the deny baseline and adding a narrowly scoped allow policy for the labeled client and application TCP port.
- **Pass condition:** the authorized client succeeds; an otherwise equivalent unapproved client remains denied. Both tests use fresh connections and bounded timeouts.
- **Teaching point:** NetworkPolicies are additive; an existing allow policy can defeat the intended failure.
- **Reset:** explicitly remove both exercise policies before restoring the baseline. Reapplying a deny object does not remove an added allow policy.

### 08 — Pending PVC

- **Healthy setup:** prove that a small disposable PVC and consuming Pod work with the cluster's default StorageClass. Record the selected class, binding mode, and reclaim policy.
- **Broken YAML:** create a separate disposable claim with an explicitly nonexistent StorageClass, and point the workload at it. Verify there is no matching static PV or class that would accidentally satisfy it.
- **Symptoms:** the new claim stays Pending and its consumer cannot start with the volume available.
- **Investigation:** inspect PVC events, class name, available classes when readable, and the consumer Pod. Distinguish an invalid class from legitimate `WaitForFirstConsumer` waiting, provisioner failure, or capacity issues.
- **Solution:** apply `fixed.yaml` creating a new, correctly configured recovery claim and updating the consumer reference. Include a no-surge rollout for an RWO-backed single-instance workload. After recovery, remove only the exercise's unused invalid claim.
- **Pass condition:** the recovery claim is Bound, the consumer is Ready, and a write/read check succeeds on the mounted lab volume. Do not claim data was recovered from the invalid, unbound claim.
- **Reset:** stop the lab consumer before removing disposable exercise claims, then recreate the healthy baseline. Document retained-PV handling for the instructor; do not delete shared PVs or modify the default StorageClass.
- **Constraint:** do not promise an in-place `storageClassName` edit as the repair.

### 08b — Configuration startup failure: storage alternative

- **When used:** replaces exercise 08 in the timetable when suitable storage provisioning is unavailable. All YAML and solutions still ship for both exercises.
- **Healthy setup:** a ConfigMap with a required key and a Deployment referencing that key through `configMapKeyRef`.
- **Broken YAML:** change the Deployment's required key reference to a nonexistent key, leaving the ConfigMap intact.
- **Symptoms:** the container cannot start; expect configuration error evidence, commonly `CreateContainerConfigError`, rather than a process crash loop.
- **Investigation:** inspect Pod events and compare the key reference with the ConfigMap. Explain why previous application logs may not exist.
- **Solution:** apply `fixed.yaml` restoring the correct key reference and wait for the new Pod to start. Explain that environment values sourced from ConfigMaps are not automatically refreshed in an already running container.
- **Pass condition:** correct reference, Ready Pod, and working application response.
- **Reset:** restore the baseline ConfigMap and Deployment reference.

### 09 — Capstone: several faults, one unavailable application

- **Healthy setup:** independent application and labeled client in a dedicated capstone namespace. Confirm baseline traffic.
- **Broken YAML:** combine the nonexistent image tag, mismatched Service selector, and server ingress-deny policy from earlier exercises. Avoid requiring storage for the capstone.
- **Learner prompt:** an application became unavailable after a deployment/configuration change; restore the agreed client path and provide evidence for each root cause. Keep the explicit fault list in instructor material.
- **Solution sequence:** repair image startup, prove Pod health, repair Service selection, and add the scoped policy allowance. Explain that earlier faults can mask later ones.
- **Fixed YAML:** complete corrected Deployment and Service plus the deny/allow policy state. Include any remaining required baseline resources in setup.
- **Pass condition:** healthy replicas, correct ready backends, allowed-client success, unapproved-client denial, and an incident note explaining all three failures and repairs.
- **Reset:** remove capstone policy additions and restore its independently verified healthy setup.

## 7. Learner, hints, and solution content

Every exercise in `student-guide.md` includes its objective, timebox, prerequisites, namespace, setup/injection commands, initial symptom, investigation tasks, required evidence, success checks, and reset/cleanup entry points. Do not expose the root cause in the initial student prompt; keep manifest inspection available as a legitimate diagnostic technique.

`hints.md` provides three progressive hints per exercise: which system layer to inspect, which object/command to inspect, then which field or comparison matters.

For every exercise, `solutions.md` must provide:

1. Exact reproduction commands from a clean setup.
2. Expected observable symptoms, clearly distinguishing illustrative output from captured validation evidence.
3. Diagnostic commands and an explanation of what each proves or rules out.
4. Root cause and the smallest appropriate repair.
5. The exact `fixed.yaml` path and any ordered lifecycle steps, especially storage replacement and policy reset.
6. Verification commands with expected conditions and bounded failure behavior.
7. Reset and cleanup commands, common wrong turns, and reasons they do not solve the fault.

The incident evidence template records scope, timeline, symptoms, hypotheses, evidence, root cause, repair, verification, and one prevention action. Learners must explain the repair, not merely apply the answer file.

The instructor guide includes the schedule, access provisioning, capability checks, troubleshooting for failed lab setup, solution index, storage-alternative selection, concurrency/capacity guidance, and expected learner evidence. Refer to prior cluster-health, placement, and resource-management modules where useful.

## 8. Implementation status

The core scenarios, capability-dependent scenarios, storage alternative, capstone, teaching guides, diagnostics, and validation records are present in this module. Static checks parsed all 34 YAML files, verified setup namespace closure, checked the intended setup/broken/fixed deltas, compiled the embedded Python source, and checked workload security and resource fields. No live cluster operation was performed.

The remaining work is an authorized instructor run on the selected OpenShift cluster.

## 9. Acceptance criteria and validation

The finished lab is ready only when all of the following are evidenced:

- Every named file exists, every exercise has setup/broken/fixed YAML, and every learner instruction links to the correct artifact.
- All 34 YAML files parse successfully, contain concrete values, and pass server-side validation on the target release. Fault injection that depends on admission or runtime behavior must be tested at that layer, not judged solely by static review.
- For every supported exercise: setup reaches healthy state, injection produces the intended symptom, documented diagnosis finds the intended evidence, the solution passes its checks, reset restores baseline, and a second injection reproduces the fault.
- The quota case proves ReplicaSet admission rejection; the readiness case proves lack of ready backends; the crash case proves process termination; the configuration alternative proves startup blockage. The exercises must not collapse into unrelated image or permission failures.
- The network case proves both allowed and denied clients after repair. The storage case proves recovery with the selected binding mode and a real consumer. If storage is unavailable, exercise 08 is marked unvalidated for that environment and 08b passes instead.
- Each fixed exercise namespace remains isolated from the other exercise namespaces. If concurrent groups need duplicate copies, the instructor must provide independently renamed manifest copies and RBAC; this package itself uses one fixed namespace per case.
- Manual reset and cleanup commands verify the current context, exact namespace, and ownership labels before mutation. Repeated deletion uses `--ignore-not-found` only for exact lab objects.
- Cluster health remains at its preflight baseline; no shared configuration was changed. Sanitized evidence and exact tested versions are recorded.
- An instructor dry run confirms the six-hour pacing. The capstone can be completed using the supplied materials, and each solution contains sufficient evidence to explain why it works.

Do not report runtime validation until these checks have actually run on the selected cluster. Documentation review alone is not a passing hands-on test.

## 10. Technical references

These primary sources informed the fault mechanisms and diagnostic distinctions. During implementation, use Red Hat documentation matching the actual target release; the OpenShift 4.18 link below is a reference, not a selected release or compatibility claim.

- [Kubernetes container images](https://kubernetes.io/docs/concepts/containers/images/) — image references and pull behavior.
- [Debug running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/) — status, events, and container logs.
- [Liveness, readiness, and startup probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/) — probe behavior and readiness effects.
- [Assigning Pods to nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) — selector-based placement.
- [Resource quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/) — namespace quota enforcement at admission.
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) — selector and endpoint diagnosis.
- [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) and [OpenShift 4.18 NetworkPolicy](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/network_security/network-policy) — enforcement requirements, additive policy behavior, and traffic caveats.
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) and [Storage classes](https://kubernetes.io/docs/concepts/storage/storage-classes/) — claims, provisioning, binding, and reclamation.
- [Configure Pods to use ConfigMaps](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#restrictions) and [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) — required keys and update behavior.
