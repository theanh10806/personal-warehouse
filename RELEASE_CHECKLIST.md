# Release checklist — Personal Warehouse for Windows

## Before publishing

### Unified release 3.8.0

- Current published versions: GitHub **3.7.0**; Microsoft Store **3.1.0** (reported by owner).
- Target: GitHub tag **v3.8.0**, installer **PersonalWarehouse-Setup-3.8.0.exe**, Store package **PersonalWarehouse-3.8.0.msix**, manifest **3.8.0.0**.
- Update the existing Store product, never create a second product. Upload the paired MSIX from the same build as the GitHub installer.
- Export a full .pwbak from each old installation before testing upgrades. If two installations contain different inventories, preserve both packages; do not overwrite or attempt an automatic merge.
- [ ] Upgrade an isolated copy from Store 3.1.0 to Store 3.8.0.0; compare items, movements, history, photos and settings.
- [ ] Upgrade an isolated copy from GitHub 3.7.0 to EXE 3.8.0; compare the same data.
- [ ] Wait for the Store release to be approved and available before publishing the GitHub 3.8.0 draft.

- [ ] Use one stable `major.minor.patch` for source/tag and `major.minor.patch.0` for Store; update the source manifest together with `__version__`.
- [ ] Build once with `packaging\build.ps1 -RequireBothPackages`: EXE and MSIX must come from the same `dist` folder; never rebuild one channel separately.
- [ ] Download the paired packages from the same Actions artifact. Keep GitHub Release as draft while submitting the MSIX to Partner Center.
- [ ] After Store approval and verification, publish the matching GitHub draft. Store approval timing means exact simultaneous availability cannot be guaranteed.
- [ ] Test installing both channels under the same Windows account: same selected data folder, cross-channel single-instance lock, upgrade/downgrade refusal, and `.pwbak` restore. Verify Store removal leaves the shared data intact.
- [ ] Version guard (`installed_version.txt`): with 3.8.0 run once, open Store/EXE 3.1.0 or 3.7.0 → "newer version" message and no start; run the old Setup.exe → refused; delete the file → old copy starts again.
- [ ] Store identity Name/Publisher and Inno Setup AppId must remain unchanged. Store updates must never launch the GitHub EXE installer.

- [ ] Create the public repository `theanh10806/personal-warehouse`; `GITHUB_REPO` is already set to `theanh10806/personal-warehouse`.
- [ ] Confirm `__version__` matches the release tag (for example, `3.0.0` and `v3.0.0`).
- [ ] Add release notes under the matching heading in `CHANGELOG.md`.
- [ ] Run `python -m pytest -q` and confirm all tests pass.
- [ ] Run `node --check src/personal_warehouse/webui/static/app.js` and `node --test tests/map_ui.test.cjs`.
- [ ] Verify history newest-first ordering, same-second IDs, targeted confirmations, Undo/Redo, and refusal to overwrite newer changes using an isolated demo warehouse.
- [ ] Test fast navigation between pages while data is loading; verify no JavaScript exceptions.
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
