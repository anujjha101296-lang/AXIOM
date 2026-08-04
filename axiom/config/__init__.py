"""axiom/config/__init__.py — re-exports for convenience."""
from axiom.config.settings import get_settings, settings, AxiomSettings

__all__ = ["get_settings", "settings", "AxiomSettings"]
