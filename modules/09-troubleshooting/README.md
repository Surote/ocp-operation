# OpenShift Day-2 Troubleshooting Lab

This six-hour, symptom-first lab teaches OpenShift administrators to diagnose image, process, readiness, scheduling, quota, Service, NetworkPolicy, storage, and configuration failures. A capstone combines three independent faults. Every case lives in the single `09-ts-lab` namespace and all cases can be applied at once. Faults are namespace-scoped, apart from the `lab-case-05` PriorityClass that scopes the exercise 05 quota; cluster triage is read-only.

The package contains only concrete YAML and Markdown. Each `manifests/<case>/setup.yaml` creates the shared `09-ts-lab` namespace if it is absent, plus that case's complete healthy state; `broken.yaml` injects the fault; `fixed.yaml` applies the repair. Those two hold only the objects that actually change, so each one names the fault and its repair plainly and must be applied on top of `setup.yaml`, never on their own. Do not apply the entire `manifests/` tree because lifecycle files conflict.

Every object a case owns is named with the case suffix (`app-01`, `diagnostic-client-01`) and labelled `training.redhat.com/case=01`, so cases never collide and each one is selected, reset, and removed by that label.

Requirements are an OpenShift 4.x cluster, `oc`, permissions listed in [instructor-guide.md](instructor-guide.md), and access to `registry.access.redhat.com/ubi9/python-312:latest` (diagnostic and unapproved clients) and `quay.io/rh_ee_swongpai/fast-localtime-check` (the app container). The app image is baked-in (no ConfigMap-mounted server.py); its command is overridden to run `uvicorn` on port 8080, and its readiness probe checks path `/`. All ten cases were run end to end on an OpenShift 4.x cluster on 2026-09-07: every fault reproduced and every repair recovered. Exercise 08 requires a working default dynamic StorageClass; use 08b otherwise.

```bash
oc config current-context
oc whoami
oc apply -f manifests/01-image-pull/setup.yaml
oc -n 09-ts-lab rollout status deployment/app-01 --timeout=120s
oc apply -f manifests/01-image-pull/broken.yaml
```

Investigate with [student-guide.md](student-guide.md), then use [hints.md](hints.md) progressively. [solutions.md](solutions.md) contains complete repairs and explanations. [diagnostics/cluster-triage.md](diagnostics/cluster-triage.md) covers platform triage, and [diagnostics/evidence-template.md](diagnostics/evidence-template.md) is the incident record.

The literal namespace is `09-ts-lab`, shared by every exercise. One learner owns it at a time: the case label separates the exercises, not the learners. For multiple learners, the instructor must distribute separate copies with every namespace occurrence changed consistently in YAML and guides before use.

Because the namespace is shared, `oc get events` returns every case at once. Read events against the object names in your own case.

Reset or clean up one case by its label, never by deleting the namespace, which would destroy every other case. Inspect what the label selects before deleting it:

```bash
oc -n 09-ts-lab get deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --show-labels
oc -n 09-ts-lab delete deployment,service,configmap,networkpolicy,resourcequota,pvc -l training.redhat.com/case=01 --wait=true --timeout=180s
```

Deletion is irreversible. Exercise 05 also creates the cluster-scoped `lab-case-05` PriorityClass; remove it with `oc delete priorityclass lab-case-05` once no learner needs exercise 05. Exercise 08 claims and data are disposable; never use an existing claim or shared data.
