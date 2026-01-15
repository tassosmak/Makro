# Makro

Makro is a modular Python framework for building apps with a reusable kernel and a focused set of kits—input, notifications, audio, login, plugins, and optional GUI support.   
Build new projects by composing proven components, not rebuilding fundamentals. 

## Why Makro

- **Kernel-first** architecture for shared tasks, system calls, and app utilities. 
- **Modular kits** for input, notifications, audio, and authentication. 
- **Plugin-ready** design that makes features easy to add, remove, and maintain. 
- **Console or GUI** workflows, with a path to Toga-based UI where needed. 

## Deployment

### Use It Yourself
- to add it to your project you can use the command : git submodule add https://github.com/tassosmak/Makro.git Makro


## Features

### Kernel Core
- Centralized task handling and job flow. 
- System-level helpers for OS calls and utilities. 
- Consistent app services shared across projects. 

### Renderer & Highlight Kits
- Clean rendering for rich output (highlighting, progress, live updates). 
- Output designed to stay readable as complexity grows. 

### Input Management
- Flexible input handling with multiple backend options
- One input surface for different platforms and devices. 

### Notifications
- System notifications, alerts, dialogs, and custom notification types. 
- Clear prompts and predictable messaging for user-facing flows. 

### AudioKit
- Simple sound effects and lightweight audio cues. 
- Useful for alerts and feedback. 

### Login & Security
- Authentication workflows with credential handling and optional two-step verification. 
- Keep copy concise and unambiguous. 

### Plugins
- Extend Makro through modular plugins (utilities, viewers, tools, and more). 
- Keep features isolated without fragmenting the app core. 

### Error Logging
- Built-in error handling and logging utilities to capture failures cleanly.

## Project layout

```text
Makro/
├── Boot/                  # Launcher scripts
├── Drivers/               # Driver modules (Input, Notifications, Audio)
├── MakroCore/             # Kernel + core framework modules
├── MakroCore/src/         # Resources and installation scripts
├── Plugins/               # Plugins (examples + utilities)
└── README.md


