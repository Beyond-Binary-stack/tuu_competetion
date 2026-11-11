"""Make a consistent copy of the SQLite database (safe while the server runs)."""
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Back up the SQLite database into backups/"

    def handle(self, *args, **opts):
        src_path = Path(settings.DATABASES["default"]["NAME"])
        out_dir = Path(settings.BASE_DIR) / "backups"
        out_dir.mkdir(exist_ok=True)
        dst_path = out_dir / f"db-{datetime.now():%Y%m%d-%H%M%S}.sqlite3"
        src = sqlite3.connect(src_path)
        dst = sqlite3.connect(dst_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()
        self.stdout.write(self.style.SUCCESS(f"Backup written to {dst_path}"))
