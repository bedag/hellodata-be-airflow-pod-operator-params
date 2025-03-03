# HelloDATA BE Pod Operator Params (OpenSource) <!-- omit from toc -->
- [One time setup](#one-time-setup)
- [When coming back...](#when-coming-back)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Prod Deployment](#prod-deployment)
- [Install Package](#install-package)
- [Get Tokens](#get-tokens)
  - [Push Tokens](#push-tokens)

# One time setup

1. Create local Python environment
```bash
python -m venv venv
```

2. Activate environment
```bash
# For Linux / MacOS
source venv/bin/activate
```

```Powershell
# For Windows Powershell
. ./venv/Scripts/Activate.ps1
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Activate pre-commit hooks
```bash
pre-commit install
```

# When coming back...
Make sure to reactivate Pythons venv:
```bash
# For Linux / MacOS
source venv/bin/activate
```

```Powershell
# For Windows Powershell
. ./venv/Scripts/Activate.ps1
```

# Deployment

## Prerequisites
Increase version number using `bump-my-version` (commit all changes beforehand).


```bash
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
