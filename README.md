# Bazzite Buddy

A [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) plugin for [Bazzite](https://bazzite.gg) that surfaces release notes and a **Restart to Windows** action directly in the Steam Quick Access Menu (QAM).

---

## Features

- **Bazzite Release Notes** — fetches and renders the latest changelog from GitHub inside the QAM panel with full GFM (tables, code blocks, lists) support.
- **Refresh** — reload the changelog on demand without leaving Gaming Mode.
- **View All Release Notes** — opens the Bazzite GitHub releases page.
- **Restart to Windows** *(dual-boot only)* — sets the one-time EFI boot target to `Windows Boot Manager` and reboots. The action is hidden automatically when no Windows EFI entry is detected.

---

## System prerequisites

### 1. Bazzite

| Requirement | Details |
|---|---|
| OS | [Bazzite](https://bazzite.gg) (image-based, Fedora Atomic) |
| Edition | Any edition — handheld (deck), desktop, or HTPC |
| Internet | Required to fetch changelogs from `github.com` |

### 2. Decky Loader

| Requirement | Version |
|---|---|
| Decky Loader | ≥ `v3.2.8` |

> **Why v3.2.8?** Earlier builds have a QAM rendering regression (Decky issue [#948](https://github.com/SteamDeckHomebrew/decky-loader/issues/948)) that causes the QAM tab to disappear after Steam reinitializes. Update Decky from its own **Settings → Updates** tab, or reinstall:
> ```sh
> # Desktop Mode terminal
> curl -L https://github.com/SteamDeckHomebrew/decky-installer/releases/latest/download/install_release.sh | sh
> ```

### 3. Dual-boot prerequisites *(Restart to Windows only)*

The **Restart to Windows** action appears automatically when a `Windows Boot Manager` EFI entry is present. No separate configuration is needed — the plugin reads `efibootmgr` directly and the action is hidden if Windows is not detected.

| Requirement | Details |
|---|---|
| Windows installation | A working Windows install with an EFI entry labelled exactly **`Windows Boot Manager`** |
| `efibootmgr` | Included in Bazzite by default |
| Decky root flag | Plugin runs with the `_root` flag — required for `efibootmgr` access |

> **Note:** The plugin calls `efibootmgr -n <boot-number>` to arm Windows as a one-time boot target, then `systemctl --no-block reboot`. If the reboot step fails, the plugin clears `BootNext` to avoid leaving a stale entry.

---

## Installation

### From the Decky Plugin Store *(recommended)*

Search for **"Bazzite Buddy"** in the Decky Store tab in Gaming Mode.

### Manual / sideload install

1. Download the latest `bazzite-buddy.zip` from the [Releases](https://github.com/xXJSONDeruloXx/bazzite-buddy/releases) page.
2. In Gaming Mode open Decky → **Settings → Developer → Install Plugin from ZIP**.
3. Select the downloaded file.

> Alternatively, from a Desktop Mode terminal:
> ```sh
> # Adjust the version tag as needed
> curl -L https://github.com/xXJSONDeruloXx/bazzite-buddy/releases/latest/download/bazzite-buddy.zip \
>   -o /tmp/bazzite-buddy.zip
> unzip /tmp/bazzite-buddy.zip -d ~/.local/share/decky-loader/plugins/bazzite-buddy
> # Restart Decky from its Settings tab
> ```

---

## How Restart to Windows works

1. On load the frontend calls `get_windows_boot_target` — the backend runs `efibootmgr` and parses its output for an entry labelled `Windows Boot Manager`.
2. If no entry is found the **Power** section is hidden entirely.
3. When the user presses **Restart**, a confirmation modal appears ("This will close your current session and use Windows for the next boot only.").
4. On confirm, the backend re-detects the Windows EFI number (guarding against a stale QAM view), then calls `efibootmgr -n <boot-number>`.
5. On success the backend calls `systemctl --no-block reboot`. If the reboot command fails, `efibootmgr -N` is called immediately to clear `BootNext`.
6. A toast notification is shown on any failure with the exact error from `efibootmgr` or `systemctl`.

---

## Development

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | ≥ 18 LTS | [nodejs.org](https://nodejs.org) |
| pnpm | ≥ 9 | `npm install -g pnpm` |
| Python | ≥ 3.11 | [python.org](https://python.org) |
| TypeScript | via pnpm | installed by `pnpm install` |

### Setup

```sh
git clone https://github.com/xXJSONDeruloXx/bazzite-buddy.git
cd bazzite-buddy
pnpm install
```

### Running tests

```sh
# All tests: Python backend + JS release-preview + TypeScript type-check
pnpm test

# Python backend tests only
python3 -m unittest discover -s tests -v

# JS release-preview tests only
node --test tests/release_preview.test.mjs

# TypeScript type-check only
npx tsc --noEmit
```

### Building

```sh
pnpm build
# Output: dist/index.js
```

### Watch mode

```sh
pnpm watch
```

### Deploying to a Bazzite device for live testing

Using the [Decky CLI](https://github.com/SteamDeckHomebrew/decky-cli):

```sh
# Install Decky CLI once (gitignored)
curl -L https://github.com/SteamDeckHomebrew/decky-cli/releases/latest/download/decky -o cli/decky
chmod +x cli/decky

# Deploy over SSH (replace with your device hostname or IP)
cli/decky plugin deploy -h nilesh@steamos.local
```

---

## Repository structure

```
bazzite-buddy/
├── main.py                         # Python backend — EFI detection, reboot logic
├── plugin.json                     # Decky plugin manifest
├── src/
│   ├── index.tsx                   # React frontend — QAM panel, Power section, changelog viewer
│   ├── releasePreview.js           # Release note pre-processing (strips noise)
│   ├── PartnerEventStorePatch.tsx  # Steam PartnerEventStore patch for changelog fetch
│   └── types.d.ts                  # TypeScript ambient declarations
├── tests/
│   ├── test_main.py                # Python unit tests (EFI parsing, reboot flow, error cases)
│   ├── test_release_notes_styles.py# Python tests for release note formatting
│   └── release_preview.test.mjs   # Node.js tests for release preview logic
├── assets/                         # Plugin artwork / icons
├── package.json                    # Node dependencies and build scripts
├── rollup.config.js                # Frontend bundler config
├── tsconfig.json                   # TypeScript compiler config
└── justfile                        # Optional Just task runner shortcuts
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| **Restart to Windows** button not visible | No `Windows Boot Manager` EFI entry found | Verify Windows is installed and EFI; run `efibootmgr` in a terminal and check for the entry |
| Restart fails with "permission denied" | Plugin not running with root flag | Ensure `plugin.json` contains `"_root"` in flags; reinstall the plugin |
| Restart fails with "EFI variables not supported" | Bazzite not booted in UEFI mode | Check BIOS — CSM / legacy boot mode disables EFI variable access |
| `BootNext` left set after failed reboot | `clear_boot_next()` also failed | Run `efibootmgr -N` manually in a terminal to clear it |
| Changelog shows spinner indefinitely | Network unreachable from Gaming Mode | Check Wi-Fi connection; tap **Refresh** after reconnecting |
| QAM tab disappears after Steam restarts | Decky Loader < v3.2.8 regression | Update Decky to ≥ v3.2.8 via Decky Settings → Updates |

---

## Contributing

PRs are welcome against the [upstream repository](https://github.com/xXJSONDeruloXx/bazzite-buddy). Please run `pnpm test` before submitting.

## License

[BSD 3-Clause](./LICENSE)
