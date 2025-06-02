import os
import sys
from dotenv import load_dotenv
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration, loading secrets from Azure Key Vault.
    """
    MICROSOFT_APP_ID: str
    MICROSOFT_APP_PASSWORD: str

    DB_SERV: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: int

    AMMAN_RP_SAP_SERV: str
    AMMAN_RP_SAP_USER: str
    AMMAN_RP_SAP_PASS: str

    AZURE_STORAGE_CONNECTION_STRING: str
    AZURE_STORAGE_CONTAINER_NAME: str

    _key_vault_url: str
    _client_id: str | None = None
    _client_secret: str | None = None
    _tenant_id: str | None = None

    def __init__(self):
        # These are needed before the async loading begins
        self._key_vault_url = os.getenv("DEV_AZURE_KEY_VAULT_URL")
        self._client_id = os.getenv("DEV_AZURE_CLIENT_ID")
        self._client_secret = os.getenv("DEV_AZURE_CLIENT_SECRET")
        self._tenant_id = os.getenv("DEV_AZURE_TENANT_ID")

        if not self._key_vault_url:
            print(
                "CRITICAL WARNING: AZURE_KEY_VAULT_URL is not set in .env. Key Vault loading will fail.")

    async def load_secrets_from_keyvault(self):
        """
        Authenticates with Azure and loads secrets from Key Vault.
        Uses ClientSecretCredential for local development based on .env.
        Consider using DefaultAzureCredential or ManagedIdentityCredential for deployment.
        """
        if not self._key_vault_url:
            print("Skipping Key Vault loading as URL is not configured.")
            return

        credential = None
        try:
            # Prioritize ClientSecretCredential if credentials are provided in .env
            if all([self._client_id, self._client_secret, self._tenant_id]):
                credential = ClientSecretCredential(
                    self._tenant_id, self._client_id, self._client_secret)
                print("Using ClientSecretCredential for Key Vault.")
            else:
                # Fallback to DefaultAzureCredential if explicit creds are missing
                print(
                    "ClientSecretCredential details missing, attempting DefaultAzureCredential.")
                credential = DefaultAzureCredential()

            client = SecretClient(
                vault_url=self._key_vault_url, credential=credential)
            print(
                f"Attempting to load secrets from Key Vault at {self._key_vault_url}...")
            # Load secrets by name from Key Vault using the secret names from .env
            # Need to define *_SECRET_NAME variables in .env if not already
            self.MICROSOFT_APP_ID = (await client.get_secret(os.getenv("DEV_MICROSOFT_APP_ID"))).value
            self.MICROSOFT_APP_PASSWORD = (await client.get_secret(os.getenv("DEV_MICROSOFT_APP_PASSWORD"))).value
            self.AZURE_STORAGE_CONNECTION_STRING = (await client.get_secret(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))).value
            self.AZURE_STORAGE_CONTAINER_NAME = (await client.get_secret(os.getenv("AZURE_STORAGE_CONTAINER_NAME"))).value
            self.DB_SERV = (await client.get_secret(os.getenv("DB_SERV_SECRET_NAME"))).value
            self.DB_NAME = (await client.get_secret(os.getenv("DB_NAME_SECRET_NAME"))).value
            self.DB_USER = (await client.get_secret(os.getenv("DB_USER_SECRET_NAME"))).value
            self.DB_PASS = (await client.get_secret(os.getenv("DB_PASS_SECRET_NAME"))).value
            self.DB_PORT = int((await client.get_secret(os.getenv("DB_PORT_SECRET_NAME"))).value)
            self.AMMAN_RP_SAP_SERV = (await client.get_secret(os.getenv("AMMAN_RP_SAP_SERV"))).value
            self.AMMAN_RP_SAP_USER = (await client.get_secret(os.getenv("AMMAN_RP_SAP_USER"))).value
            self.AMMAN_RP_SAP_PASS = (await client.get_secret(os.getenv("AMMAN_RP_SAP_PASS"))).value

            print("Secrets loaded successfully from Key Vault.")
        except Exception as e:
            print(f"ERROR loading secrets from Key Vault: {e}")
            raise ValueError("Loading Azure Key Vault credentials error")
        finally:
            print(f"Azure key vault closing session")
            await client.close()
            await credential.close()


# Global variable to hold the loaded configuration instance, or act like singleton
# This will be populated during the FastAPI lifespan startup event
app_config: Config = Config()
