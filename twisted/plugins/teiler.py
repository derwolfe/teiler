"""
Twisted twisted application plugins.
"""

from twisted.application.service import ServiceMaker

teilerService = ServiceMaker(
    "teiler service/",
    "teiler.tap",
    "Simple local filesharing",
    "teiler"
)
