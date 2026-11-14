# Install and activate

Download **[deep-reef-screensaver.zip](https://github.com/christopher-weaver/roku-fish/raw/refs/heads/main/dist/deep-reef-screensaver.zip)** to your computer first. This link downloads the installable ZIP itself; do not use GitHub’s **Code → Download ZIP**, which downloads the source repository. Leave the installation ZIP compressed.

1. On the Roku remote press **Home three times, Up twice, Right, Left, Right, Left, Right**.
2. Enable the **Developer Application Installer**, accept the developer agreement, configure a development password, and allow the Roku to reboot.
3. Find the Roku's IP address on the developer setup screen or **Settings → Network → About**. The computer and Roku must be able to reach each other on the local network.
4. Open `http://ROKU_IP` in a browser. Authenticate with username **rokudev** and the configured development password.
5. Upload **`dist/deep-reef-screensaver.zip`** and select **Install**. Upload the ZIP itself; do not extract it first. Inspect the installer result for compilation errors.
6. On the TV open **Settings → Theme → Screensavers**. Locate **Deep Reef** (some Roku OS versions show the developer entry as **dev**).
7. Choose **Set as screensaver**, then **Preview**. Set the screensaver wait time and let the device idle to check automatic activation.
8. Use **Change screensaver settings** to configure the aquarium. Pressing a remote button during the aquarium returns to the previous Roku screen; the aquarium has no interactive controls.

Only one sideloaded developer application can be installed at a time. Installing Deep Reef replaces the previous one. A pure screensaver is selected through settings and does not need to appear as an ordinary launchable Home-screen channel.

## Command-line deployment

Build first with `python tools/build.py`. Set the following environment variables in your shell, then invoke `python tools/deploy.py`.

macOS/Linux:

```sh
export ROKU_IP=192.168.1.50
export ROKU_DEV_PASSWORD='your-development-password'
python tools/deploy.py
```

Windows PowerShell:

```powershell
$env:ROKU_IP = '192.168.1.50'
$env:ROKU_DEV_PASSWORD = 'your-development-password'
python tools/deploy.py
```

Exit any running preview on the TV before updating. The helper uses the installer's HTTP Digest authentication, checks for a success response, and does not launch a normal channel. It does not auto-discover devices or attempt deployment without both variables.

## Troubleshooting

- **Installer unreachable:** verify the IP, local network, developer-mode activation and any guest Wi-Fi isolation.
- **Authentication fails:** username is `rokudev`; passwords are case-sensitive. This is the developer password, not the Roku account password.
- **Invalid package:** run `python tools/build.py`; `manifest` must be at ZIP root. Do not ZIP the containing project folder.
- **Screensaver missing:** reinstall the release ZIP, check the developer entry named `dev`, and verify `screensaver_title=Deep Reef`. The package intentionally has no `Main()`, `RunUserInterface()` or ordinary `title=`. Read compiler output from the installer.
- **Black output or artifacts:** choose **Visual quality → Performance** (720p double-buffered output) in settings, then reactivate. Check the screensaver debugger on TCP **8087**; normal app/settings debug output can use **8085**.
- **Slow output:** enable Show FPS temporarily, try Performance, and leave optional particle settings Low or Off. Report model, OS version and debug output.
- **Settings reset:** reinstallation can reset device registry data. Verify persistence across two activations before reinstalling, then across a device restart.
- **Preview seems locked after update:** dismiss the active screensaver, return to settings and preview again. Reboot the Roku if a prior developer app is wedged.

The ZIP is validated locally, but the installation and registration steps have not been exercised on hardware in this environment.

## Updating to 1.0.8

Download a fresh copy of the installation ZIP above. Dismiss the active screensaver, open the Roku Developer Application Installer at `http://ROKU_IP`, upload the ZIP without extracting it and select Install. Then return to **Settings → Theme → Screensavers → Deep Reef (or dev)** and preview it again. Saved preferences are retained. Open **Change screensaver settings**: the complete menu should fit the screen, option names and values should appear above the pink highlight, arrows change the selected option, and **Back** or **Done** closes the menu. For the full slow back-and-forth sweep choose **Camera movement → Slow**. Use **Bubble density → Low** or **Medium** to see the larger bubbles; an existing Off setting remains Off. Auto/High now target 60 fps; Auto settles at 30 fps after sustained missed frames, while Performance starts at 30 fps with 720p output.

Version 1.0.4 removes dappled reef lighting, adds rolling surface waves with synchronized moving sand highlights, and improves fish/bubble/effect smoothness. Exit the active preview before installing the fresh ZIP, then preview again. Use Visual quality → Auto for the 60 fps target and Show FPS temporarily to check actual device output. Performance remains a 30 fps option.

Version 1.0.5 keeps the same pan rate and adds fractional placement, a closer full-width reef, larger/sharper fish, and defined photographic sand ridges with subtle wave-linked light changes. The startup GPU probe selects a supported drawing path automatically; no new setting is required. Install the fresh ZIP and preview again. The diagnostic line `Deep Reef fractional pan=` is available on the screensaver debugger at port 8087.

Version 1.0.6 smooths fish turns with blended views and gentler steering. Eight separate mid-ground reef formations now guide fish routes around and behind the coral. No new setting is required. Dismiss the active preview, upload the fresh ZIP in the same developer installer, choose Install/Replace, and preview Deep Reef again. The debugger also prints `Deep Reef fractional fish=` for the pitched fish placement probe.

Version 1.0.7 fixes upside-down turns and replaces the large-anchor camera path with whole-frame pixel blending. The reef is sparser and layered, with rendered coral perspectives. Dismiss the current preview, install the fresh ZIP, and open Deep Reef again. No new setting is required; Camera movement → Slow retains the four-minute cycle.

Version 1.0.8 removes overlapping fish poses and extra filtering, joins the reef along a common foundation, adds seven-view 3D fan/anemone volumes and recreates matching backgrounds. Exit the current preview, install the fresh ZIP, and preview again. Settings are retained and no new option is required.
