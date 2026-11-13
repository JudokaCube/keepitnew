#!/usr/bin/env python3
from pathlib import Path
import shutil,tarfile
root=Path(__file__).resolve().parent
release=root/'release'
if release.exists():shutil.rmtree(release)
release.mkdir()
for name in ('bin','plugins','services','integrations'):shutil.copytree(root/name,release/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for path in (root/'packaging').iterdir():
    if path.is_file():shutil.copy2(path,release/path.name)
shutil.copy2(root/'LICENSE',release/'LICENSE')
(release/'README.md').write_text('# KeepItNew\n\nUpdate Arch, AUR and Flatpak packages, clean up disk space, and track updates from your desktop bar.\n\n## Features\n\n- Arch, AUR and Flatpak update counts, scheduled checks and one update workflow.\n- Disk-space checks, reboot recommendations, and cleanup presets with selectable categories.\n- Nine themes, optional transparency, square border styles and configurable widgets.\n\n## Installation\n\nRequires Linux, Python 3.11+, Kitty and systemd. Updates require Arch/pacman and checkupdates or fakeroot; yay/paru adds AUR, and Flatpak support is optional.\n\nFrom the installer folder, run as your normal desktop user:\n\n```sh\nbash install.sh\n```\n\nThis installer includes only KeepItNew and its widgets. Choose a bar, theme and background-service options during setup. Existing app data is preserved. Open a new terminal to use newly enabled aliases.\n\n## Usage\n\nRun `keepitnew` to open its own desktop window; **Q** closes it. Use `keepitnew --overview` to run inside your current terminal instead. Without a desktop or Kitty, it stays in the current terminal. Local installs also provide `system-update` and the optional `update` alias. Select actions with arrows/Enter or the mouse. In **Free disk space**, choose a preset, toggle categories with Space or clicks, then select **Clean**. Unavailable tools are disabled.\n\n## Settings\n\nChoose **Settings** from the main menu. Use arrows for quick adjustments; Enter or a click opens choices. **Save / Ctrl+S** applies changes; **Esc** discards unsaved changes.\n\n- KeepItNew: AUR and Flatpak source toggles, preferred AUR helper, cached package versions, automatic checks, confirmations, reboot hints and cleanup presets.\n- Appearance: theme, opacity, borders, widget visibility and text. Noctalia also supports animation controls.\n\nSave applies opacity immediately in app-launched Kitty windows. Older windows need one relaunch from the widget or launcher. Other terminals control their own transparency. Widget changes appear after a short delay.\n\n## Desktop bars\n\n- **Noctalia 5.3+**: native widgets with hover details.\n- **Waybar**: custom modules and tooltips. Restart Waybar after installation.\n- **Caelestia**: requires a writable shell checkout using `--caelestia-root`. Restart the shell after installation.\n- **No bar**: use the apps and optional background services on their own.\n\nRight-click a widget to reload and open its app.\n\n## License\n\nMIT · jdkcube\n')
with tarfile.open(root/'release.tar.gz','w:gz') as out:
    for path in release.rglob('*'):
        if path.is_file():
            info=out.gettarinfo(str(path),str(Path('release')/path.relative_to(release)))
            info.uid=info.gid=0;info.uname=info.gname=''
            with path.open('rb') as f:out.addfile(info,f)
print('Created release/ and release.tar.gz')
