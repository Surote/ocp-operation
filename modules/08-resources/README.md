
# Resources

This module covers **ResourceQuota** and **LimitRange** — two mechanisms for controlling resource consumption within a namespace.

---

### ResourceQuota

A ResourceQuota sets hard caps on the total amount of resources a namespace can consume. Pods that would exceed the quota are rejected.

Create a quota:

```bash
oc apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: example-quota
  namespace: <namespace>
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
EOF
```

Parameters under `spec.hard`:

| Parameter | Description |
|---|---|
| `requests.cpu` | Maximum total CPU requests across all pods in the namespace |
| `requests.memory` | Maximum total memory requests across all pods |
| `limits.cpu` | Maximum total CPU limits across all pods |
| `limits.memory` | Maximum total memory limits across all pods |
| `pods` | Maximum number of pods allowed in the namespace |

Additional parameters you can set:

| Parameter | Description |
|---|---|
| `persistentvolumeclaims` | Maximum number of PVCs |
| `services` | Maximum number of services |
| `services.loadbalancers` | Maximum number of LoadBalancer services |
| `services.nodeports` | Maximum number of NodePort services |
| `secrets` | Maximum number of secrets |
| `configmaps` | Maximum number of configmaps |
| `replicationcontrollers` | Maximum number of replication controllers |
| `requests.storage` | Maximum total storage requested across all PVCs |

Check current usage against the quota:

```bash
oc describe quota example-quota -n <namespace>
```

```bash
oc get resourcequota -n <namespace>
```

---

### LimitRange

A LimitRange sets default resource requests/limits that are automatically applied to containers that don't specify their own. It can also enforce min/max boundaries per container.

Create a limit range:

```bash
oc apply -f - <<EOF
apiVersion: v1
kind: LimitRange
metadata:
  name: example-limits
  namespace: <namespace>
spec:
  limits:
  - type: Container
    default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    min:
      cpu: 50m
      memory: 64Mi
    max:
      cpu: "2"
      memory: 2Gi
EOF
```

Parameters under `spec.limits[]`:

| Parameter | Description |
|---|---|
| `type` | What the limits apply to: `Container`, `Pod`, or `PersistentVolumeClaim` |
| `default` | Default **limits** injected into containers that don't specify their own |
| `defaultRequest` | Default **requests** injected into containers that don't specify their own |
| `min` | Minimum allowed value — containers requesting below this are rejected |
| `max` | Maximum allowed value — containers requesting above this are rejected |
| `maxLimitRequestRatio` | Maximum ratio of limit/request (e.g. `"4"` means limits can be at most 4x the request) |

How defaults get applied:

| Container specifies | What happens |
|---|---|
| Nothing | Gets both `defaultRequest` and `default` (limit) injected |
| Only requests | Gets `default` (limit) injected, keeps its own requests |
| Only limits | Gets `defaultRequest` injected, keeps its own limits |
| Both | Nothing injected, but must be within `min`/`max` range |

Check the active limit range:

```bash
oc describe limitrange example-limits -n <namespace>
```

```bash
oc get limitrange -n <namespace>
```

---

### How They Work Together

| | ResourceQuota | LimitRange |
|---|---|---|
| Scope | Total resources for the entire namespace | Per-container defaults and boundaries |
| Enforcement | Rejects pods that would exceed the quota | Injects defaults, rejects containers outside min/max |
| Requires resource specs on pods? | Yes (pods without requests/limits are rejected when quota is set) | No (provides defaults automatically) |

A common pattern is to use both together: LimitRange ensures every container gets default requests/limits, and ResourceQuota caps the namespace total so no single team over-consumes cluster resources.