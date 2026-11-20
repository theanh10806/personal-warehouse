"""Move the whole warehouse between computers: one ``.pwbak`` file (a zip) holding the database, photos and settings.
Optionally encrypted with a password (AES-256-GCM, scrypt key, needs the ``cryptography`` package).

* ``create_package``  snapshot -> a single file you can copy, e-mail or drop into OneDrive / Google Drive / Dropbox.
* ``inspect_package`` checks a file *without* touching your data (is it ours, is it intact, is it from a newer app).
* ``restore_package`` replaces the current data with the package (a safety copy of the current data is made first).
* ``sync_to_folder``  writes a dated package into a synced folder and keeps only the newest few.

No GUI code here. Photos are stored by file name only, so they stay valid on any computer.
"""
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import zipfile

from personal_warehouse import __version__, config
from personal_warehouse.config import SCHEMA_VERSION
from personal_warehouse.core.database import backup_db_to, db, init_db, verify_db

EXT = ".pwbak"
FORMAT = 1
KEEP_SYNC_COPIES = 7
_PORTABLE_SETTINGS = ("lang", "theme")          # not machine-specific paths / update state


MAGIC = b"PWENC1\n"                                    # first bytes of a password-protected package
_CHUNK = 1 << 20


class PackageError(ValueError):
    """The file is not a usable package. The message is a short code the API turns into a readable text."""



# ------------------------------------------------------------------ optional password protection
def crypto_available():
    try:
        import cryptography  # noqa: F401
        return True
    except ImportError:
        return False


def is_encrypted(path):
    try:
        with open(path, "rb") as f:
            return f.read(len(MAGIC)) == MAGIC
    except OSError:
        return False


def _aes(password, salt):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    except ImportError:
        raise PackageError("no_crypto") from None
    return AESGCM(Scrypt(salt=salt, length=32, n=2 ** 15, r=8, p=1).derive(password.encode("utf-8")))


def encrypt_file(src, dst, password):
    """Chunked AES-GCM. The chunk number is in the nonce and a 'last chunk' flag in the AAD, so chunks cannot be
    reordered, dropped or the file silently truncated."""
    salt, prefix = os.urandom(16), os.urandom(4)
    aes = _aes(password, salt)
    with open(src, "rb") as f, open(dst, "wb") as out:
        out.write(MAGIC + salt + prefix)
        cur, i = f.read(_CHUNK), 0
        while True:
            nxt = f.read(_CHUNK)
            out.write(aes.encrypt(prefix + i.to_bytes(8, "big"), cur, b"\x01" if not nxt else b"\x00"))
            if not nxt:
                break
            cur, i = nxt, i + 1


def decrypt_file(src, dst, password):
    from cryptography.exceptions import InvalidTag
    with open(src, "rb") as f, open(dst, "wb") as out:
        head = f.read(len(MAGIC) + 20)
        if len(head) < len(MAGIC) + 20 or not head.startswith(MAGIC):
            raise PackageError("not_package")
        aes = _aes(password, head[len(MAGIC):len(MAGIC) + 16])
        prefix = head[-4:]
        cur, i = f.read(_CHUNK + 16), 0
        while True:
            nxt = f.read(_CHUNK + 16)
            try:
                out.write(aes.decrypt(prefix + i.to_bytes(8, "big"), cur, b"\x01" if not nxt else b"\x00"))
            except InvalidTag:
                raise PackageError("bad_password") from None
            if not nxt:
                break
            cur, i = nxt, i + 1


@contextmanager
def _plain(path, password=None):
    """Yield the path of a readable zip (decrypted into a temp folder when the package is protected)."""
    if not is_encrypted(path):
        yield path
        return
    if not password:
        raise PackageError("need_password")
    tmp = Path(tempfile.mkdtemp(prefix="pw_dec_"))
    try:
        decrypt_file(path, tmp / "p.zip", password)
        yield tmp / "p.zip"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _counts(db_file):
    con = sqlite3.connect(db_file)
    try:
        items = con.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        moves = con.execute("SELECT COUNT(*) FROM movements").fetchone()[0]
    finally:
        con.close()
    return items, moves


