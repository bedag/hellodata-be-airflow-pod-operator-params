# HelloDATA BE Pod Operator Params (OpenSource) <!-- omit from toc -->
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Prod Deployment](#prod-deployment)
- [Install Package](#install-package)
- [Get Tokens](#get-tokens)
  - [Push Tokens](#push-tokens)


# Deployment

## Prerequisites
Increase version number using `bump-my-version`.


```bash
# Install bump-my-version
pip i -r requirements.txt

# Bump version
# bump-my-version bump <patch|minor|major> <config-files>
bump-my-version bump patch pyproject.toml
```

## Prod Deployment

Push to `main` branch and see new version on [PyPI](https://pypi.org/project/hellodata-pod-operator-params/)

The action executes the following commands (can also be executed locally):

```bash
pip install -r requirements.txt
python -m build
FILE_NAME=`ls ./dist/ | grep .whl`
curl -F package=@dist/$FILE_NAME https://'${{ secrets.PACKAGE_INDEX_TOKEN }}'@push.fury.io/datenstreambedag/
```

# Install Package

The uploaded package can be installed with the following command:

```bash
pip install --index-url https://pypi.fury.io/datenstreambedag/ hellodata_be_airflow_pod_operator_params
```

# Get Tokens

To get the push / deploy tokens, navigate to the [according page on Gemfury](https://manage.fury.io/manage/datenstreambedag/tokens) and create the token you need.

## Push Tokens

Push tokens are used to push new packages to the registry.