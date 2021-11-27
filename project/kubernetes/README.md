## Kubernetes Declarative Manifests 

Place the Kubernetes declarative manifests in this directory.


## Troubleshooting

When your pod in k3s gets the following [error](https://github.com/rancher/k3os/issues/702):
```sh
Error: failed to create containerd container: get apparmor_parser version: exec: "apparmor_parser": executable file not found in $PATH
```

Run the following command to install `apparmor-parser`on your vagrant machine
```sh
zypper install apparmor-parser
```

Restarting deployment
```sh
kubectl rollout restart deployment techtrends -n sandbox
```