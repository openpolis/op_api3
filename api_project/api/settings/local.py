__author__ = 'guglielmo'
from .base import *

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = INSTALLED_APPS + (
    'debug_toolbar',
)

OC_PG_CONN = env('OPEN_COESIONE_DB_CONN_STRING')
OP_API_URI = env('OP_API_URI')
OP_API_USERNAME = env('OP_API_USERNAME')
OP_API_PASSWORD = env('OP_API_PASSWORD')