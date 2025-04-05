from ..utils.constants import *
from ..utils.envs import set_neuroanalyst_root_dirs

import importlib, pkgutil, logging

from celery import Celery
from celery.signals import after_setup_logger

set_neuroanalyst_root_dirs()

# Configure Celery with Redis as the broker
celery_app = Celery(
    "neuroimaging_tasks",
    # broker="redis://localhost:6379/0",  # Using Redis running in Docker
    # backend="redis://localhost:6379/0",
    broker=REDIS_BROKER_URL, # Using Redis running locally
    backend=REDIS_BROKER_URL
    # include=["app.celery.tasks"],
)

# Automatically discover all task modules in celery/tasks
def autodiscover_tasks(package_name):
    package = importlib.import_module(package_name)
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        importlib.import_module(f"{package_name}.{modname}")

# Call autodiscovery for celery.tasks
autodiscover_tasks("app.celery.tasks")

@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Example: File logging
    fh = logging.FileHandler(CELERY_LOG_FILEPATH)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
