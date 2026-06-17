import os 
import sys 
from pathlib import Path 
 
BASE_DIR = Path(__file__).resolve().parent.parent.parent 
 
sys.path.insert(0, os.path.join(BASE_DIR, 'apps')) 
 
SECRET_KEY = 'temporary-secret-key-for-base' 
DEBUG = True 
ALLOWED_HOSTS = []

AUTH_USER_MODEL = 'users.User'

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_JWT_SECRET = os.environ.get('SUPABASE_JWT_SECRET', '')
SUPABASE_JWT_AUDIENCE = os.environ.get('SUPABASE_JWT_AUDIENCE', 'authenticated') 
