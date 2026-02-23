from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
import io
import uvicorn
import pandas as pd
from analyzer import analyze_csv
from deps import get_options, AnalyzeOptions


app = FastAPI(title="CSV Data Analyzer")

@app.post("/upload-and-process")
async def upload_and_process(
    file: UploadFile = File(...),
    options: AnalyzeOptions = Depends(get_options),
):
    """
    - Validate file extension
    - Validate columns if required
    - Drop empty rows if instructed
    - Return both: stats + processed CSV
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files allowed")
    
    raw = await file.read()
    buffer = io.BytesIO(raw)

    try:
        df = pd.read_csv(buffer)
    except Exception as e:
        raise HTTPException(400, f"CSV parse error: {e}")

    print(options)
    # Required columns validation
    if options.required_columns:
        missing = [c for c in options.required_columns if c not in df.columns]
        if missing:
            raise HTTPException(400, f"Missing required columns: {missing}")


    # Optional cleaning
    if options.drop_empty_rows:
        df = df.dropna(how="all")

     # FIXED: analyze the dataframe directly
    from analyzer import analyze_dataframe
    stats = analyze_dataframe(df, top_n=options.top_n)


    # Return processed CSV
    output_buf = io.StringIO()
    df.to_csv(output_buf, index=False)
    output_buf.seek(0)


    return {
        "stats": stats,
        "processed_csv": output_buf.getvalue(),
    }

@app.post("/analyze-file")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")


    try:
        # read into memory (ok for small -> medium files). For large files stream/temporary file recommended.
        contents = await file.read()
        # pandas can read bytes buffer via io.BytesIO
        import io
        buffer = io.BytesIO(contents)
        stats = analyze_csv(buffer)
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)