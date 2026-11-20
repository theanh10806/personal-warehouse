import pytest

from personal_warehouse.core.database import db
from personal_warehouse.core.stock import apply_movement
from personal_warehouse.instance import single_instance


@pytest.mark.parametrize("typ,quantity,price", [
    ("invalid", 1, 0), ("Stock In", -1, 0),
    ("Stock Out", float("nan"), 0), ("Adjustment", float("inf"), 0),
    ("Stock In", 1, -1), ("Stock Out", 0, 0),
])
def test_invalid_movement_leaves_no_record(data_dir, typ, quantity, price):
    with pytest.raises(ValueError):
        apply_movement(999, typ, quantity, price, "test")
    with db() as con:
        assert con.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 0


def test_missing_item_is_rejected(data_dir):
    with pytest.raises(ValueError, match="does not exist"):
        apply_movement(999, "Stock In", 1, 0, "test")


def test_instance_lock_released_after_exception(tmp_path, monkeypatch):
    monkeypatch.setattr("personal_warehouse.instance.Path.home", lambda: tmp_path)
    with pytest.raises(RuntimeError):
        with single_instance() as acquired:
            assert acquired
            with single_instance() as second:
                assert not second
            raise RuntimeError("crash")
    with single_instance() as acquired:
        assert acquired
