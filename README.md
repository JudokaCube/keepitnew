# KeepItNew

Customizable terminal app and desktop widget. MIT licensed. Public releases start without personal data.

## Install

Requires Linux, Python 3.11+, Kitty and systemd. Updates require Arch/pacman, Flatpak and checkupdates or fakeroot; yay/paru adds AUR.

```sh
python3 build-release.py
bash release/install.sh
```

For a downloaded installer, run `bash install.sh`. Setup offers theme, opacity, bar, position, aliases, check interval and package confirmations. Existing data is preserved; no keybindings are added. `--help` lists flags; `--yes` uses defaults/flags without questions.

## Bars

- Noctalia 5.3+: native plugins, enabled automatically.
- Waybar: native custom modules; existing JSON/JSONC values are preserved, formatting/comments are rewritten. Restart Waybar after installation.
- Caelestia: requires an editable shell checkout via `--caelestia-root`; setup adds the supplied QML widget to its bar. Restart that shell afterward. System-owned files are not changed.
- None: apps and optional background services only.

Right-click opens fresh app code. Widget styles follow the shared theme. Waybar uses tooltips for hover details; Caelestia uses a tooltip and progress strip. Shell-native notification alignment remains controlled by the shell.

## KeepItNew

Run `update` or `python3 bin/system-update`. Arrows/Enter or clicks select actions. Cleanup has presets and checkboxes; space/click toggles, clean runs checked categories. Missing tools are disabled. Disk checks are minimum reserves, not exact size estimates. Reboot hints never reboot automatically.

## Appearance and development

Open theme/appearance for nine palettes. Arrows preview, Enter/click saves, Esc cancels, n resets Nord. Opacity defaults to 94%. Reopen windows after code or launch-setting changes. Settings respect XDG directories; runtime data stays outside the source tree.

`bin/` apps, `plugins/` Noctalia widgets, `integrations/` other bars, `services/` startup, `packaging/` installer.

```sh
noctalia plugins lint plugins/*
python3 build-release.py
```

Rebuild after edits. Upload this source folder, including `.gitignore`, and attach `release.tar.gz` to releases. Files starting `PRIVATE-` are personal copies, not public releases.
