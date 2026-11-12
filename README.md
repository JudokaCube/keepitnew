# KeepItNew

Update Arch, AUR and Flatpak packages, clean up disk space, and track updates from your desktop bar.

## Features

- Arch, AUR and Flatpak update counts, scheduled checks and one update workflow.
- Disk-space checks, reboot recommendations, and cleanup presets with selectable categories.
- Nine themes, optional transparency, square border styles and configurable widgets.

## Installation

Requires Linux, Python 3.11+, Kitty and systemd. Updates require Arch/pacman and checkupdates or fakeroot; yay/paru adds AUR, and Flatpak support is optional.

Download the installer archive from [GitHub Releases](https://github.com/JudokaCube/keepitnew/releases/latest) and extract it.

From the installer folder, run as your normal desktop user:

```sh
bash install.sh
```

This installer includes only KeepItNew and its widgets. Choose a bar, theme and background-service options during setup. Existing app data is preserved. Open a new terminal to use newly enabled aliases.

## Usage

Run `keepitnew`. Local installs also provide `system-update` and the optional `update` alias. Select actions with arrows/Enter or the mouse. In **Free disk space**, choose a preset, toggle categories with Space or clicks, then select **Clean**. Unavailable tools are disabled.

## Settings

Choose **Settings** from the main menu. Use arrows for quick adjustments; Enter or a click opens choices. **Save / Ctrl+S** applies changes; **Esc** discards unsaved changes.

- KeepItNew: AUR and Flatpak source toggles, preferred AUR helper, cached package versions, automatic checks, confirmations, reboot hints and cleanup presets.
- Appearance: theme, opacity, borders, widget visibility and text. Noctalia also supports animation controls.

Reopen the app after changing opacity. Widget changes appear after a short delay.

## Desktop bars

- **Noctalia 5.3+**: native widgets with hover details.
- **Waybar**: custom modules and tooltips. Restart Waybar after installation.
- **Caelestia**: requires a writable shell checkout using `--caelestia-root`. Restart the shell after installation.
- **No bar**: use the apps and optional background services on their own.

Right-click a widget to reload and open its app.

## License

MIT · jdkcube
