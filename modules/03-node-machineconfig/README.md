# Node MachineConfig

This module demonstrates how to work with MachineConfigPool (MCP) to manage node roles and apply machine-level configuration in OpenShift.

---

## Overview

A **MachineConfigPool** groups nodes by label so that MachineConfig resources (NTP, file writes, kernel arguments, etc.) can target specific sets of nodes. In this example we create two custom pools for infra workloads:

- `infra-general` — general-purpose infra nodes (e.g. ingress, registry)
- `infra-logmon` — infra nodes dedicated to logging and monitoring

---

## Step 1 — Label the Nodes

Assign the appropriate role labels to worker nodes so each MCP can select them.

```bash
# infra-general node
oc label no/<node-name> node-role.kubernetes.io/infra=
oc label no/<node-name> node-role.kubernetes.io/infra-general=

# infra-logmon node
oc label no/<node-name> node-role.kubernetes.io/infra=
oc label no/<node-name> node-role.kubernetes.io/infra-logmon=
```

![Label nodes](../../img/module-03/label-node-infra.png)

Verify the roles appear on the nodes:

```bash
oc get no
```

![Label result](../../img/module-03/label-node-infra-result.png)

---

## Step 2 — Apply the MachineConfigPool Manifests

```bash
oc apply -f manifests/mcp-infra-general.yaml
oc apply -f manifests/mcp-infra-logmon.yaml
```

![Apply MCP](../../img/module-03/applied-mcp.png)

---

## Step 3 — Verify

Check that the new pools are created and all machines are updated:

```bash
oc get mcp
```

Pools are healthy when `UPDATED` is `True`, `UPDATING` is `False`, and `DEGRADED` is `False`.

![MCP result](../../img/module-03/applied-mcp-result.png)

---

## Manifests Reference

| File | MCP Name | Node Selector Label |
|---|---|---|
| `mcp-infra-general.yaml` | `infra-general` | `node-role.kubernetes.io/infra-general` |
| `mcp-infra-logmon.yaml` | `infra-logmon` | `node-role.kubernetes.io/infra-logmon` |

Both pools use `machineConfigSelector` matching roles `[worker, infra]`, meaning they inherit all MachineConfigs targeted at `worker` or `infra` roles.