# Flowmodoro 🌊

A true flowmodoro timer for the macOS menu bar.

Work freely until you decide to stop. Your break is earned proportionally:
`break = focus_time / 5`. No presets. No interruptions.

---

## How it works

| State         | Menu bar shows | What you can do              |
|---------------|---------------|------------------------------|
| Idle          | `🌊 Flow`     | Start Focus                  |
| Focus         | `⏸ 23:14`     | Pause, Stop & Take Break     |
| Focus (paused)| `▶ 23:14`     | Resume, Stop & Take Break    |
| Break         | `☕ 04:38`     | Skip Break                   |

- Focus for **50 minutes** → earn a **10-minute** break
- Focus for **25 minutes** → earn a **5-minute** break
- Sessions under **30 seconds** prompt you to continue focusing or take a short break

---

## Install

### Prerequisites

- macOS 10.14+
- Python 3.8+

### 1. Install dependencies

```bash
cd flowmodoro
pip install -r requirements.txt
```

### 2. Build and install

```bash
bash build_app.sh
open /Applications/Flowmodoro.app
```

A `🌊 Flow` icon will appear in your menu bar. Click it to get started.

To launch on startup, add it to **Login Items** in System Settings →
General → Login Items.

> **Note on notifications:** For pop-up notifications, go to
> System Settings → Notifications → Flowmodoro and set the style to **Alerts**.
> The default (Banners) only shows briefly in the notification center.

---

## Files

```
flowmodoro/
├── flowmodoro.py      # main app
├── requirements.txt   # runtime dependencies
├── setup.py           # py2app packaging config
├── build_app.sh       # builds a standalone .app bundle
├── Flowmodoro.icns    # app icon
└── README.md
```
