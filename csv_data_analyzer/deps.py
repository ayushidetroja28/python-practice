from fastapi import Depends
from models import AnalyzeOptions


# defaults can come from env or config
async def get_options(opts: AnalyzeOptions = Depends()):
    return opts