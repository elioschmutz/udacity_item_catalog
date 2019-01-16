activate_this = '/apps/udacity_item_catalog/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/apps/udacity_item_catalog')

from application import app as application
