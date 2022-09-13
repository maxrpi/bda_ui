import PySimpleGUI as sg

top_text_width=16
sorter_width = 30


timeseries_layout = [
  [
    sg.Column(
      [
        [ sg.T("Available Attributes")],
        [ sg.Listbox(values=[], size=(sorter_width,15,),
            enable_events=True, key="-TS_FEATURE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE") ]
      ]
    ),
    sg.Column(
      [
        [ sg.B("INPUTS ->", enable_events=True, key="-TS_INPUT_SEND-") ],
        [ sg.B("<- INPUTS", enable_events=True, key="-TS_RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.B("OUTPUTS ->", enable_events=True, key="-TS_OUTPUT_SEND-") ],
        [ sg.B("<- OUTPUTS", enable_events=True, key="-TS_RETURN_OUTPUT-") ],
        [ sg.Checkbox("Time as input:", default=False, enable_events=True, key="-TIME_AS_INPUT-")]
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.Listbox([], size=(sorter_width,8),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-TS_INPUTS_LIST-")],
        [ sg.T("OUTPUT")],
        [ sg.Listbox([], size=(sorter_width,3),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-TS_OUTPUTS_LIST-")]
      ]
    ),
  ],
  [
    sg.Column(
      [
        [ sg.T("Start Time"),
          sg.In("start time", size=(20, 1), key="-TS_START_TIME-", text_color="black"),
          sg.B("Parse Start Time", enable_events=True, key="-TS_PARSE_START-")
        ],
        [ sg.T("End Time"),
          sg.In("end time", size=(20, 1), key="-TS_END_TIME-", text_color="black"),
          sg.B("Parse End Time", enable_events=True, key="-TS_PARSE_END-")],
        [sg.B("Set maximum range", enable_events=True, key="-TS_SET_MAX_RANGE-")],
        [sg.T("Number of Samples"), sg.In("100", size=(6,1), key="-TS_NUMBER_SAMPLES-"),
        sg.T("OR   Sample period in seconds"), sg.In("0", size=(6,1), key="-TS_SAMPLE_PERIOD-")]
      ]
    )
  ],
  [
    sg.T("Name for MKO"),
    sg.In("name",size=(12,1),  key="-TS_MKO_NAME-"),
    sg.B("Request MKO training", enable_events=True, key="-TS_TRAIN_MKO-"),
    sg.In("", visible=False, enable_events=True, key="-TS_DOWNLOAD_REQUEST_FILENAME-"),
    sg.SaveAs("Download Request Data",
      default_extension=".txt", file_types=[('Text','*.txt')],
      key='-TS_DOWNLOAD_REQUEST_DATA-',
      enable_events=True),
    sg.Checkbox("Time as timestamp",key="-TS_TIME_AS_TIMESTAMP-",enable_events=True),
  ],
]
timeseries_tab = [sg.Tab("Timeseries", timeseries_layout, key="-TIMESERIES_TAB-")]

lot_series_layout = [
  [
    sg.T("Lot Holder Attribute and Name:"),
    sg.T("", size=(8,1), background_color="white", text_color="black", key="-LS_LOT_HOLDER_ATTRIBUTE-"),
    sg.T("", size=(16,1), background_color="white", text_color="black", key="-LS_LOT_HOLDER_NAME-"),
    sg.B("DELETE LOT HOLDER", enable_events=True, key="-LS_DELETE_LOT_HOLDER-")
  ],
  [
    sg.Column(
      [
        [ sg.T("Available features")],
        [ sg.Listbox(values=[], size=(sorter_width,15,),
            enable_events=True, key="-LS_FEATURE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE") ]
      ]
    ),
    sg.Column(
      [
        [ sg.B("INPUTS ->", enable_events=True, key="-LS_INPUT_SEND-") ],
        [ sg.B("<- INPUTS", enable_events=True, key="-LS_RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.B("OUTPUTS ->", enable_events=True, key="-LS_OUTPUT_SEND-") ],
        [ sg.B("<- OUTPUTS", enable_events=True, key="-LS_RETURN_OUTPUT-") ],
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.Listbox([], size=(sorter_width,8),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-LS_INPUTS_LIST-")],
        [ sg.T("OUTPUT")],
        [ sg.Listbox([], size=(sorter_width,3),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-LS_OUTPUTS_LIST-")]
      ]
    ),
  ],
  [
    sg.Column(
      [
        [
          sg.Checkbox("Use All Lots", default=True, enable_events=True, key="-LS_SET_MAX_RANGE-"),
          sg.Push(),
          sg.T("Start Lot"),
          sg.In("start lot", size=(10, 1), key="-LS_START_LOT-", disabled=True),
          sg.Push(),
          sg.T("End Lot"),
          sg.In("end lot", size=(10, 1), key="-LS_END_LOT-", disabled=True),
        ],
      ]
    )
  ],
  [
    sg.T("Name for MKO"),
    sg.In("name",size=(12,1),  key="-LS_MKO_NAME-"),
    sg.B("Request MKO training", enable_events=True, key="-LS_TRAIN_MKO-"),
    sg.In("", visible=False, enable_events=True, key="-LS_DOWNLOAD_REQUEST_FILENAME-"),
    sg.SaveAs("Download Request Data",
      default_extension=".txt", file_types=[('Text','*.txt')],
      key='-LS_DOWNLOAD_REQUEST_DATA-',
      enable_events=True),
  ],
]
lot_series_tab = [sg.Tab("Lot Series", lot_series_layout, key="-LOT_SERIES_TAB-")]


training_tabs = sg.TabGroup(
  [timeseries_tab, lot_series_tab],
  expand_x=True,
  expand_y=True,
  enable_events=True,
  key="-TRAINING_TABGR-"
  )


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
    sg.Frame("ANALYSES", layout=[[training_tabs]], expand_x=True, expand_y=True)
  ]
]