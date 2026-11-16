"""Read QR codes / barcodes from an image (OpenCV, optional pyzbar)."""


def decode_codes(img):
    """Read one QR code or 1-D barcode from an OpenCV image. Returns '' if nothing found."""
    try:
        import cv2
    except ImportError:
        return ""
    try:
        text, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
        if text:
            return text
    except Exception:
        pass
    try:                                            # OpenCV >= 4.8
        res = cv2.barcode.BarcodeDetector().detectAndDecode(img)
        infos = res[1] if len(res) == 4 else res[0]
        for s in ([infos] if isinstance(infos, str) else list(infos or [])):
            if s:
                return s
    except Exception:
        pass
    try:                                            # optional: pip install pyzbar
        from pyzbar import pyzbar
        for d in pyzbar.decode(img):
            return d.data.decode("utf-8", "ignore")
    except Exception:
        pass
    return ""
