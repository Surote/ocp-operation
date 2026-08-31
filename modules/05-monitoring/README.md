# Monitoring

This module covers the OpenShift monitoring stack configuration — moving components to infra nodes, setting retention/storage, and using AlertRelabelConfig to enrich alerts.

---

### Monitoring Stack Configuration

Apply the cluster monitoring ConfigMap to configure all monitoring components:

```bash
oc apply -f manifests/cm-openshift-monitoring.yaml
```

This ConfigMap (`cluster-monitoring-config` in `openshift-monitoring`) configures the following:

| Component | Node Selector | Storage | Other |
|---|---|---|---|
| `alertmanagerMain` | `infra` | `5Gi` (`standard-csi`) | — |
| `prometheusK8s` | `infra` | `200Gi` (`standard-csi`) | `retention: 15d` |
| `prometheusOperator` | `infra` | — | — |
| `monitoringPlugin` | `infra` | — | — |
| `metricsServer` | `infra` | — | — |
| `kubeStateMetrics` | `infra` | — | — |
| `telemeterClient` | `infra` | — | — |
| `openshiftStateMetrics` | `infra` | — | — |
| `thanosQuerier` | `infra` | — | — |

All components are pinned to infra nodes with a matching toleration for `node-role.kubernetes.io/infra`.

---

### Changing Prometheus Retention

Edit the `prometheusK8s.retention` field in the ConfigMap:

```bash
oc edit configmap cluster-monitoring-config -n openshift-monitoring
```

```yaml
prometheusK8s:
  retention: 30d
```

---

### Expanding Prometheus PVC

If the storage class supports volume expansion (CSI), resize by patching the PVC directly:

```bash
oc patch pvc prometheus-data-prometheus-k8s-0 -n openshift-monitoring --type merge -p '
spec:
  resources:
    requests:
      storage: 400Gi
'
```

Verify:

```bash
oc get pvc -n openshift-monitoring
```

---

### Alert Relabeling

`AlertRelabelConfig` lets you add, modify, or drop labels on platform alerts before they reach Alertmanager. This is useful for routing alerts to specific teams or receivers.

Apply the relabel config:

```bash
oc apply -f manifests/platform-alert-relabel-01.yaml
```

This example adds a `team: platform-infra` label to the `KubeNodeNotReady` alert:

```yaml
apiVersion: monitoring.openshift.io/v1
kind: AlertRelabelConfig
metadata:
  name: kube-node-notready-team
  namespace: openshift-monitoring
spec:
  configs:
    - sourceLabels: [alertname]
      regex: "KubeNodeNotReady"
      targetLabel: team
      replacement: platform-infra
      action: Replace
```

| Parameter | Description |
|---|---|
| `sourceLabels` | List of label names to match against |
| `regex` | Regex pattern to match on the concatenated source label values |
| `targetLabel` | The label to set on the alert |
| `replacement` | The value to set on the target label |
| `action` | `Replace`, `Keep`, `Drop`, `HashMod`, `LabelMap`, `LabelDrop`, `LabelKeep` |

Once applied, the `KubeNodeNotReady` alert will carry the `team = platform-infra` label, which can be used in Alertmanager to route notifications to the correct receiver.

![Alert relabel result](../../img/module-05/05-mail-relabel.png)