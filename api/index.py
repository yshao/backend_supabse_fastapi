import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.api.index import app
from mangum import Mangum

# Vercel serverless handler
handler = Mangum(app, lifespan="off")
