"""About page, feedback mail links, support info."""
from urllib.parse import parse_qs, unquote, urlparse

import pytest

from personal_warehouse import about
from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api


@pytest.fixture()
def api(data_dir):
    set_language("en")
    return Api()


def test_about_info(api):
    r = api.about_info()
    assert r["ok"] and r["email"] == "theanh1129@gmail.com" and r["github"].startswith("https://github.com/")
    assert {k["value"] for k in r["kinds"]} == {"idea", "bug", "thanks", "other"}


def test_feedback_builds_mailto_to_the_author(api):
    r = api.feedback_send("bug", "The export button is broken", "me@x.com", True, "mail")
    assert r["ok"] and r["open_in_js"]
    u = urlparse(r["url"])
    assert u.scheme == "mailto" and u.path == "theanh1129@gmail.com"
    q = parse_qs(u.query)
    assert "Bug report" in q["subject"][0]
    body = q["body"][0]
    assert "export button is broken" in body and "Contact: me@x.com" in body and "Python" in body


def test_feedback_without_system_info_and_gmail_link(api):
    r = api.feedback_send("idea", "Add dark mode please", "", False, "gmail")
    assert r["url"].startswith("https://mail.google.com/mail/?view=cm") and "to=theanh1129%40gmail.com" in r["url"]
    assert "Python" not in unquote(r["url"])


def test_feedback_validation(api):
    assert api.feedback_send("idea", "  ", "", True)["ok"] is False
    long = api.feedback_send("idea", "ü" * 1000, "", True, "mail")                # percent-encoding blows past the limit
    assert long["ok"] is False and long["copy"]                                      # user can still copy it
    assert api.feedback_send("idea", "ü" * 1000, "", True, "gmail")["ok"]


def test_open_link_only_known_keys(api):
    assert api.open_link("github")["url"] == about.GITHUB_URL
    assert api.open_link("javascript:alert(1)")["ok"] is False
