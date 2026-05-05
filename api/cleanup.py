import os
import shutil
import asyncio
from datetime import datetime, timedelta

WEB_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "../data/images/web")


def delete_job_images(job_id: str):
    """Delete the image folder for a specific job. Called after evaluation if no-persist."""
    folder = os.path.join(WEB_IMAGE_DIR, job_id)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"  cleanup: deleted {folder}")


async def cleanup_images(job_id: str, delay_hours: int = 24):
    """Schedule image folder deletion after a delay. Used as a FastAPI background task."""
    await asyncio.sleep(delay_hours * 3600)
    delete_job_images(job_id)


def cleanup_old_images(max_age_hours: int = 24):
    """
    Delete all web image folders older than max_age_hours.
    Run this on startup to catch anything left over from a previous crash.
    """
    if not os.path.isdir(WEB_IMAGE_DIR):
        return

    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    cleaned = 0

    for folder_name in os.listdir(WEB_IMAGE_DIR):
        folder = os.path.join(WEB_IMAGE_DIR, folder_name)
        if not os.path.isdir(folder):
            continue
        modified = datetime.fromtimestamp(os.path.getmtime(folder))
        if modified < cutoff:
            shutil.rmtree(folder)
            cleaned += 1

    if cleaned:
        print(f"  startup cleanup: removed {cleaned} stale image folder(s)")
