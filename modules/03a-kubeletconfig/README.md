# KubeletConfig

This module demonstrates how to customise kubelet settings per MachineConfigPool using the **KubeletConfig** custom resource in OpenShift.

---

## Overview

A **KubeletConfig** resource lets you override default kubelet parameters (e.g. `maxPods`, system-reserved resources) for a specific set of nodes selected through a MachineConfigPool label. In this module we apply two KubeletConfig objects — one for each infra pool created in module 03:

- `infra-general-kubeletconfig` — targets `infra-general` nodes, sets `maxPods: 280`
- `infra-observe-kubeletconfig` — targets `infra-observe` nodes, sets `maxPods: 290`

Both configs enable `autoSizingReserved: true`, which lets the kubelet automatically calculate system-reserved CPU and memory based on the node's capacity.

> **Note:** The default `maxPods` is **250**. The hard upper limit depends on the host prefix — a `/23` CIDR allows up to **510** pods per node. The values here are intentionally above the default for testing purposes.

---

## Prerequisites

- Module 03 (Node MachineConfig) must be completed — the `infra-general` and `infra-observe` MachineConfigPools must already exist.

---

## Check existing configuration

ตรวจสอบค่าของ cpu,memory,pods ที่สามารถใช้งานได้ ของ `infra-general` และ `infra-observe`

![Existing allocation](../../img/module-03a/existing-allocation.png)

โดยที่เครื่อง `..-3` คือ `infra-general` และเครื่อง `..-6` คือ `infra-observe` ที่ถูกกำหนดมาจาก 02-placement ทั้งคู่มี pods: 250 ซึ่งเป็นค่าตั้งต้น

## Step 1 — Apply the KubeletConfig Manifests

```bash
oc apply -f manifests/infra-general.yaml
oc apply -f manifests/infra-observe.yaml
```

---

## Step 2 — Verify the Rollout

Applying a KubeletConfig triggers a rolling update of the targeted MachineConfigPool. Monitor progress with:

![Applied kubeletconfig](../../img/module-03a/applied-kubeletconfig.png)

`oc get node`
![Node rolling cli](../../img/module-03a/node-rolling-cli.png)

`Compute > Nodes`
![Node rolling UI](../../img/module-03a/node-rolling-ui.png)

```bash
oc get mcp -w
```

Wait until both `infra-general` and `infra-logmon` pools show `UPDATED: True`, `UPDATING: False`, and `DEGRADED: False`.

You can also inspect the rendered kubelet config on a specific node:

```bash
oc debug node/<node-name> -- chroot /host cat /etc/kubernetes/kubelet.conf | grep maxPods
```

---

## Manifests Reference

| File | KubeletConfig Name | Target MCP Label | maxPods | autoSizingReserved |
|---|---|---|---|---|
| `infra-general.yaml` | `infra-general-kubeletconfig` | `infra-general` | 280 | true |
| `infra-logmon.yaml` | `infra-logmon-kubeletconfig` | `infra-logmon` | 290 | true |
