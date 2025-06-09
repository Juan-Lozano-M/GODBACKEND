import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

load_dotenv()

cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred, {
    'projectId': os.getenv('FIREBASE_PROJECT_ID')
})

print("Firebase Admin initialized")
