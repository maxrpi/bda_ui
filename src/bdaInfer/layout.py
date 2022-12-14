import PySimpleGUI as sg
from bdaInfer.analysisUIs import UIs


analysis_layouts = []
for name in UIs:
  ui = UIs[name]
  analysis_layouts.append(
    sg.Tab(name, ui.layout, key=name)
  )


option_tabs = sg.TabGroup(
  [analysis_layouts],
  expand_x=True,
  expand_y=True,
  enable_events=True,
  key="-ANALYSIS_TABGR-"
  )

layout = [
  [
    sg.T("CREATE ANALYSIS")
  ],
  [
    sg.Column(
      [
        [
          sg.T("READY MKOs")
        ],
        [
          sg.Listbox(
            [],
            size=(11,10),
            select_mode="LISTBOX_SELECT_MODE_SINGLE",
            key="-BI_AVAILABLE_MKOS-"
            ),
        ],
        [
          sg.B("DELETE", key="-BI_DELETE_AVAILABLE_MKO-")
        ],
      ]
    ),
    sg.Frame("ANALYSES", layout=[[option_tabs]],  size=(425,300)),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.Column(
      [
        [
          sg.Listbox(
            [],
            size=(11,10),
            select_mode="LISTBOX_SELECT_MODE_SINGLE",
            key="-READY_ANALYSES-"
          )
        ],
        [
          sg.B("Display Analysis", enable_events=True, key="-DISPLAY_ANALYSIS-")
        ],
        [
          sg.B("DELETE", key="-BI_DELETE_ANALYSIS-")
        ]
      ]
    ) ,
    sg.Column(
      [
        [
          sg.Table(values=[[]],
            headings=["Analysis", "Progress"],
            col_widths = [8,  10],
            auto_size_columns=False,
            justification='center',
            background_color="white",
            text_color="black",
            key="-PENDING_ANALYSES-",
            display_row_numbers=False,
            num_rows=4,
            expand_x=False,
            vertical_scroll_only=True
            ),
        ],
        [
          sg.B("Unqueue Analyses", enable_events=True, key="-UNQUEUE_ANALYSES-")
        ]
      ]
    )
  ]
]