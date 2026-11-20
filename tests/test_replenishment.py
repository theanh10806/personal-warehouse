import pytest

from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api
from test_webui_api import new_item


@pytest.mark.parametrize("quantity,threshold,state,suggested", [
    ("0", "5", "out", "5"), ("2", "5", "low", "3"),
    ("5", "5", "low", None), ("0", "0", "out", None),
    ("0.25", "1.5", "low", "1.25"),
])
def test_stock_notice_supplier_and_minimum_replenishment(data_dir, quantity, threshold, state, suggested):
    set_language("en")
    api = Api()
    item_id = new_item(api, quantity=quantity, min_stock=threshold, supplier="Supplier A", unit="kg")["id"]
    notice = api.dashboard()["alerts"][0]["replenishment"]
    assert notice["state"] == state
    assert notice["supplier"] == "Supplier A"
    if suggested:
        assert f"{suggested} kg" in notice["suggestion"]
    else:
        assert "no higher target" in notice["suggestion"]
    assert api.item_info(item_id)["replenishment"] == notice
    assert api.inventory()["rows"][0]["replenishment"] == notice


def test_supplier_optional_and_notice_disappears_after_stock_in(data_dir):
    api = Api()
    item_id = new_item(api, quantity="1", min_stock="3")["id"]
    assert api.item_info(item_id)["replenishment"]["supplier"] == ""
    assert api.save_movement({"item_id": item_id, "type": "Stock In", "qty": "5"})["ok"]
    assert api.item_info(item_id)["replenishment"] is None
    assert api.dashboard()["alerts"] == []
