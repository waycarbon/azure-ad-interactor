import json
from dataclasses import dataclass
from typing import Union, Optional

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from requests import Session


def log(data):
    print(json.dumps(data, default=str))


DEFAULT_ROLE_DISPLAY_NAMES = {"User", "msiam_access"}


@dataclass
class AzureADInteractorConfig:
    client_id: str
    tenant_id: str
    client_secret: str


# AZURE_CLIENT_ID, AZURE_TENANT_ID and AZURE_CLIENT_SECRET environment variables must be set!
class AzureActiveDirectoryInteractor:
    request_session: Session = Session()
    microsoft_graph_url: str = "https://graph.microsoft.com/v1.0"
    credential: Union[DefaultAzureCredential, ClientSecretCredential]

    def __init__(self, config: Optional[AzureADInteractorConfig] = None):
        if config is not None:
            self.credential = ClientSecretCredential(**vars(config))
        else:
            self.credential = DefaultAzureCredential()
        self.refresh_azure_token()

    def refresh_azure_token(self):
        scope = "https://graph.microsoft.com/.default"
        token = self.credential.get_token(scope).token

        self.request_session.headers = {"Authorization": f"Bearer {token}"}

    def get_json_or_raise_for_status(self, resource):
        url = f"{self.microsoft_graph_url}{resource}"
        response = self.request_session.get(url)
        response.raise_for_status()
        return response.json()

    def get_resource_and_resolve_continuation(self, resource):
        response_json = self.get_json_or_raise_for_status(resource)
        yield from response_json["value"]
        while response_json.get("@odata.nextLink") is not None:
            response = self.request_session.get(response_json["@odata.nextLink"])
            response.raise_for_status()
            response_json = response.json()
            yield from response_json["value"]

    def get_user(self, user_email):
        return self.get_json_or_raise_for_status(f"/users/{user_email}")

    def get_service_principal(self, service_principal_id):
        return self.get_json_or_raise_for_status(f"/servicePrincipals/{service_principal_id}")

    def get_role_assignments_from_service_principal(self, service_principal_id):
        return self.get_resource_and_resolve_continuation(f"/servicePrincipals"
                                                          f"/{service_principal_id}/appRoleAssignedTo")

    def assign_user_to_service_principal(self, service_principal, user, role_name=None):
        role_to_add = (next(role for role in service_principal["appRoles"] if role_name == role["displayName"])
                       if role_name else
                       {"id": "00000000-0000-0000-0000-000000000000"})
        payload = {"appRoleId": role_to_add["id"],
                   "resourceId": service_principal['id'],
                   "principalId": user["id"]}
        log(payload)
        assignment_response = self.request_session.post(f"{self.microsoft_graph_url}/users"
                                                        f"/{user['id']}/appRoleAssignments",
                                                        json=payload)
        log(assignment_response.json())


def _service_principal_has_custom_roles(service_principal):
    _, service_principal_data = service_principal
    non_default_roles = [role for role in service_principal_data["appRoles"]
                         if role["displayName"] not in DEFAULT_ROLE_DISPLAY_NAMES and role["isEnabled"]]
    return len(non_default_roles) > 0
