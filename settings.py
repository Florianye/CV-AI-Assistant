import pysqlite3
import sys
import os
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(".", 'db.sqlite3'),
#     }
# }