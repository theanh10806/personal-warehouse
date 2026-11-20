from pathlib import Path
import xml.etree.ElementTree as ET

from personal_warehouse import __version__


def test_store_manifest_matches_source_version_and_keeps_identity():
    root = Path(__file__).resolve().parents[1]
    manifest = ET.parse(root / "packaging/AppxManifest.xml").getroot()
    identity = manifest.find("{http://schemas.microsoft.com/appx/manifest/foundation/windows10}Identity")
    assert identity.attrib["Version"] == __version__ + ".0"
    assert identity.attrib["Name"] == "Shinnosuke.ShinWarehouseManagement"
    assert identity.attrib["Publisher"] == "CN=08A55B90-7F96-4488-8586-F75F7BCC7746"


def test_store_identity_prevents_exe_updates_outside_windowsapps(monkeypatch):
    import ctypes
    from types import SimpleNamespace
    from personal_warehouse import updater
    class PackageFunction:
        def __call__(self, *args):
            return 122
    monkeypatch.setattr(updater.sys, "platform", "win32")
    monkeypatch.setattr(updater.sys, "executable", r"C:\CustomInstall\PersonalWarehouse.exe")
    monkeypatch.setattr(ctypes, "windll", SimpleNamespace(kernel32=SimpleNamespace(GetCurrentPackageFullName=PackageFunction())), raising=False)
    assert updater.is_store_package()
    assert not updater.can_self_update()
