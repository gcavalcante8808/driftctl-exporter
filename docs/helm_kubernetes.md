#### Installing Using Kubernetes (and Helm)

The most basic example, provides `environment.DCTL_FROM` and `environment.RESULT_PATH` and the aws credentials (static credentials in this first example):

```bash
helm upgrade --install drifctl-exporter \
  driftctl_exporter \
  --set-string environment.DCTL_FROM="tfstate+s3://my-bucket/terraform.tfstate \
  --set-string environment.RESULT_PATH="s3://result-bucket/result.json" \
  --set-string secrets.AWS_REGION="us-east-1" \
  --set-string secrets.AWS_ACCESS_KEY_ID="<SOME_ACCESS_KEY_ID>" \
  --set-string secrets.AWS_SECRET_ACCESS_KEY="<SOME_SECRET_ACCESS_KEY>" \
  --set-file driftignore=.driftignore
```

If you use EKS, you can use a [IRSA/Workload Identity](https://docs.aws.amazon.com/eks/latest/userguide/specify-service-account-role.html) instead of static credentials by setting the expected serviceAccount annotation:

```bash
helm upgrade --install drifctl-exporter \
  driftctl_exporter  
  --set-string environment.DCTL_FROM="tfstate+s3://my-bucket/terraform.tfstate \
  --set-string environment.RESULT_PATH="s3://result-bucket/result.json" \
  --set-string serviceAccount.annotations[0] = eks.amazonaws.com/role-arn: arn:aws:iam::account-id:role/iam-role-name
```

And if you already have  a [".driftignore"](https://docs.driftctl.com/next/usage/cmd/gen-driftignore-usage/) file, you can use `driftignore` value with its content as well:

```bash
helm upgrade --install drifctl-exporter \
  driftctl_exporter  
  --set-string environment.DCTL_FROM="tfstate+s3://my-bucket/terraform.tfstate \
  --set-string environment.RESULT_PATH="s3://result-bucket/result.json" \
  --set-string serviceAccount.annotations[0] = eks.amazonaws.com/role-arn: arn:aws:iam::account-id:role/iam-role-name \
  --set-file driftignore=.driftignore
```