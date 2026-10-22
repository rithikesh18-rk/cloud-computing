"""Dataset preview, sample download, and upload validation endpoints."""

import io
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
import pandas as pd

from app.models.schemas import DatasetPreviewResponse, DatasetUploadResponse, DatasetRow
from app.ml.generator import generate_synthetic_workload

router = APIRouter(prefix="/dataset", tags=["Dataset"])

BASE_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SAMPLE_CSV_PATH = BASE_DATA_DIR / "sample_workload.csv"
ACTIVE_CSV_PATH = BASE_DATA_DIR / "active_workload.csv"

REQUIRED_COLUMNS = ["timestamp", "cpu_usage", "memory_usage", "request_count", "response_time"]


def get_current_dataset_path() -> Path:
    """Return active dataset path, falling back to sample dataset."""
    if ACTIVE_CSV_PATH.exists():
        return ACTIVE_CSV_PATH
    if not SAMPLE_CSV_PATH.exists():
        # Ensure sample dataset exists
        generate_synthetic_workload(days=14, output_path=SAMPLE_CSV_PATH)
    return SAMPLE_CSV_PATH


@router.get("/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview() -> DatasetPreviewResponse:
    """Return top 50 rows, time bounds, and null-value counts of the active dataset."""
    csv_path = get_current_dataset_path()
    if not csv_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No dataset available. Please generate or upload a dataset.",
        )

    df = pd.read_csv(csv_path)

    # Basic validations
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Dataset is missing required columns: {missing_cols}",
        )

    null_counts: Dict[str, int] = {str(col): int(count) for col, count in df.isna().sum().to_dict().items()}

    # Compute time bounds
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    time_bounds = {
        "start": str(df["timestamp"].min()),
        "end": str(df["timestamp"].max()),
    }

    # Extract first 50 rows
    preview_df = df.head(50)
    rows = [
        DatasetRow(
            timestamp=str(row["timestamp"]),
            cpu_usage=float(row["cpu_usage"]),
            memory_usage=float(row["memory_usage"]),
            request_count=int(row["request_count"]),
            response_time=float(row["response_time"]),
        )
        for _, row in preview_df.iterrows()
    ]

    return DatasetPreviewResponse(
        total_rows=len(df),
        time_bounds=time_bounds,
        null_counts=null_counts,
        rows=rows,
    )


@router.get("/sample")
def download_sample_dataset():
    """Download the pre-generated 14-day synthetic cloud workload CSV."""
    if not SAMPLE_CSV_PATH.exists():
        generate_synthetic_workload(days=14, output_path=SAMPLE_CSV_PATH)

    return FileResponse(
        path=str(SAMPLE_CSV_PATH),
        media_type="text/csv",
        filename="cloudpulse_sample_workload.csv",
    )


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetUploadResponse:
    """Validate and upload new cloud telemetry CSV.

    Validates header presence (timestamp, cpu_usage, memory_usage, request_count, response_time),
    numeric types, and removes corrupted rows.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a CSV file with .csv extension.",
        )

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted CSV file: {str(e)}",
        )

    # Check header conformity
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"CSV header validation failed. Missing required columns: {missing_cols}",
        )

    raw_count = len(df)
    if raw_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file contains 0 data rows.",
        )

    # Parse and validate timestamps
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse 'timestamp' column as datetime.",
        )

    # Coerce numeric columns and drop invalid records
    for col in ["cpu_usage", "memory_usage", "request_count", "response_time"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop invalid rows and sort chronologically
    df_valid = df.dropna().sort_values("timestamp").reset_index(drop=True)
    valid_count = len(df_valid)

    if valid_count == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All uploaded rows were invalid or contained non-numeric metrics.",
        )

    # Save to active dataset
    BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df_valid.to_csv(ACTIVE_CSV_PATH, index=False)

    time_bounds = {
        "start": str(df_valid["timestamp"].min()),
        "end": str(df_valid["timestamp"].max()),
    }

    return DatasetUploadResponse(
        message=f"Dataset successfully uploaded and validated. {valid_count}/{raw_count} rows accepted.",
        total_rows=raw_count,
        valid_rows=valid_count,
        time_bounds=time_bounds,
    )
