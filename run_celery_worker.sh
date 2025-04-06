screen -S celery_worker
cd $HOME/github/neuroanalyst
source venv/bin/activate
celery -A app.celery.celery_app worker --loglevel=info --logfile $NEUROANALYST_LOGS/celery_worker.log