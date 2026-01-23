from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List, Optional, Dict, Any
import httpx
import logging
import asyncio

from app.config import settings
from app.qr import extract_qr_urls

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}

async def check_url_remote(url: str) -> Dict[str, Any]:
    """
    Check URL against urlsafe service.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.URLSAFE_SERVICE_URL}/check",
                params={"url": url}
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"urlsafe service returned {response.status_code}")
                return {"error": "urlsafe_failed"}
    except Exception as e:
        logger.error(f"Error connecting to urlsafe: {e}")
        return {"error": "urlsafe_unreachable"}

async def check_image_remote(image_bytes: bytes) -> Dict[str, Any]:
    """
    Check image against imagesafe service.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            files = {"image": ("image.jpg", image_bytes, "image/jpeg")}
            response = await client.post(
                f"{settings.IMAGESAFE_SERVICE_URL}/check",
                files=files
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"imagesafe service returned {response.status_code}")
                return {"error": "imagesafe_failed"}
    except Exception as e:
        logger.error(f"Error connecting to imagesafe: {e}")
        return {"error": "imagesafe_unreachable"}

@app.post("/check/url")
async def check_url(url: str = Form(...)):
    """
    Checks a single URL for NSFW and malicious content.
    """
    result = await check_url_remote(url)
    return result

@app.post("/check/image")
async def check_image(image: UploadFile = File(...)):
    """
    Handles image upload, extracts QR codes, and checks both image content and extracted URLs.
    """
    image_bytes = await image.read()

    # 1. Start Image Safety Check (Node.js service)
    # 2. Extract QR URLs
    # 3. Check extracted URLs (Python service)

    image_task = asyncio.create_task(check_image_remote(image_bytes))

    # QR Extraction is synchronous (CPU bound/OpenCV), ideally we'd run it in a threadpool
    # but for simplicity we'll do it here or via run_in_executor
    loop = asyncio.get_event_loop()
    qr_urls = await loop.run_in_executor(None, extract_qr_urls, image_bytes)

    url_results = []
    if qr_urls:
        url_tasks = [check_url_remote(url) for url in qr_urls]
        url_results = await asyncio.gather(*url_tasks)

    image_result = await image_task

    # Consolidate results
    is_explicit = False
    is_malicious = False

    # Check image content result
    if "porn" in image_result and image_result["porn"] > settings.NSFW_THRESHOLD:
        is_explicit = True
    if "hentai" in image_result and image_result["hentai"] > settings.NSFW_THRESHOLD:
        is_explicit = True
    if "sexy" in image_result and image_result["sexy"] > 0.9: # Stricter for 'sexy'
        is_explicit = True

    # Check URL results
    for url_res in url_results:
        if url_res.get("is_adult"):
            is_explicit = True
        if url_res.get("is_malicious"):
            is_malicious = True

    return {
        "is_explicit": is_explicit,
        "is_malicious": is_malicious,
        "image_content": image_result,
        "qr_urls": [
            {"url": url, "result": res} for url, res in zip(qr_urls, url_results)
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
