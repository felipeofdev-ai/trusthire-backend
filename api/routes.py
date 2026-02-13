"""
TrustHire Web Routes
Serves the web interface
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
import os

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    """Serve homepage"""
    # Check if index.html exists
    if os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        # Fallback simple HTML
        return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>TrustHire - Verify Before You Trust</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>🛡️ TrustHire</h1>
    <p>Verify recruitment messages before you trust them.</p>
    <p>API Documentation: <a href="/api/v1/docs">/api/v1/docs</a></p>
</body>
</html>
        """)
