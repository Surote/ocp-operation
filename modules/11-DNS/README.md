# Module 11 - DNS

## HostAliases Testing

`hostAliases` ใช้สำหรับเพิ่ม entry ลงใน `/etc/hosts` ของ Pod โดยตรง โดยไม่ต้องแก้ไข DNS server  
เหมาะสำหรับ:
- ทดสอบ internal hostname resolution
- override DNS ชั่วคราวในระดับ Pod
- mapping custom hostname ไปยัง IP ที่ต้องการ

### Deploy

```bash
oc apply -f modules/11-DNS/manifests/hostalias-test.yaml
```

### Verify

1. ตรวจสอบ Pod status:

```bash
oc get pods -n 11-dns-module
```

2. ดู `/etc/hosts` ภายใน Pod:

```bash
oc exec -n 11-dns-module deploy/hostalias-test -- cat /etc/hosts
```

ผลลัพธ์ควรมี entry ที่เพิ่มจาก `hostAliases`:

```
# Entries added by HostAliases.
10.0.0.100  myapp.internal.example.com  myapp-alias.internal.example.com
10.0.0.200  db.internal.example.com
10.0.0.300  cache.internal.example.com
```

3. ทดสอบ resolution:

```bash
oc exec -n 11-dns-module deploy/hostalias-test -- getent hosts myapp.internal.example.com
oc exec -n 11-dns-module deploy/hostalias-test -- getent hosts db.internal.example.com
```

4. ดู startup logs:

```bash
oc logs -n 11-dns-module deploy/hostalias-test
```

### Cleanup

```bash
oc delete -f modules/11-DNS/manifests/hostalias-test.yaml
```

### Key Points

| Field | Description |
|-------|------------|
| `spec.hostAliases[].ip` | IP address ที่ต้องการ map |
| `spec.hostAliases[].hostnames` | list ของ hostname ที่จะ resolve ไปยัง IP นั้น |

> **Note:** `hostAliases` จะถูกเพิ่มเข้าไปใน `/etc/hosts` ของ Pod เท่านั้น ไม่กระทบ DNS ของ cluster หรือ Pod อื่น
