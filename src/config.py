import os


class DefaultConfig:
    GITHUB_AUTH_TOKEN = os.environ.get('GITHUB_API_TOKEN')
    CORS_ORIGINS = ['https://localhost:5000']
