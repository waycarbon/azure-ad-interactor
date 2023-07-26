# azure-ad-interactor
Python Interactor for Azure AD REST API

# Prerequisites

- Python 3.9+
- Poetry

# Development

- Each new feature should be developed and merged using pull requests.
- Each new release should be done using the Github release feature.

# Installation

You can install this package using pipenv or poetry.

**NOTE**: Change v0.1.0 in the installation scenarios to the required release tag.

## pipenv

```shell
pipenv install -e 'git+ssh://git@github.com/waycarbon/azure-ad-interactor.git@v0.1.0#egg=azure-ad-interactor'
```

## poetry

```shell
poetry add 'git+ssh://git@github.com/waycarbon/azure-ad-interactor.git#v0.1.0'
```

# Usage

Required environment variables:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_SECRET`

```python
from azure_ad_interactor import AzureActiveDirectoryInteractor
azure_ad_interactor = AzureActiveDirectoryInteractor()
user = azure_ad_interactor.get_user("example@email.com")
```

