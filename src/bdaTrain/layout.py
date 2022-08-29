import PySimpleGUI as sg

top_text_width=16
sorter_width = 30

layout = [
  [
    sg.T("BDA URL:"),
    sg.In("URL", enable_events=True, key="-BDA_URL-", size=32),
    sg.In("ServerSecret", enable_events=True, key="-SERVER_SECRET-", size=10),
    sg.B("Init server", enable_events=True, key="-INIT_SERVER-")
  ],
  [
    sg.T("BDA Username:"),
    sg.In("username", enable_events=True, key="-BDA_USER-", size=top_text_width),
    sg.T("BDA password:"),
    sg.In("password", enable_events=True, key="-BDA_PASSWORD-", size=top_text_width, password_char="*"),
    sg.B("Create User", enable_events=True, key="-CREATE_USER-")
  ],
  [
    sg.B("Log in", enable_events=True, key="-LOG_IN_BDA-"),
    sg.T("BDA token expires:"),
    sg.Multiline("-------", size=(20,1),
                no_scrollbar=True, justification="t", key="-BDA_EXPIRES-"),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.T("CREATE MODEL")
  ],
  [
    sg.Column(
      [
        [ sg.T("Available Attributes")],
        [ sg.Listbox(values=[], size=(sorter_width,15,),
            enable_events=True, key="-ATTRIBUTE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE") ]
      ]
    ),
    sg.Column(
      [
        [ sg.B("INPUTS ->", enable_events=True, key="-INPUT_SEND-") ],
        [ sg.B("<- INPUTS", enable_events=True, key="-RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.B("OUTPUTS ->", enable_events=True, key="-OUTPUT_SEND-") ],
        [ sg.B("<- OUTPUTS", enable_events=True, key="-RETURN_OUTPUT-") ]
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.Listbox([], size=(sorter_width,8),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-INPUTS_LIST-")],
        [ sg.T("OUTPUT")],
        [ sg.Listbox([], size=(sorter_width,3),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-OUTPUTS_LIST-")]
      ]
    ),
  ],
  [
    sg.Column(
      [
        [ sg.T("Start Time"),
          sg.In("start time", size=(20, 1), key="-START_TIME-"),
          sg.B("Parse Start Time", enable_events=True, key="-PARSE_START-")
        ],
        [ sg.T("End Time"),
          sg.In("end time", size=(20, 1), key="-END_TIME-"),
          sg.B("Parse End Time", enable_events=True, key="-PARSE_END-")],
        [sg.B("Set maximum range", enable_events=True, key="-SET_MAX_RANGE-")],
        [sg.T("Number of Samples"), sg.In("0", size=(6,1), key="-NUMBER_SAMPLES-")],
        [sg.T("Sample period in seconds"), sg.In("0", size=(6,1), key="-SAMPLE_PERIOD-")]
      ]
    )
  ],
  [
    sg.T("Auth to send"),
    sg.Checkbox("SMIP token", key="-BOOL_SEND_TOKEN-"),
    sg.Checkbox("Username/Password", key="-BOOL_SEND_USERPASS-")
  ],
  [
    sg.In("", visible=False, enable_events=True, key="-DOWNLOAD_REQUEST_FILENAME-"),
    sg.SaveAs("Download Request Data",
      default_extension=".txt", file_types=[('Text','*.txt')],
      key='-DOWNLOAD_REQUEST_DATA-',
      enable_events=True)
  ],
  [
    sg.T("Name for MKO"),
    sg.In("name", key="-MKOname-"),
    sg.B("Request MKO training", enable_events=True, key="-TRAIN_MKO-")
  ],
  [
    sg.T("Error Output", visible=False, key="-ERRORREPORT1-"),
    sg.Multiline("Error Output", visible=False, key="-ERRORREPORT2-")
  ] 
]
