import os
import shlex
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    os.chdir(settings.BASE_DIR)
    cmd = "pkill celery"
    subprocess.call(shlex.split(cmd))
    cmd = "celery worker -l info -A config"
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting celery worker with autoreload...")
        autoreload.run_with_reloader(restart_celery)
