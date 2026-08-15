"""CSV import/export endpoints."""
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.csv import ImportSummary
from app.services.csv_service import export_csv, import_csv
from app.utils.response import Envelope, ok

router = APIRouter(prefix="/csv", tags=["CSV Import / Export"])


@router.post("/import", response_model=Envelope[ImportSummary])
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Import expenses from a CSV file. Returns an import summary."""
    return ok(import_csv(db, current_user, file))


@router.get("/export")
def download_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the user's expenses as a CSV file."""
    content = export_csv(db, current_user)
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=expenses.csv",
        },
    )
