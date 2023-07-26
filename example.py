from azure_ad_interactor import AzureActiveDirectoryInteractor
import os

azure_ad_interactor = AzureActiveDirectoryInteractor()
user = azure_ad_interactor.get_user(os.environ.get("USER_EMAIL"))
print(user)
