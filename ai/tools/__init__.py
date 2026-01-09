"""
Modular tools structure for AI agents.
"""

from .order_tools import order_tools
from .ticket_tools import ticket_tools
from .support_tools import support_tools
from .document_tools import document_tools
from .tmdb_tools import tmdb_tools

__all__ = [
    "order_tools",
    "ticket_tools",
    "support_tools",
    "document_tools",
    "tmdb_tools",
]
