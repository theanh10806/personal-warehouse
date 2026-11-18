"""Online machine translation (needs Internet)."""

import json
import urllib.parse
import urllib.request


def translate_online(text, target="ar"):
    """Machine translation through a public web endpoint (needs Internet)."""
    url = ("https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl="
           f"{target}&dt=t&q={urllib.parse.quote(text)}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(seg[0] for seg in data[0] if seg and seg[0]).strip()
