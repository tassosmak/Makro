Makro
Makro is a modular Python framework for building apps with a reusable kernel and a focused set of kits—input, notifications, audio, login, plugins, and optional GUI support. Build a new project by composing proven components, not rebuilding fundamentals.
​

Why Makro
Kernel-first architecture for shared tasks, system calls, and app utilities.
​

Modular kits for input, notifications, audio, and authentication.
​

Plugin-ready design that makes features easy to add, remove, and maintain.
​

Console or GUI workflows, with a path to Toga-based UI where needed.
​

Features
Kernel Core
Centralized task handling and job flow.
​

System-level helpers for OS calls and utilities.
​

Consistent app services shared across projects.
​

Renderer & Highlight Kits
Clean rendering for rich console output (highlighting, progress, live updates).
​

Output designed to stay readable as complexity grows.
​

Input Management
Flexible input handling with multiple backend options (for example, pynput, cross-platform getch, or native alternatives).
​

One input surface for different platforms and devices.
​

Notifications
System notifications, alerts, dialogs, and custom notification types.
​

Clear prompts and predictable messaging for user-facing flows.
​

AudioKit
Simple sound effects and lightweight audio cues.
​

Useful for alerts, feedback, and notification sounds.
​

Login & Security
Authentication workflows with credential handling and optional two-step verification.
​

UI text intended to be concise and unambiguous.
​

Plugins
Extend Makro through modular plugins (utilities, viewers, tools, and more).
​

Keep features isolated without fragmenting the app core.
​

Error Logging
Built-in error handling and logging utilities to capture failures cleanly.
​

Project layout
text
Makro/
├── Boot/                  # Launcher scripts
├── Drivers/               # Driver modules (Input, Notifications, Audio)
├── MakroCore/             # Kernel + core framework modules
├── MakroCore/src/         # Resources and installation scripts
├── Plugins/               # Plugins (examples + utilities)
└── README.md
Key components
MakroCore/KernelReboot.py — Kernel-level reboot operations.
​

MakroCore/TaskHandler.py — Task and job management.
​

MakroCore/SystemCalls.py — OS-level commands and system calls.
​

Drivers/InputManagerKit/ — Input abstraction across backends.
​

Drivers/NotificationsKit/ — Cross-platform notification helpers.
​

Drivers/AudioKit/ — Audio playback utilities.
​

MakroCore/LoginKit/ — Login workflows and two-step verification.
​

Plugins/ — Ready-to-use modules for extending the framework.
​

Requirements
Python 3.9+
​

Dependencies listed in requirements.txt
​

Install
bash
git clone https://github.com/your-username/Makro.git
cd Makro
pip install -r requirements.txt
Note: Some plugins or drivers may require additional system libraries depending on platform.
​

Run
bash
python Boot/launcher.py
Create a plugin
Add a new module in Plugins/ (for example, Plugins/my_plugin.py).
​

Define a main() entry point.
​

Launch Makro—plugins integrate through the kernel.
​
# to add it to your project type: git submodule add https://github.com/tassosmak/Makro.git Makro
