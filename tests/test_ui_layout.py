"""Layout rules that do not need a display: breakpoints, RTL mirroring and the dashboard's data."""
import importlib
from unittest import mock

import pytest

from personal_warehouse import i18n
from personal_warehouse.core import database


def test_columns_follow_breakpoints(fake_tk, data_dir):
    w = importlib.import_module("personal_warehouse.ui.widgets")
    bp = [(980, 4), (520, 2)]
    assert [w.cols_for_width(bp, x) for x in (300, 519, 520, 979, 980, 2000)] == [1, 1, 2, 2, 4, 4]


@pytest.mark.parametrize("rtl", [False, True])
def test_flow_puts_first_item_at_the_start_side(fake_tk, data_dir, rtl):
    w = importlib.import_module("personal_warehouse.ui.widgets")
    flow = w.Flow(mock.MagicMock(), rtl, [(900, 3)])
    items = [mock.MagicMock() for _ in range(4)]
    for it in items:
        flow.add(it)
    flow.layout(3)
    col = lambda i: items[i].grid.call_args.kwargs["column"]
    assert [col(0), col(1), col(2)] == ([2, 1, 0] if rtl else [0, 1, 2])
    last = items[3].grid.call_args.kwargs                 # a lone item on the last row spans the full width
    assert (last["row"], last["column"], last["columnspan"]) == (1, 0, 3)


def test_flow_single_column_when_narrow(fake_tk, data_dir):
    w = importlib.import_module("personal_warehouse.ui.widgets")
    flow = w.Flow(mock.MagicMock(), False, [(900, 3)])
    items = [mock.MagicMock() for _ in range(3)]
    for it in items:
        flow.add(it)
    flow.layout(w.cols_for_width(flow.bp, 400))
    assert [it.grid.call_args.kwargs["row"] for it in items] == [0, 1, 2]


def test_dashboard_numbers_and_insights(fake_tk, data_dir):
    theme = importlib.import_module("personal_warehouse.ui.theme")
    app_mod = importlib.import_module("personal_warehouse.ui.app")
    i18n.set_language("en")
    theme.set_theme("light")
    win = app_mod.WarehouseApp()
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part,quantity,min_stock,purchase_price,selling_price)"
                    " VALUES('WH-1','Filter','A','1',0,2,3,5)")
        con.execute("INSERT INTO items(item_code,name,section,part,quantity,min_stock,purchase_price,selling_price)"
                    " VALUES('WH-2','Belt','B','2',10,2,4,9)")
        today = database.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if hasattr(database, "datetime") else None
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute("INSERT INTO movements(item_id,movement_type,quantity,movement_date) VALUES(2,'Stock In',7,?)",
                    (today,))
        con.execute("INSERT INTO movements(item_id,movement_type,quantity,movement_date) VALUES(2,'Stock Out',3,?)",
                    (today,))
    win.refresh_dashboard()
    assert win.metric_vars["items"].get() == "2"
    assert win.metric_vars["alerts"].get() == "1"
    assert win._trend_data_map[today[:10]] == (7, 3)
    assert win.sub_vars["alerts"].get() == "1 out · 0 low"
    win._draw_trend()                                    # must not raise with real data


@pytest.mark.parametrize("lang", ["vi", "en", "ar"])
def test_new_dashboard_texts_exist_in_every_language(fake_tk, data_dir, lang):
    for key in ("card_trend", "card_insights", "ins_ok", "ins_out", "ins_low", "ins_top", "ins_idle", "kpi_sections",
                "kpi_net7", "dash_view_all", "top_search", "trend_empty"):
        assert i18n.TR[key][lang], (key, lang)
