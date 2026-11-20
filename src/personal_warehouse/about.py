"""Facts shown on the About page + how feedback e-mails are built. Edit the constants below to change them."""
import platform
from urllib.parse import quote

from personal_warehouse import __version__

AUTHOR_NAME = "Võ Thế Anh"
CONTACT_EMAIL = "theanh1129@gmail.com"
GITHUB_URL = "https://github.com/theanh10806/personal-warehouse"
ISSUES_URL = GITHUB_URL + "/issues"

# Ways to support the author. One dict per line on the page; "value" gets a Copy button.
# Add your real details here, e.g. {"label": "Vietcombank", "value": "0123456789 - NGUYEN VAN A"},
#                                  {"label": "PayPal", "value": "https://paypal.me/yourname"}.
# A QR picture named donate_qr.png placed in webui/static/ is shown automatically.
DONATE = []

MAILTO_LIMIT = 1900                    # Windows cuts mailto: links longer than ~2000 characters
GMAIL_LIMIT = 7000
LINKS = {"github": GITHUB_URL, "issues": ISSUES_URL}


def system_info(lang):
    return f"Personal Warehouse {__version__} | {platform.system()} {platform.release()} | Python {platform.python_version()} | lang={lang}"


def compose(kind_label, message, contact, include_info, lang):
    """Return (subject, body) for a feedback mail. Nothing from the warehouse itself is ever included."""
    body = (message or "").strip()
    if contact and contact.strip():
        body += f"\n\nContact: {contact.strip()}"
    if include_info:
        body += f"\n\n---\n{system_info(lang)}"
    return f"[Personal Warehouse {__version__}] {kind_label}", body


def mailto_url(subject, body):
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


def gmail_url(subject, body):
    return f"https://mail.google.com/mail/?view=cm&fs=1&to={quote(CONTACT_EMAIL)}&su={quote(subject)}&body={quote(body)}"
