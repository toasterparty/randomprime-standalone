# Randomprime Standalone

Desktop app that applies a [randomprime](https://github.com/randovania/randomprime) patcher JSON (for example, one exported by [Randovania](https://randovania.org/)) to a vanilla Metroid Prime ISO.

- Overrides in-game options (screen, audio, HUD, controls) and cosmetics (map state, Fusion suit, HUD color, suit hue rotations)
- Optional cheats: start with all items, custom starting room, instakill, low gravity
- Verifies the input ISO against known good dumps before patching
- Optionally launches Dolphin with the patched ISO

## Install

Download the build for your OS from [Releases](../../releases). On Windows, just run the exe. On Linux/macOS, mark it executable first (`chmod +x`).

## Development

Requirements: git and GNU make (uv and Python are bootstrapped automatically).

```powershell
winget install --id Git.Git -e --source winget
winget install --id ezwinports.make -e --source winget
```

| Command | Description |
| ------- | ----------- |
| `make run` | Run the app from source |
| `make release` | Build the platform executable into `dist/` |
| `make upgrade` | Upgrade locked dependencies |
| `make clean` | Delete the venv and build outputs |

## Releasing

Run the `Release` workflow from the GitHub Actions tab, choosing a major/minor/patch version bump. It bumps the version, tags the commit, builds Windows/Linux/macOS executables, and publishes a GitHub release with the assets attached.
