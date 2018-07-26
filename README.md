# rpi-google-cloud-dns-dynamic

Adds a managed dns zone and A record containing your public ip addresses

## Prerequisites

Install gcloud sdk and login using gcloud init.

Create a service account with the dns.admin role and generate a credentials key:
```
NAME=rpi-google-cloud-dns-dynamic
gcloud iam service-accounts create $NAME --display-name "$NAME"
SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter=name:"$NAME" --format='value(email)')
GCLOUD_PROJECT=$(gcloud config get-value project)
gcloud projects add-iam-policy-binding $GCLOUD_PROJECT --member="serviceAccount:$SERVICE_ACCOUNT" --role="roles/dns.admin"
gcloud iam service-accounts keys create google-application-credentials.json --iam-account=$SERVICE_ACCOUNT
```

## Usage
```
docker run -it \
-e PROJECT_ID=kubernetes-rocks \
-e DNS_ZONE_NAME=kubernetes-rocks \
-e DNS_NAME=pi.kubernetes.rocks. \
-e GOOGLE_APPLICATION_CREDENTIALS=/google-application-credentials.json \
-v $(pwd)/google-application-credentials.json:/google-application-credentials.json \
jonaseck/rpi-google-cloud-dns-dynamic
```

### Kubernetes

Create a configmap containing project_id, dns_zone_name and dns_name. The zone will be created if needed.
```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: google-cloud-dns-dynamic
data:
  project_id: kubernetes-rocks
  dns_zone_name: kubernetes-rocks
  dns_name: pi.kubernetes.rocks.
EOF
kubectl create secret generic google-application-credentials --from-file=google-application-credentials.json
kubectl apply -f https://github.com/jonaseck2/rpi-google-cloud-dns-dynamic/blob/master/deployment.yaml
```
