apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-tls-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: simple-tls-server
  template:
    metadata:
      labels:
        app: simple-tls-server
    spec:
      containers:
      - name: simple-tls-server
        image: srinmantest.azurecr.io/tls-server:v4
        ports:
        - containerPort: 443
        volumeMounts:
        - name: tls-secret
          mountPath: "/etc/tls"
          readOnly: true
      volumes:
      - name: tls-secret
        secret:
          secretName: tls-secret
---
apiVersion: v1
kind: Service
metadata:
  name: pythonsvc
spec:
  selector:
    app: simple-tls-server
  ports:
    - protocol: TCP
      port: 443
      targetPort: 443
  type: ClusterIP