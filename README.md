# HelloDATA Pod Operator Params

# Deployment

## Prerequisites
Increase version number using `bump-my-version`.

> [!WARNING]  
> The same version cannot be uploaded twice! So always bump the version before pushing!
> So if you push commits without having increased the version, the GitHub Action will fail.

```bash
# Install bump-my-version
pip i -r requirements.txt

# Bump version
# bump-my-version bump <patch|minor|major> <config-file>
bump-my-version bump patch pyproject.toml setup.py
```

> [!NOTE]  
> `bump-my-version` will update the version and create a commit and a tag for the new version.
> This commit can be pushed to upload a new version of the library to the respective package index (test / prod).


## Test Deployment

Push to `develop` branch and see new version on [TestPyPI] (https://test.pypi.org/project/hellodata-pod-operator-params/)

## Prod Deployment

Push to `main` branch and see new version on [PyPI](https://pypi.org/project/hellodata-pod-operator-params/)
