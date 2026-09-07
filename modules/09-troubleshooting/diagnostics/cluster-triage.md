# Read-only cluster triage

Use this before fault injection to decide whether a symptom is platform-wide or confined to the learner namespace. These commands do not authorize changes to cluster-scoped resources. If RBAC denies a command, record the denial and use a timestamped, sanitized instructor capture.

```bash
date -u
oc whoami
oc version
oc get clusterversion
oc get clusteroperators
oc get nodes
oc get machineconfigpools
oc get events -A --sort-by=.metadata.creationTimestamp
```

Inspect conditions rather than relying only on table summaries:

```bash
oc get clusterversion version -o yaml
oc get clusteroperators -o yaml
oc get nodes -o custom-columns='NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status,REASON:.status.conditions[?(@.type=="Ready")].reason'
oc get machineconfigpools -o yaml
```

Then narrow to your exercise. Every case shares the `09-ts-lab` namespace, so select yours by its case label:

```bash
export CASE=01
export NS=09-ts-lab
oc get namespace "$NS" --show-labels
oc -n "$NS" get deploy,rs,pods,svc,endpointslice,pvc,networkpolicy -l training.redhat.com/case="$CASE"
oc -n "$NS" get events --sort-by=.metadata.creationTimestamp
```

Events carry no lab labels, so the last command returns every case in the namespace. Match them to your own case by object name.

Record any pre-existing `Degraded`, `Progressing`, unavailable, or NotReady condition with its timestamp and message. Compare its affected component and time window with the lab symptom. Escalate to the instructor when registry, DNS, network, storage, scheduling, or control-plane health could explain the same symptom. Do not “fix” nodes, Operators, MachineConfigPools, SCCs, cluster RBAC, ingress, DNS, or StorageClasses during this lab.

Events are transient and human-readable messages can vary by release. Use them with object status, conditions, controller state, and a bounded functional request. Do not use a historical warning alone as proof that the current state is unhealthy.
