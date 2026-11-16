"""Optional Pillow import: Image / ImageTk are None when Pillow is not installed."""
try:
    from PIL import Image, ImageTk  # noqa: F401 (re-exported)
except ImportError:
    Image = ImageTk = None