def create_package(dest, password=None):
    """Write a package to ``dest`` (a file path ending in .pwbak). Returns the manifest dict.

    With ``password`` the whole file is encrypted. The file appears under its final name only when complete."""
    if password and not crypto_available():
        raise PackageError("no_crypto")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix="pw_pack_"))
    part = dest.with_name(dest.name + ".part")           # written next to the target, renamed when complete
    try:
        snap = tmp_dir / "warehouse.db"
        backup_db_to(snap)                               # consistent snapshot even while the app is open
        items, moves = _counts(snap)
        photos = sorted(p for p in config.PHOTO_DIR.glob("*") if p.is_file()) if config.PHOTO_DIR.exists() else []
        trash = sorted(p for p in config.TRASH_DIR.glob("*") if p.is_file()) if config.TRASH_DIR.exists() else []
        st = {}
        try:
            st = {k: v for k, v in json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8")).items()
                  if k in _PORTABLE_SETTINGS}
        except Exception:                                # noqa: BLE001 - settings are optional
            pass
        manifest = {"format": FORMAT, "app": "personal-warehouse", "app_version": __version__,
                    "schema": SCHEMA_VERSION, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": items, "movements": moves, "photos": len(photos),
                    "db_sha256": hashlib.sha256(snap.read_bytes()).hexdigest()}
        with zipfile.ZipFile(part, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1))
            z.write(snap, "Database/warehouse.db")
            z.writestr("settings.json", json.dumps(st))
            for p in photos:
                z.write(p, f"Photos/{p.name}", compress_type=zipfile.ZIP_STORED)   # jpg/png do not shrink
            for p in trash:                              # deleted items' photos, so "undo delete" survives a move
                z.write(p, f"Trash/{p.name}", compress_type=zipfile.ZIP_STORED)
        if password:
            encrypt_file(part, dest.with_name(dest.name + ".enc"), password)
            os.replace(dest.with_name(dest.name + ".enc"), dest)
        else:
            os.replace(part, dest)
        return manifest
    finally:
        part.unlink(missing_ok=True)
        dest.with_name(dest.name + ".enc").unlink(missing_ok=True)
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _read_manifest(z):
    try:
        m = json.loads(z.read("manifest.json"))
    except (KeyError, ValueError):
        raise PackageError("not_package") from None
    if m.get("app") != "personal-warehouse" or "Database/warehouse.db" not in z.namelist():
        raise PackageError("not_package")
    return m


def _inspect_zip(zp):
    try:
        z = zipfile.ZipFile(zp)
    except (zipfile.BadZipFile, OSError):
        raise PackageError("not_package") from None
    with z:
        m = _read_manifest(z)
        if int(m.get("schema", 0)) > SCHEMA_VERSION:
            raise PackageError("too_new")                # made by a newer app: refuse instead of corrupting it
        if z.testzip() is not None:
            raise PackageError("damaged")
        tmp = Path(tempfile.mkdtemp(prefix="pw_chk_"))
        try:
            sha = hashlib.sha256()
            with z.open("Database/warehouse.db") as src, open(tmp / "w.db", "wb") as out:
                for block in iter(lambda: src.read(1 << 20), b""):
                    sha.update(block)
                    out.write(block)
            if m.get("db_sha256") and m["db_sha256"] != sha.hexdigest():
                raise PackageError("damaged")
            if not verify_db(tmp / "w.db"):
                raise PackageError("damaged")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return m


def inspect_package(path, password=None):
    """Validate a package without changing anything. Returns its manifest; raises PackageError."""
    with _plain(path, password) as zp:
        return _inspect_zip(zp)


def _safety_copy(tag, source):
    """Save the current data as a package before it is replaced. Returns the path (or None when there is no data)."""
    config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not config.DB_PATH.exists():
        return None
    stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
    safety, n = config.BACKUP_DIR / f"before_{tag}_{stamp}{EXT}", 1
    while safety.exists() or Path(source).resolve() == safety.resolve():   # never overwrite a copy (or the source)
        n += 1
        safety = config.BACKUP_DIR / f"before_{tag}_{stamp}_{n}{EXT}"
    create_package(safety)
    return safety


def _swap_db(staged):
    os.replace(staged, config.DB_PATH)                   # swap the database in one step
    for ext in ("-wal", "-shm"):
        Path(str(config.DB_PATH) + ext).unlink(missing_ok=True)
    init_db()                                            # upgrade an older database to the current schema


