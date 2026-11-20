import re
from pathlib import Path

from personal_warehouse.core.database import db
from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api
from test_webui_api import new_item


def test_zero_opening_with_later_stock_cannot_undo_create(data_dir):
    api = Api()
    item_id = new_item(api, quantity="0")["id"]
    created = api.history_list()["rows"][0]["id"]
    assert api.save_movement({"item_id": item_id, "type": "Stock In", "qty": "5"})["ok"]
    assert api.history_undo(created, True)["ok"] is False
    assert api.get_item(item_id)["item"]["quantity"] == "5"


def test_delete_restore_redo_keeps_full_ledger(data_dir):
    api = Api()
    item_id = new_item(api)["id"]
    assert api.save_movement({"item_id": item_id, "type": "Stock Out", "qty": "3"})["ok"]
    assert api.delete_items([item_id], True)["ok"]
    deleted = api.history_list()["rows"][0]["id"]
    for expected_exists in (True, False, True):
        assert api.history_undo(deleted, True)["ok"]
        assert api.get_item(item_id)["ok"] is expected_exists
        if expected_exists:
            assert api.get_item(item_id)["item"]["quantity"] == "7"
            assert len(api.movements(item_id)["rows"]) == 2
        deleted = api.history_list()["rows"][0]["id"]


def test_history_same_timestamp_order_and_redo_labels(data_dir):
    set_language("en")
    api = Api()
    item_id = new_item(api)["id"]
    assert api.save_movement({"item_id": item_id, "type": "Stock In", "qty": "2"})["ok"]
    original = api.history_list()["rows"][0]["id"]
    assert api.history_undo(original, True)["ok"]
    rows = api.history_list()["rows"]
    assert rows[0]["operation"] == "undo" and rows[0]["reverse_label"] == "Redo"
    assert rows[0]["source_id"] == original
    undo_id = rows[0]["id"]
    confirm = api.history_undo(undo_id)
    assert confirm["title"] == "Redo" and f"#{undo_id}" in confirm["message"]
    assert api.history_undo(undo_id, True)["ok"]
    with db() as connection:
        connection.execute("UPDATE history SET ts='2026-11-20 10:00:00'")
    rows = api.history_list()["rows"]
    assert [row["id"] for row in rows] == sorted([row["id"] for row in rows], reverse=True)
    assert rows[0]["operation"] == "redo" and rows[0]["reverse_label"] == "Undo"
    assert api.history_undo(original)["ok"] is False


def test_static_button_actions_have_handlers():
    source = (Path(__file__).resolve().parents[1] / "src/personal_warehouse/webui/static/app.js").read_text(encoding="utf-8")
    handlers = source[source.index("const ACT ="):source.index("document.addEventListener('click'")]
    names = set(re.findall(r"['\"]([a-z][a-z0-9-]+)['\"]\s*:", handlers))
    declared = set(re.findall(r'data-act="([a-z][a-z0-9-]+)"', source))
    declared.update(re.findall(r"btnHtml\([^\n]*?,\s*'([a-z][a-z0-9-]+)'", source))
    assert declared - names == set()
