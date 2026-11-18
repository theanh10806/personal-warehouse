# Release checklist — Personal Warehouse for Windows

## Before publishing

- [ ] Create the public repository `theanh10806/personal-warehouse`; `GITHUB_REPO` is already set to `theanh10806/personal-warehouse`.
- [ ] Confirm `__version__` matches the release tag (for example, `3.0.0` and `v3.0.0`).
- [ ] Add release notes under the matching heading in `CHANGELOG.md`.
- [ ] Run `python -m pytest -q` and confirm all tests pass.
- [ ] Build on Windows with Python 3.12 x64 using `powershell -ExecutionPolicy Bypass -File packaging\build.ps1`.
- [ ] Confirm both `dist\PersonalWarehouse\PersonalWarehouse.exe` and `Output\PersonalWarehouse-Setup-x.y.z.exe` exist.

## Test the installer on a clean Windows account or VM

- [ ] Install without administrator privileges.
- [ ] Launch from the Start menu and desktop shortcut.
- [ ] Create a test item; test stock-in, stock-out, and adjustment.
- [ ] Close and reopen the app; verify the data persists.
- [ ] Export CSV and Excel; generate and print a QR/barcode label.
- [ ] Test USB barcode scanning. Test camera scanning only on a machine with a working camera and supported drivers.
- [ ] Create a backup, restore it, and verify the restored inventory.
- [ ] Install a newer version over the old version; verify existing data remains.
- [ ] Uninstall; verify user data in `Documents\MyWarehouse` remains intact.
- [ ] Verify update-check behavior after publishing a GitHub Release.

## Publish through GitHub Actions

1. Push the source to the `main` branch.
2. In GitHub, set **Settings → Actions → General → Workflow permissions** to **Read and write permissions**.
3. Ensure the `GITHUB_REPO` value exactly matches the repository owner/name.
4. Push a version tag matching `__version__`, for example:

   ```powershell
   git tag v3.0.0
   git push origin main --tags
   ```

5. Wait for the **Release** workflow to pass, then download the installer from GitHub Releases and test it before sharing it with users.

## Release safety

- Keep the `AppId` in `packaging\installer.iss` unchanged across upgrades.
- Keep user data outside the installation directory (`Documents\MyWarehouse`).
- Never publish a release until the installer has been tested on a clean Windows environment.