def restore_package(path, password=None):
    """Replace the current database + photos with the package. Returns (manifest, safety_copy_path)."""
    with _plain(path, password) as zp:
        manifest = _inspect_zip(zp)
        safety = _safety_copy("restore", path)           # one-click undo: restore this file to go back
        staged = config.DB_PATH.with_name("warehouse.restoring")
        st = {}
        try:
            with zipfile.ZipFile(zp) as z:
                with z.open("Database/warehouse.db") as src, open(staged, "wb") as out:
                    shutil.copyfileobj(src, out)
                for prefix, folder in (("Photos/", config.PHOTO_DIR), ("Trash/", config.TRASH_DIR)):
                    folder.mkdir(parents=True, exist_ok=True)
                    for info in z.infolist():
                        if not info.filename.startswith(prefix) or info.is_dir():
                            continue
                        base = Path(info.filename).name  # flatten: never write outside the target folder
                        if base and base not in (".", ".."):
                            with z.open(info) as src, open(folder / base, "wb") as out:
                                shutil.copyfileobj(src, out)
                try:
                    st = json.loads(z.read("settings.json"))
                except (KeyError, ValueError):
                    pass
            _swap_db(staged)
        finally:
            staged.unlink(missing_ok=True)
    if st:
        from personal_warehouse.settings import save_settings
        save_settings(**{k: v for k, v in st.items() if k in _PORTABLE_SETTINGS})
    return manifest, safety


def restore_db_file(path):
    """Go back to an automatic / safety database copy (``.db``). Photos are left as they are."""
    if not verify_db(path):
        raise PackageError("damaged")
    safety = _safety_copy("restore", path)
    staged = config.DB_PATH.with_name("warehouse.restoring")
    try:
        shutil.copyfile(path, staged)
        _swap_db(staged)
    finally:
        staged.unlink(missing_ok=True)
    return safety


# ------------------------------------------------------------------ restore points and backup health
_KINDS = (("warehouse_", "auto"), ("before_delete_", "delete"), ("before_restore_", "restore"), ("before_v", "upgrade"))


def restore_points(limit=40):
    """Backups found in the Backup folder, newest first: [{name, kind, when, items, size_kb}]."""
    out = []
    for f in list(config.BACKUP_DIR.glob("*.db")) + list(config.BACKUP_DIR.glob(f"*{EXT}")):
        kind = next((k for pre, k in _KINDS if f.name.startswith(pre)), "other")
        items = None
        try:
            if f.suffix == ".db":
                items = _counts(f)[0]
            elif not is_encrypted(f):
                with zipfile.ZipFile(f) as z:
                    items = _read_manifest(z).get("items")
        except Exception:                                # noqa: BLE001 - listing must never fail
            pass
        st = f.stat()
        out.append({"name": f.name, "kind": kind, "items": items, "size_kb": max(1, st.st_size // 1024),
                    "when": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"), "_t": st.st_mtime})
    out.sort(key=lambda r: r["_t"], reverse=True)
    for r in out:
        r.pop("_t")
    return out[:limit]


def backup_status(settings):
    """3-2-1 check: a recent local backup, plus a copy that has left this computer (sync folder or exported file)."""
    from personal_warehouse.config import OFFSITE_WARN_DAYS

    def parse(v):
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M")
        except (TypeError, ValueError):
            return None
    autos = sorted(config.BACKUP_DIR.glob("warehouse_*.db"))
    last_local = datetime.fromtimestamp(autos[-1].stat().st_mtime) if autos else None
    offsite = [d for d in (parse(settings.get("last_sync")), parse(settings.get("last_export"))) if d]
    last_off = max(offsite) if offsite else None
    age = (datetime.now() - last_off).days if last_off else None
    return {"local": last_local.strftime("%Y-%m-%d %H:%M") if last_local else "",
            "offsite": last_off.strftime("%Y-%m-%d %H:%M") if last_off else "",
            "offsite_ok": age is not None and age <= OFFSITE_WARN_DAYS, "offsite_days": age,
            "local_count": len(autos), "encrypt": crypto_available()}


def sync_to_folder(folder):
    """Write ``MyWarehouse_<date>.pwbak`` into ``folder`` (replacing today's copy), keep the newest few."""
    folder = Path(folder)
    if not folder.is_dir():
        raise PackageError("sync_missing")
    target = folder / f"MyWarehouse_{datetime.now():%Y%m%d}{EXT}"
    manifest = create_package(target)
    for old in sorted(folder.glob(f"MyWarehouse_*{EXT}"))[:-KEEP_SYNC_COPIES]:
        old.unlink(missing_ok=True)
    return target, manifest


def latest_in_folder(folder):
    """Newest package in a synced folder, or None. Handy on a new computer."""
    try:
        found = sorted(Path(folder).glob(f"MyWarehouse_*{EXT}"))
    except OSError:
        return None
    return found[-1] if found else None


def has_data():
    """True when this computer already has at least one item (used to warn before a restore)."""
    try:
        with db() as con:
            return con.execute("SELECT COUNT(*) FROM items").fetchone()[0] > 0
    except Exception:                                    # noqa: BLE001
        return False
