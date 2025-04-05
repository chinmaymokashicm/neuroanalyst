screen -S celery_worker
cd $HOME/github/neuroanalyst
celery -A app.celery.celery_app worker --loglevel=info