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
| `InPlaceOrRecreate` | In this mode, the VPA automatically applies the recommended CPU and memory resources throughout the pod lifetime. When any pod in the project is out of alignment with the VPA recommendations, the VPA attempts to apply updates in-place, without restarting the pod. If the VPA is not able to update the containers in-place, the VPA deletes the pod - rolling pod เพื่ออัพเดทค่าที่ VPA แนะนำ|

> **Tip:** Start with `Off` to observe recommendations before enabling `Auto` in production.

---

### VPA Resource

This module creates a VPA targeting the `timechecker-deployment` in namespace `02-module`:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-02-module
  namespace: 02-module
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: timechecker-deployment
  updatePolicy:
    updateMode: "Off"
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      controlledResources:
      - cpu
      - memory
      minAllowed:
        cpu: 10m
        memory: 25Mi
      maxAllowed:
        cpu: 1
        memory: 500Mi
```

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
| `minAllowed` | Minimum resource values VPA will recommend |
| `maxAllowed` | Maximum resource values VPA will recommend |
| `mode` | `Auto` (default) or `Off` to exclude a specific container |

---

### Deploy

```bash
oc apply -f modules/10-VPA/manifests/02-module-deployment-vpa.yaml
```

### Check Recommendations

```bash
oc get vpa timecheck-deployment-vpa -n 02-module -o yaml
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
oc get vpa -n 02-module
oc describe vpa vpa-02-module -n 02-module
```

เช็ก deployment ใน 02-placement จะสังเกตุว่าไม่มี resource กำหนดใน deployment
แต่

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

#### Deploy Sample Application with In-Place Resize

```bash
oc apply -f modules/10-VPA/manifests/sample-application.yaml
```

#### Deploy VPA with `InPlaceOrRecreate`

```bash
oc apply -f modules/10-VPA/manifests/10-module-deployment-vpa.yaml
```

The VPA in `10-module` uses `InPlaceOrRecreate` mode with `controlledValues: RequestsOnly` (Burstable QoS):

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: vpa-10-module
  namespace: 10-module
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: timecheck-deployment
  updatePolicy:
    updateMode: InPlaceOrRecreate
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      controlledValues: RequestsOnly
      controlledResources:
      - cpu
      - memory
      minAllowed:
        cpu: 10m
        memory: 25Mi
      maxAllowed:
        cpu: 1
        memory: 500Mi
```

#### Verify In-Place Resize

ตรวจสอบว่า pod ได้รับ resource ใหม่โดยไม่ถูก restart:

```bash
oc get pod -n 10-module -o yaml | grep -A 10 resizePolicy
oc get pod -n 10-module -o jsonpath='{.items[*].status.resize}'
```

ถ้า `status.resize` แสดง `InProgress` หรือว่างเปล่า แสดงว่า in-place resize สำเร็จ — pod ไม่ถูก restart

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
