"""Clinical notes schemas."""
from pydantic import BaseModel, Field


class ClinicalNotesUpdate(BaseModel):
    """Schema for updating clinical notes."""
    clinical_notes: str = Field(..., min_length=1, max_length=10000)