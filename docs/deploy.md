# Deploying SalSmart for free

Everything below runs on free tiers. Some chains block downloads from outside Israel, so the server must be in an
Israeli region. The steps marked **(you)** need your accounts and cannot be automated.

## 1. A free VM in Israel (you)

1. Sign up at Oracle Cloud and choose **Israel Central (Jerusalem)** as the home region. Sign-up asks for a card to
   verify identity; Always Free resources are not charged. Set a budget alert of $1 right away (Billing, Budgets).
2. Create a VM: shape `VM.Standard.A1.Flex` (Ampere, Always Free), 2 OCPU and 12 GB RAM, Ubuntu 24.04.
   If Jerusalem has no free Ampere capacity, use Azure Israel Central instead (paid after the free credit).
3. Open ports 22, 80 and 443 in the VM's security list.

## 2. Kubernetes on the VM

```bash
ssh ubuntu@<vm-ip>
curl -sfL https://get.k3s.io | sh -
sudo cat /etc/rancher/k3s/k3s.yaml   # copy to ~/.kube/config on your Mac, replacing 127.0.0.1 with the VM IP
```

## 3. Images

Every push to `main` builds both images and publishes them to GitHub Container Registry
(`.github/workflows/images.yml`). If the repository is private, make the two packages public in GitHub
(Packages, Package settings) or add an image pull secret.

## 4. Email and Google sign-in (you)

- **Email:** a free Brevo account (300 emails a day). Its SMTP login and key go into `secrets.env`.
- **Google sign-in:** in Google Cloud Console create an OAuth client of type "Web application" with your site as an
  authorized JavaScript origin. Put the client ID in the repository variable `GOOGLE_CLIENT_ID` (Settings, Variables)
  for the frontend build, and add `GOOGLE_CLIENT_ID` to the API environment.

## 5. Deploy

```bash
cp k8s/overlays/production/secrets.env.example k8s/overlays/production/secrets.env   # fill in real values
# set your host in k8s/overlays/production/ingress.yaml, e.g. 1-2-3-4.sslip.io
kubectl apply -k k8s/overlays/production
kubectl -n salsmart get pods
kubectl -n salsmart create job --from=cronjob/ingest-rami-levy first-run   # first ingestion without waiting for 05:30
```

The CronJobs then run every morning (Israel time). Grafana is inside the cluster:
`kubectl -n salsmart port-forward service/grafana 3000:3000`.
