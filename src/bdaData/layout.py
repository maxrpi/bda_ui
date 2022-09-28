import PySimpleGUI as sg

top_text_width=16
sorter_width = 20


timeseries_layout = [
  [
    sg.Column(
      [
        [ sg.T("Available Attributes")],
        [ sg.Listbox(values=[], size=(sorter_width,10,),
            enable_events=True, key="-TS_FEATURE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE") ],
        [ sg.Checkbox("Time as input:",
            default=False,
            enable_events=True, key="-TS_TIME_AS_INPUT-")],
      ]
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.B(sg.SYMBOL_RIGHT, enable_events=True, key="-TS_INPUT_SEND-") ],
        [ sg.B(sg.SYMBOL_LEFT, enable_events=True, key="-TS_RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.T("OUTPUT")],
        [ sg.B(sg.SYMBOL_RIGHT, enable_events=True, key="-TS_OUTPUT_SEND-") ],
        [ sg.B(sg.SYMBOL_LEFT, enable_events=True, key="-TS_RETURN_OUTPUT-") ],
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.Listbox([], size=(sorter_width,6),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-TS_INPUTS_LIST-")],
        [ sg.Listbox([], size=(sorter_width,6),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-TS_OUTPUTS_LIST-")]
      ],
      vertical_alignment="center"
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
          sg.B("Parse End Time", enable_events=True, key="-TS_PARSE_END-"),
        ],
        [ sg.B("Set maximum range", enable_events=True, key="-TS_SET_MAX_RANGE-"), ],
      ],
    vertical_alignment='center'
    ),
  ],
  [
    sg.Column(
      [
        [
          sg.T("Number of Samples"), sg.In("100", size=(6,1), key="-TS_NUMBER_SAMPLES-"),
          sg.T("OR   Sample period in seconds"), sg.In("0", size=(6,1), key="-TS_SAMPLE_PERIOD-")
        ],
        [
          sg.Checkbox("Time as timestamp",key="-TS_TIME_AS_TIMESTAMP-",enable_events=True),
        ]
      ],
      vertical_alignment="center"
    )
  ],
]
timeseries_tab = [sg.Tab("Timeseries", timeseries_layout, key="-TIMESERIES_TAB-")]

lot_series_layout = [
  [
    sg.T("Lot Holder Attribute and Name:"),
    sg.T("", size=(8,1), background_color="white", text_color="black", key="-LS_LOT_HOLDER_ATTRIBUTE-"),
    sg.T("", size=(16,1), background_color="white", text_color="black", key="-LS_LOT_HOLDER_NAME-"),
    sg.B("DELETE", enable_events=True, key="-LS_DELETE_LOT_HOLDER-")
  ],
  [
    sg.Column(
      [
        [
          sg.T("Available features")
        ],
        [
          sg.Listbox(values=[], size=(sorter_width,12,),
            enable_events=True, key="-LS_FEATURE_LIST-",
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE")
        ]
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.T("INPUTS") ],
        [ sg.B(sg.SYMBOL_RIGHT, enable_events=True, key="-LS_INPUT_SEND-") ],
        [ sg.B(sg.SYMBOL_LEFT, enable_events=True, key="-LS_RETURN_INPUT-") ],
        [ sg.HorizontalSeparator()],
        [ sg.T("OUTPUT")],
        [ sg.B(sg.SYMBOL_RIGHT, enable_events=True, key="-LS_OUTPUT_SEND-") ],
        [ sg.B(sg.SYMBOL_LEFT, enable_events=True, key="-LS_RETURN_OUTPUT-") ],
      ],
      vertical_alignment="center"
    ),
    sg.Column(
      [
        [ sg.Listbox([], size=(sorter_width,6),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-LS_INPUTS_LIST-")],
        [ sg.Listbox([], size=(sorter_width,6),
            select_mode="LISTBOX_SELECT_MODE_MULTIPLE",
            key="-LS_OUTPUTS_LIST-")]
      ],
      vertical_alignment="center"
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
]
lot_series_tab = [sg.Tab("Lot Series", lot_series_layout, key="-LOT_SERIES_TAB-")]


dataspec_tabs = sg.TabGroup(
  [timeseries_tab, lot_series_tab],
  expand_x=True,
  expand_y=True,
  enable_events=True,
  key="-DATASPEC_TABGR-"
  )

layout = [
  [
    sg.Frame("DATA SPEC", layout=[[dataspec_tabs]], expand_x=True, expand_y=True)
  ],
  [
    sg.In("", visible=False, enable_events=True, key="-DS_DOWNLOAD_REQUEST_FILENAME-"),
    sg.SaveAs("Download Request Data",
      default_extension=".txt",
      file_types=[('Text','*.txt')],
      enable_events=True
    ),
  ],
  [
    sg.T("Name for MKO"),
    sg.In("name",size=(12,1),  key="-DS_MKO_NAME-"),
    sg.B("Send MKO to Training Tab",
      enable_events=True,
      key="-DS_SEND_MKO_TO_TRAINING-",
    )
  ]
]