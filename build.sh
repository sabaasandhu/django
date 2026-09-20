#!/usr/bin/env bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput --ignore=*.scss
python manage.py migrate
