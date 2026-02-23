from pydantic import BaseModel, Field, validator
from typing import Optional


class AnalyzeOptions(BaseModel):
    top_n: int = Field(5, ge=1, le=50)
    drop_empty_rows: bool = False
    required_columns: Optional[list[str]] = None


    @validator("required_columns", pre=True)
    def ensure_list(cls, v):
        if v is None:
            return v
        # Accept comma‑separated values
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        # Accept repeated query params (?required_columns=a&required_columns=b)
        if isinstance(v, list):
            return v
        raise ValueError("Invalid required_columns format")