# OCP Operation

A collection of modules for OpenShift Container Platform day-2 operations — covering cluster health, node placement, monitoring, logging, GitOps, ingress, and resource management.

> **Disclaimer:** This repository is for **learning and demonstration purposes only**. All values and parameters (e.g. resource quotas, storage sizes, retention periods, replica counts, scan schedules) are examples and are **not intended for production use**. Review and adjust them according to your environment and organizational requirements before applying to a production cluster.

---

### Modules

| Module | Topic | Description |
|---|---|---|
| [01 - Cluster Health](modules/01-cluster-health/) | Cluster Health | Health check commands, node status, cluster operators, and diagnostics |
| [02 - Placement](modules/02-placement/) | Placement | Node labeling, taints/tolerations, node selectors, and pod placement |
| [03 - Node MachineConfig](modules/03-node-machineconfig/) | Node MachineConfig | MachineConfigPool (MCP) management and machine-level node configuration |
| [03a - KubeletConfig](modules/03a-kubeletconfig/) | KubeletConfig | Kubelet configuration for custom MachineConfigPools (maxPods, autoSizingReserved) |
| [04 - GitOps Deploy Operators](modules/04-gitops-deploy-operators/) | GitOps / Operators | Deploying operators (Compliance Operator) via Argo CD with auto-sync |
| [05 - Monitoring](modules/05-monitoring/) | Monitoring | Monitoring stack configuration, Prometheus retention/storage, and AlertRelabelConfig |
| [06 - Logging](modules/06-logging/) | Logging | OpenShift logging with LokiStack and ODF MCG (NooBaa) for S3 storage |
| [07 - IngressController](modules/07-ingresscontroller/) | Ingress | IngressController sharding with NodePortService and custom domain routing |
| [08 - Resources](modules/08-resources/) | Resources | ResourceQuota and LimitRange for namespace resource control |
