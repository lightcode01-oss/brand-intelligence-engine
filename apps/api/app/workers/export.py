from app.workers.celery_app import celery_app
from app.utils.exports import generate_export_files

@celery_app.task
def async_compile_export_task(report_data: dict, export_format: str) -> dict:
    """Task compiling report data into PDF, Markdown, JSON or CSV files."""
    try:
        file_path = generate_export_files(report_data, export_format)
        return {"status": "SUCCESS", "format": export_format, "file_path": file_path}
    except Exception as exc:
        return {"status": "FAILURE", "error": str(exc)}
