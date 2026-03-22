<div align="center">

# 🔋 Battery Alarm

**Charge smart. Battery lasts longer.**

![Windows 11 Ready](https://img.shields.io/badge/Windows-11_Ready-0078D4?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/PyQt6-UI-41CD52?style=for-the-badge&logo=qt)
![License](https://img.shields.io/badge/License-GNU_GPLv3-blue?style=for-the-badge)

*A lightweight, modern Windows desktop application that protects your laptop's battery lifespan by alerting you before it overcharges.*

</div>

<br />

## ✨ Why Battery Alarm?

Modern lithium-ion batteries degrade faster when constantly charged to 100%. **Battery Alarm** is built on one simple premise: **unplug before you hit the limit.** 

Set your target percentage (e.g., 80%), and the app gracefully monitors your charging state in the background. Once the target is reached, an alarm will gently remind you to unplug your charger—automagically silencing itself the moment you do!

---

## ⚡ Key Features

*   🎯 **Customisable Threshold:** Fine-tune your target percentage from `50%` to `100%`.
*   🛑 **Smart Auto-Stop:** Unplug your charger, and the alarm instantly turns off. No buttons needed.
*   🖼️ **Mini Desktop Widget:** Keep an eye on your battery with a stunning, always-on-bottom transparent widget that sits seamlessly on your desktop.
*   🚀 **Run on Startup:** Zero friction. Enable startup to have Battery Alarm silently protect your battery from the moment you boot your PC.
*   🌗 **Modern Dark Mode UI:** Built specifically to match the gorgeous aesthetics of Windows 11 with soft shadows, rounded corners, and smooth typography.
*   🔔 **Snooze & Stop:** Need 5 more minutes? Hit snooze. Can't unplug right now? Just stop the alarm until the next charging cycle.
*   💾 **Set It and Forget It:** All your preferences—including startup settings and target percentage—are saved automatically.
*   Tray Integration: Minimises to the system tray so it never clutters your taskbar. 

---

## 🚀 Getting Started (End Users)

You don't need Python or any programming knowledge to run Battery Alarm! 

1. **Download the App:** Find the standalone `BatteryAlarm.exe` file in the main folder.
2. **Double Click to Run:** Launch the `.exe`. 
3. **That's it!** The app will automatically create a handy desktop shortcut for you the first time it opens.

---

## 💻 For Developers

Want to hack on Battery Alarm? It's built with Python `3.11+` and `PyQt6`.

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/battery-alarm.git
cd "battery alarm pc python"

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Assets

If this is your first time compiling the source code, generate the local icon and audio assets:

```bash
python generate_alarm.py
python generate_icon.py
```

### 3. Run from Source

```bash
python main.py
```

### 4. Build Standalone Executable

To compile your own `BatteryAlarm.exe` without revealing the source code:

```bash
pip install pyinstaller

pyinstaller --noconfirm --onefile --windowed ^
    --name "BatteryAlarm" ^
    --add-data "assets;assets" ^
    main.py
```

The compiled binary will be placed inside the `dist/` folder.

---

## ⌨️ Shortcuts & Controls

| Action | How to do it |
| :--- | :--- |
| **Close Window** | Click the `X` (Minimises to tray silently) |
| **Open App** | Single-click the Desktop Widget, or double-click the tray icon |
| **Toggle Widget** | Right-click tray icon → `Show/Hide Widget` |
| **Quick Exit** | Right-click tray icon → `Exit` |

---

## 📜 License

This project is licensed under the **GNU General Public License v3.0**. Feel free to fork, modify, and use it in your own projects!
