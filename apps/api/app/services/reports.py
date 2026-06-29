import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.report import SavedReport

class ReportsManager:
    """Enterprise saved reports operations manager supporting CSV, JSON, Markdown, and PDF formats."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report(
        self, workspace_id: uuid.UUID, user_id: uuid.UUID, name: str, report_type: str, fmt: str, data: Dict[str, Any]
    ) -> SavedReport:
        """Stores a historical report in the database with version tracking."""
        # Find next version if name matches
        stmt = select(SavedReport).where(
            SavedReport.workspace_id == workspace_id,
            SavedReport.name == name
        ).order_by(desc(SavedReport.version)).limit(1)
        
        last_report = (await self.db.execute(stmt)).scalar()
        next_ver = (last_report.version + 1) if last_report else 1

        report = SavedReport(
            workspace_id=workspace_id,
            user_id=user_id,
            name=name,
            report_type=report_type,
            format=fmt.lower(),
            data_json=data,
            version=next_ver
        )
        
        self.db.add(report)
        await self.db.flush()
        return report

    async def list_reports(self, workspace_id: uuid.UUID) -> List[SavedReport]:
        """Lists all saved reports in a workspace."""
        stmt = select(SavedReport).where(
            SavedReport.workspace_id == workspace_id,
            SavedReport.deleted_at == None
        ).order_by(desc(SavedReport.created_at))
        
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_report_by_id(self, report_id: uuid.UUID) -> Optional[SavedReport]:
        """Fetches a specific saved report."""
        stmt = select(SavedReport).where(
            SavedReport.id == report_id,
            SavedReport.deleted_at == None
        )
        return (await self.db.execute(stmt)).scalar()

    def compile_export_stream(self, report: SavedReport) -> tuple[str, str]:
        """Converts report details to Markdown, CSV, JSON, or PDF download text streams."""
        fmt = report.format.lower()
        content = ""
        media_type = "text/plain"
        
        if fmt == "json":
            content = json.dumps(report.data_json, indent=2)
            media_type = "application/json"
            
        elif fmt == "csv":
            # Extract simple dict to rows
            headers = ["Metric", "Value"]
            rows = [f"{k},{v}" for k, v in report.data_json.items() if not isinstance(v, (dict, list))]
            content = ",".join(headers) + "\n" + "\n".join(rows)
            media_type = "text/csv"
            
        elif fmt == "markdown" or fmt == "pdf":
            # Generate standard readable markdown structure
            lines = [
                f"# Nomen Enterprise Report: {report.name}",
                f"- **Workspace ID:** {report.workspace_id}",
                f"- **Report Type:** {report.report_type}",
                f"- **Version:** v{report.version}",
                f"- **Generated At:** {report.created_at.isoformat() if report.created_at else datetime.now(timezone.utc).isoformat()}",
                "---",
                "## Metric Summary Parameters",
                "| Parameter | Value |",
                "| --- | --- |"
            ]
            for k, v in report.data_json.items():
                if not isinstance(v, (dict, list)):
                    lines.append(f"| {k} | {v} |")
                    
            content = "\n".join(lines)
            media_type = "text/markdown" if fmt == "markdown" else "application/pdf" # PDF wraps markdown for text readers fallback
            
        return content, media_type
