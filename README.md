# KeepItNew

Update Arch, AUR and Flatpak packages, clean up disk space, and track updates from your desktop bar.

## Features

- Arch, AUR and Flatpak update counts, scheduled checks and one update workflow.
- Disk-space checks, reboot recommendations, and cleanup presets with selectable categories.
- Nine themes, optional transparency, square border styles and configurable widgets.

## Installation

Requires Linux, Python 3.11+, Kitty and systemd. Updates require Arch/pacman and checkupdates or fakeroot; yay/paru adds AUR, and Flatpak support is optional.

Download the installer from [GitHub Releases](https://github.com/JudokaCube/keepitnew/releases/latest), extract it, and run `bash install.sh`. The installer starts with no personal data.

From the source folder:

```sh
python3 build-release.py
bash release/install.sh
```

For an extracted installer archive, run `bash install.sh` instead.

This installer includes only KeepItNew and its widgets. Choose a bar, theme and background-service options during setup. Existing app data is preserved. Open a new terminal to use newly enabled aliases.

## Usage

Run `keepitnew`. Local installs also provide `system-update` and the optional `update` alias. Select actions with arrows/Enter or the mouse. In **Free disk space**, choose a preset, toggle categories with Space or clicks, then select **Clean**. Unavailable tools are disabled.

## Settings

Choose **Settings** from the main menu. Use arrows for quick adjustments; Enter or a click opens choices. Theme colors and square borders preview in Settings while preserving terminal transparency. **Save / Ctrl+S** applies changes; **Esc** discards unsaved changes. **Defaults** selects the default values; Save applies them.

- KeepItNew: AUR and Flatpak source toggles, preferred AUR helper, cached package versions, automatic checks, confirmations, reboot hints and cleanup presets.
- Appearance: theme, opacity, borders, widget visibility and text. Noctalia also supports animation controls.

Widget settings take effect on the next poll. Opacity applies to newly launched windows. Settings belong only to this app.

## Desktop bars

- **Noctalia 5.3+**: native widgets with hover details.
- **Waybar**: custom modules and tooltips. Restart Waybar after installation. JSONC values are preserved; formatting and comments are rewritten.
- **Caelestia**: requires a writable shell checkout using `--caelestia-root`. The installer adds a QML component; restart the shell afterward. This integration has syntax/integration checks but has not been visually tested in a running Caelestia session.
- **No bar**: use the apps and optional background services on their own.

Right-click a widget to reload and open its app.

## Arch packaging

Separate Arch package builds are available through `build-arch.py`. See [Arch packaging](packaging/aur/README.md) for local builds and future AUR release preparation. AUR submission is pending; the release source can already be built locally with `makepkg`.

## License

MIT · jdkcube
