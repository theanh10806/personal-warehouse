import pytest

from personal_warehouse import config, settings
from personal_warehouse.core import database, transfer


def test_settings_replace_failure_preserves_original(data_dir, monkeypatch):
    settings.save_settings(lang="en")
    original = config.SETTINGS_PATH.read_bytes()
    def fail(*args):
        raise OSError("disk failure")
    monkeypatch.setattr(settings.os, "replace", fail)
    with pytest.raises(OSError):
        settings.save_settings(lang="vi")
    assert config.SETTINGS_PATH.read_bytes() == original


def test_migration_backup_failure_propagates(data_dir, monkeypatch):
    with database.db() as connection:
        connection.execute("PRAGMA user_version=1")
    monkeypatch.setattr(database, "verified_backup", lambda path: False)
    with pytest.raises(RuntimeError, match="verification failed"):
        database.pre_migration_backup()
    with database.db() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1


def test_interrupted_restore_recovery_is_repeatable(data_dir):
    photo = config.PHOTO_DIR / "image.jpg"
    added = config.PHOTO_DIR / "new.jpg"
    photo.write_bytes(b"original")
    marker = transfer._prepare_restore_journal([photo, added])
    photo.write_bytes(b"replacement")
    added.write_bytes(b"new")
    assert marker.exists()
    transfer.recover_restore()
    transfer.recover_restore()
    assert photo.read_bytes() == b"original"
    assert not added.exists()


def test_restore_swap_failure_rolls_back_photos(data_dir, tmp_path, monkeypatch):
    photo = config.PHOTO_DIR / "image.jpg"
    photo.write_bytes(b"package")
    package = tmp_path / "snapshot.pwbak"
    transfer.create_package(package)
    photo.write_bytes(b"current")
    def fail(path):
        raise OSError("swap failed")
    monkeypatch.setattr(transfer, "_swap_db", fail)
    with pytest.raises(OSError, match="swap failed"):
        transfer.restore_package(package)
    assert photo.read_bytes() == b"current"
