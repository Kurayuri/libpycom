from doctest import debug
from libpycom.Messager import LEVEL, STYLE
from libpycom import Settings

message = Settings.messager.message
message_progress = Settings.messager.message_progress
message_enumprogress = Settings.messager.message_enumprogress

debug = Settings.messager.debug
info = Settings.messager.info
warning = Settings.messager.warning
error = Settings.messager.error
critial = Settings.messager.critial
