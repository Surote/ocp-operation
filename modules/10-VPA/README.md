# Vertical Pod Autoscaler (VPA)

This module covers the **Vertical Pod Autoscaler (VPA)** — a mechanism that automatically recommends or adjusts CPU and memory requests/limits for containers based on actual usage.

> **Prerequisite:** The VPA operator must be installed. See [prep/manifests/vertical-pod-autoscaler.yaml](../../prep/manifests/vertical-pod-autoscaler.yaml) for the operator installation manifest.

---

### How VPA Works

VPA monitors historical and real-time resource usage of pods, then:
1. **Recommends** optimal CPU/memory requests and limits
2. **Optionally applies** those recommendations by evicting and recreating pods with updated resource specs

---

### Update Modes

| Mode | Description |
|---|---|
| `Off` | VPA only provides recommendations — does not modify pods - แนะนำอย่างเดียวไม่แก้ไขค่าของ application pod |
| `Initial` | VPA assigns resources at pod creation only — no updates to running pods - ใส่ค่าตั้งต้นให้เท่านั้น |
| `Recreate` | VPA evicts and recreates pods when recommendations change significantly - rolling pod เพื่ออัพเดทค่าที่ VPA แนะนำ|
| `InPlaceOrRecreate` | VPA attempts to apply updates in-place without restarting the pod. If unable to update in-place, VPA deletes and recreates the pod - พยายามปรับค่า resource โดยไม่ต้อง restart pod ก่อน ถ้าทำไม่ได้จะ rolling pod |

---

### Key Parameters

#### `spec.targetRef`

| Field | Description |
|---|---|
| `apiVersion` | API version of the target workload (e.g. `apps/v1`) |
| `kind` | Workload kind: `Deployment`, `StatefulSet`, `DaemonSet`, etc. |
| `name` | Name of the target workload |

#### `spec.resourcePolicy.containerPolicies[]`

| Field | Description |
|---|---|
| `containerName` | Container name or `'*'` for all containers |
| `controlledResources` | Which resources VPA manages: `cpu`, `memory`, or both |
| `controlledValues` | `RequestsOnly` (Burstable) or `RequestsAndLimits` (Guaranteed) |
| `minAllowed` | Minimum resource values VPA will recommend |
| `maxAllowed` | Maximum resource values VPA will recommend |
| `mode` | `Auto` (default) or `Off` to exclude a specific container |

#### `controlledValues` Summary

| Value | QoS Class | Description |
|---|---|---|
| `RequestsOnly` | Burstable | VPA ปรับเฉพาะ requests — limits คงเดิม |
| `RequestsAndLimits` | Guaranteed | VPA ปรับทั้ง requests และ limits ให้เท่ากัน — รักษา QoS Guaranteed |

---

### Deploy

#### Burstable QoS (`controlledValues: RequestsOnly`)

```bash
oc apply -f modules/10-VPA/manifests/sample-application.yaml
oc apply -f modules/10-VPA/manifests/10-module-deployment-vpa.yaml
```

#### Guaranteed QoS (`controlledValues: RequestsAndLimits`)

```bash
oc apply -f modules/10-VPA/manifests/sample-application-guaranteed.yaml
oc apply -f modules/10-VPA/manifests/10-module-deployment-vpa-guaranteed.yaml
```

### Check Recommendations

```bash
oc get vpa -n 10-module
oc get vpa vpa-10-module -n 10-module -o yaml
```
![Recommend pod](../../img/module-10/get-vpa.png)

VPA recommendations appear under `status.recommendation.containerRecommendations`:

| Field | Description |
|---|---|
| `lowerBound` | Minimum recommended resources |
| `target` | Recommended resource requests |
| `upperBound` | Maximum recommended resources |
| `uncappedTarget` | Recommendation without `minAllowed`/`maxAllowed` constraints |

```bash
oc describe vpa vpa-10-module -n 10-module
```

---

### In-Place Pod Resize and `resizePolicy`

Starting from OpenShift 4.17+ (Kubernetes 1.27+), pods can have their CPU and memory updated **without restarting** — this is called **In-Place Pod Resize**.

When VPA is set to `updateMode: InPlaceOrRecreate`, it attempts to resize containers in-place first. If in-place resize is not possible, it falls back to evicting and recreating the pod.

#### How It Works

The `resizePolicy` field in the container spec controls whether a resource change requires a container restart:

```yaml
containers:
  - name: timecheck-fastapi
    image: quay.io/rh_ee_swongpai/fast-localtime-check:lw-217d4d6d9b0e7886ae03b053db2c4f4cd8b104ec
    resources:
      requests:
        cpu: 5m
        memory: 64Mi
    resizePolicy:
      - resourceName: cpu
        restartPolicy: NotRequired
      - resourceName: memory
        restartPolicy: NotRequired
```

#### `resizePolicy` Parameters

| Field | Description |
|---|---|
| `resourceName` | Resource to configure: `cpu` or `memory` |
| `restartPolicy` | `NotRequired` — resize in-place without restart; `RestartContainer` — restart the container to apply new resources |

#### Behavior Matrix

| `restartPolicy` | CPU change | Memory change |
|---|---|---|
| `NotRequired` | Applied immediately, no restart | Applied immediately, no restart |
| `RestartContainer` | Container restarts to apply | Container restarts to apply |
| Not specified | Defaults to `NotRequired` for CPU, `NotRequired` for memory |

#### Verify In-Place Resize

ตรวจสอบว่า pod ได้รับ resource ใหม่โดยไม่ถูก restart:

> **⚠️ QoS Class Constraint:** In-place resize จะทำได้เฉพาะเมื่อ resource ใหม่ที่ VPA แนะนำ **ไม่ทำให้ QoS class เปลี่ยน** เท่านั้น เช่น ถ้า pod เดิมเป็น `Burstable` แล้ว resource ใหม่ทำให้กลายเป็น `Guaranteed` (requests = limits) จะไม่สามารถ resize in-place ได้ — VPA จะ fallback ไปใช้การ recreate pod แทน ดังนั้นการใช้ `controlledValues: RequestsOnly` ทำให้ QoS class ให้คงเดิม (Burstable)

![Recommend pod](../../img/module-10/inplace-vpa-not-restart.png)

---

### VPA vs HPA

| | VPA | HPA |
|---|---|---|
| Scaling direction | **Vertical** — adjusts CPU/memory per pod | **Horizontal** — adjusts number of pod replicas |
| When to use | Workloads that can't scale horizontally, or to right-size resource requests | Workloads with variable load that benefit from more replicas |
| Pod disruption | Evicts pods to apply new resources (in `Auto` mode) | No pod disruption — adds/removes replicas |
| Can be used together? | Yes, but do not let both control the same resource (e.g. VPA controls memory, HPA controls CPU) | Same |

> **Note:** When using VPA with HPA, ensure they do not manage the same resource metric to avoid conflicts.
