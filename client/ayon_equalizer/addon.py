import os

from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__

EQUALIZER_HOST_DIR = os.path.dirname(os.path.abspath(__file__))


class EqualizerAddon(AYONAddon, IHostAddon):
    """3DEqualizer Addon for AYON."""

    name = "equalizer"
    host_name = "equalizer"
    version = __version__
    heartbeat = 500
    enabled = True

    def initialize(self, settings):
        """Initialize Equalizer Addon."""
        self.heartbeat = settings.get("heartbeat_interval", 500)
        self.enabled = True

    def add_implementation_envs(self, env, _app):
        """Add 3DEqualizer specific environment variables.

        3DEqualizer utilize TDE4_ROOT for its root directory
        and PYTHON_CUSTOM_SCRIPTS_3DE4 as a colon separated list of
        directories to look for additional python scripts.
        (Windows: list is separated by semicolons).

        Arguments:
            env (dict): Environment variables.

        """
        startup_path = os.path.join(EQUALIZER_HOST_DIR, "startup")
        if "PYTHON_CUSTOM_SCRIPTS_3DE4" in env:
            startup_path = os.path.join(
                env["PYTHON_CUSTOM_SCRIPTS_3DE4"],
                startup_path)

        env["PYTHON_CUSTOM_SCRIPTS_3DE4"] = startup_path
        env["AYON_TDE4_HEARTBEAT_INTERVAL"] = str(self.heartbeat)

    def get_launch_hook_paths(self):
        """Get paths to launch hooks."""
        return [os.path.join(EQUALIZER_HOST_DIR, "hooks")]

    def get_workfile_extensions(self):
        """Get workfile extensions."""
        return [".3de"]
