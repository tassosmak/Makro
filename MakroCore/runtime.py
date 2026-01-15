from Makro.MakroCore.JSONhander import JSONhandle
import logging
from pathlib import Path
import inspect


class KernelRuntime:
    def __init__(self, user=None):
        # Setup logging
        logging.basicConfig(
            filename=f'{self.get_folder()}/src/MakroCore_RuntimeLogs.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Initialize kernel state
        self.state = {
            # FILE BASED STATES
            "username": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('user_credentials', 'Name'),
            "password": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('user_credentials', 'Password'),
            "mode": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('user_credentials', 'Mode'),
            "Serial": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('user_credentials', 'Serial'),
            "FTU": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('FTU', 'Use'),
            "IntSoft": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('Internal-Software', 'Enable'),
            "enable_gui": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('UI', 'Enable-AquaUI'),
            "enable_audio": JSONhandle(f'{self.get_folder()}/users/{user}.json').read_file('UI', 'Enable-Audio'),

            # INTERNAL STATES
            "UserLess_Connection": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'UserLess Connection'),
            "Run-Threads Inside": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'Run-Threads Inside'),
            "Run_Straight_Builtin": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'Run-Straight-Builtin'),
            "GO TO FTU": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'GO TO FTU'),
            "Fully_GUI": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'Fully GUI'),
            "Create_Graphs": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'Create_Graph'),
            "Runtime_Tracer": JSONhandle(f'{self.get_folder()}/../../MakroPropiatery.json').read_file('user_login', 'Runtime_Tracer'),

            # PERMANENT STATES
            "BuildReseted": False,
            "base_folder": str,
            "sys_detect": str,
            "safe_md": False,
            "newuser": bool,
            "logout": bool,
            "LCommand": str,
            "Module": bool,
            "jump": False,
            "net": True,
            "pl": '',
        }

        self.trusted_modules = set()
        self.plugin_rights = {
            "plugin:theme_manager": ["enable_gui"],
            "plugin:music_player": ["enable_audio"],
        }

    # ---------------- Public API ----------------
    def get_state(self, key):
        """
        Return a state value. If a global kernel exists, delegate to it.
        Automatically heals if called outside the active kernel.
        """
        try:
            # Lazy import prevents circular import
            from Makro.MakroCore import runtimebridge
            kernel = runtimebridge.get_kernel()
            if kernel is not self:
                return kernel.state.get(key)
        except RuntimeError:
            pass
        except ImportError:
            pass

        return self.state.get(key)

    def request_change(self, key, value):
        """
        Request a state change. If a global kernel exists, forward the request.
        """
        try:
            from Makro.MakroCore import runtimebridge
            kernel = runtimebridge.get_kernel()
            if kernel is not self:
                return kernel._process_request(key, value, "auto-forward")
        except RuntimeError:
            pass
        except ImportError:
            pass

        source = self._detect_source()
        return self._process_request(key, value, source)

    def get_folder(self, inside=False):
        """
        Return the kernel base folder. Optionally updates the internal state.
        """
        folder = Path(__file__).parent.resolve()
        if inside:
            self.request_change('base_folder', folder)
        return folder

    # ---------------- Internals ----------------
    def _process_request(self, key, value, source):
        if key not in self.state:
            return self._deny(source, f"Unknown key '{key}'")

        # Automatically trust all core modules
        if source.startswith("Makro.MakroCore."):
            return self._apply(key, value, source, level="kernel")

        if source in self.trusted_modules:
            return self._apply(key, value, source, level="kernel")

        if source.startswith("plugin:"):
            if self._can_plugin_edit(source, key):
                return self._apply(key, value, source, level="plugin")
            else:
                return self._deny(source, f"Plugin not permitted to modify '{key}'")

        return self._deny(source, "Unauthorized source")

    def _apply(self, key, value, source, level):
        old = self.state[key]
        self.state[key] = value
        self.logger.info(f"✅ [{level}] {source} changed '{key}' from {old} → {value}")
        return True

    def _deny(self, source, reason):
        self.logger.error(f"❌ [DENIED] {source}: {reason}")
        return False

    def _can_plugin_edit(self, plugin_name, key):
        return key in self.plugin_rights.get(plugin_name, [])

    def _detect_source(self):
        """
        Inspect the call stack for the caller's module name.
        Works even with simulated globals.
        """
        for frame_info in inspect.stack()[2:]:  # skip our own frames
            frame = frame_info.frame
            mod_name = frame.f_globals.get("__name__", "")
            if not mod_name:
                continue
            if mod_name.startswith(("inspect", "__main__")):
                continue
            if mod_name.startswith("Makro.MakroCore."):
                return mod_name
            if mod_name.startswith("Plugins."):
                plugin = mod_name.split("Plugins.")[-1].split(".")[0]
                return f"plugin:{plugin}"
        return "unknown"


if __name__ == "__main__":
    kernel = KernelRuntime("default")
    kernel.request_change("enable_gui", True)
    print(kernel.get_state("enable_gui"))
