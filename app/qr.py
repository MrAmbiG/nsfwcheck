import cv2
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

def extract_qr_urls(image_bytes: bytes) -> List[str]:
    """
    Extract URLs from QR codes in image bytes using OpenCV.
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Could not decode image")
            return []

        # Initialize OpenCV QR code detector
        qr_detector = cv2.QRCodeDetector()
        urls = []

        # Try different image processing techniques for better QR detection
        # 1. Original
        # 2. Grayscale
        # 3. Enhanced contrast (equalized)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.equalizeHist(gray)

        variants = [img, gray, enhanced]

        for variant in variants:
            # detectAndDecode can return multiple QR codes in recent OpenCV versions
            # but detectAndDecode itself often works better for single/primary QR.
            # Using detectAndDecodeMulti for broader coverage if available.
            retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(variant)
            if retval:
                for info in decoded_info:
                    if info and info not in urls:
                        urls.append(info)
                        logger.info(f"Found QR URL: {info}")
            else:
                # Fallback to single detection
                data, bbox, _ = qr_detector.detectAndDecode(variant)
                if data and data not in urls:
                    urls.append(data)
                    logger.info(f"Found QR URL: {data}")

        return urls

    except Exception as e:
        logger.error(f"QR code extraction error: {e}")
        return []
