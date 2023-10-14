import platform

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


# Add ngspice.dll when building for Windows
class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if platform.system() == "Windows" and version != "editable":
            build_data['force_include']['lib/ngspice.dll'] = 'phyether/ngspice.dll'
            build_data['force_include']['lib/LICENSE'] = 'phyether/LICENSE.ngspice'
