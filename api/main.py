import app
from api.db import init_db
from api.cleanup import cleanup_old_images

@app.on_event("startup")
def startup():
    init_db()
    cleanup_old_images(max_age_hours=24)
