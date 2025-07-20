
import os

def getSmartSuiteEnv():
    smartsuite_api_key = os.getenv("SMARTSUITE_API_KEY")
    smartsuite_account_id = os.getenv("SMARTSUITE_ACCOUNT_ID")
    return smartsuite_api_key, smartsuite_account_id
