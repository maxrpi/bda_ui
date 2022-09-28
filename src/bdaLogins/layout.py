import PySimpleGUI as sg

top_text_width=16
sorter_width = 30

layout = [
  [
    sg.T("BDA URL:"),
    sg.In("URL", enable_events=True, key="-BDA_URL-", size=32),
    sg.In("ServerSecret", enable_events=True, key="-SERVER_SECRET-", size=10),
  ],
  [
    sg.B("Init server", enable_events=True, key="-INIT_SERVER-")
  ],
  [
    sg.T("BDA Username:"),
    sg.In("username", enable_events=True, key="-BDA_USER-", size=top_text_width),
    sg.T("BDA password:"),
    sg.In("password", enable_events=True, key="-BDA_PASSWORD-", size=top_text_width, password_char="*"),
  ],
  [
    sg.B("Create User", enable_events=True, key="-CREATE_USER-")
  ],
  [
    sg.B("Log in", enable_events=True, key="-LOG_IN_BDA-"),
    sg.T("BDA token expires:"),
    sg.Multiline("-------", size=(20,1),
                no_scrollbar=True, justification="t", key="-BDA_EXPIRES-"),
  ],
]