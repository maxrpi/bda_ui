import PySimpleGUI as sg
from pathlib import Path

SETTINGS_PATH = Path.cwd()
settings = sg.UserSettings(
  path=SETTINGS_PATH, filename=".config.ini", use_config_file=True, convert_bools_and_none=True
)

theme = settings["GUI"]["theme"]
font_family = settings["GUI"]["font_family"]
font_size = int(settings["GUI"]["font_size"])
padding = int(settings["GUI"]["padding"])
sg.theme(theme)
sg.set_options(font=(font_family, font_size), element_padding=(padding,padding))