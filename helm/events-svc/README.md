events-svc
---------

````
# harbor credentials command

$ kubectl --kubeconfig edge-clusters-core5g.kubeconfig create secret docker-registry harbor-secret \
  --docker-server=https://dockerhub.mobilesandbox.cloud:9443 \
  --docker-username=USERE \
  --docker-password="PASSWORD" \
  --namespace listener-events
````