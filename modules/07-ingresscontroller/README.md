# Ingress

Create `sharding.yaml`

Deploy `sample-application.yaml`

Deploy `byoip-cert-check-application.yaml`

get node's IP the pod reside router sharding reside.
```
oc get pod -n openshift-ingress -o wide | grep sharded | awk '{print $7}' | xargs oc get no -o wide | awk '{print $6}'
```

![7-00](../../img/module-07/7-00.png)

get the router's svc nodeport
```
oc get svc -n openshift-ingress router-nodeport-sharded -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}{"\n"}'
```

![7-01](../../img/module-07/7-01.png)

Add `timecheck.swongpai.tt.local` `node's IP` `nodeport` in the byoip web 
browse the `https://timecheck.swongpai.tt.local` 

![7-02](../../img/module-07/7-02.png)