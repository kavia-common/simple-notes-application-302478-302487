from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.api import models
from src.api.auth import get_current_user
from src.api.db import get_db
from src.api.schemas import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_note_or_404(db: Session, note_id: UUID, user_id: UUID) -> models.Note:
    """Internal helper to load a note owned by the user."""
    stmt = select(models.Note).where(models.Note.id == note_id, models.Note.user_id == user_id)
    note = db.execute(stmt).scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get(
    "",
    response_model=list[NoteOut],
    summary="List notes",
    description="List all notes for the current user ordered by last updated.",
    operation_id="notes_list",
)
def list_notes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> list[NoteOut]:
    """List notes for the current user."""
    stmt = select(models.Note).where(models.Note.user_id == current_user.id).order_by(desc(models.Note.updated_at))
    return list(db.execute(stmt).scalars().all())


@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note for the current user.",
    operation_id="notes_create",
)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> NoteOut:
    """Create a note owned by the current user."""
    note = models.Note(user_id=current_user.id, title=payload.title or "", content=payload.content or "")
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get note",
    description="Get a single note by id (must be owned by current user).",
    operation_id="notes_get",
)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> NoteOut:
    """Fetch a note by ID."""
    return _get_note_or_404(db, note_id, current_user.id)


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update a note's title/content (must be owned by current user).",
    operation_id="notes_update",
)
def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> NoteOut:
    """Update note by ID."""
    note = _get_note_or_404(db, note_id, current_user.id)

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note (must be owned by current user).",
    operation_id="notes_delete",
)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
) -> None:
    """Delete note by ID."""
    note = _get_note_or_404(db, note_id, current_user.id)
    db.delete(note)
    db.commit()
    return None
