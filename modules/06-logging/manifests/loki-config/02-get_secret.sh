OB_NAME="obc-openshift-logging-loki";
OBC_NAME="loki";
LOKI_SEC="loki-sec"
BUCKET_ACCESS_ID="$(oc get secret -n openshift-logging $OBC_NAME -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)";
BUCKET_ACCESS_KEY="$(oc get secret -n openshift-logging $OBC_NAME -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)";
BUCKET_NAME=$(oc get ob $OB_NAME -n openshift-logging -o jsonpath='{.spec.endpoint.bucketName}');
BUCKET_ENDPOINT=$(oc get ob $OB_NAME -n openshift-logging -o jsonpath='{.spec.endpoint.bucketHost}');
oc create secret generic $LOKI_SEC --from-literal=bucketnames="$BUCKET_NAME" --from-literal=endpoint="https://$BUCKET_ENDPOINT:443" --from-literal=access_key_id="$BUCKET_ACCESS_ID" --from-literal=access_key_secret="$BUCKET_ACCESS_KEY" -n openshift-logging