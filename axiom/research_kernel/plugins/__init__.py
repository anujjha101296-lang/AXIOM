"""Built-in research domain plugins."""

from axiom.research_kernel.plugins.computer_science import ComputerSciencePlugin
from axiom.research_kernel.plugins.mathematics import MathematicsPlugin
from axiom.research_kernel.plugins.vlsi_hardware import VlsiHardwarePlugin

__all__ = ["MathematicsPlugin", "ComputerSciencePlugin", "VlsiHardwarePlugin"]
