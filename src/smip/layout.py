import PySimpleGUI as sg


def LEDIndicator(key=None, radius=30):
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key)

def SetLED(window, key, color):
    graph = window[key]
    graph.erase()
    graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)

top_text_width=13

layout = [
  [
    sg.T("URL:"),
    sg.In("", enable_events=True, key="-SMIP_URL-", size=32),
  ],
  [
    sg.T("SMIP Username:"),
    sg.In("username", enable_events=True, key="-SMIP_USER-", size=top_text_width-2),
    sg.T("SMIP password:"),
    sg.In("password", enable_events=True, key="-SMIP_PASSWORD-", size=top_text_width,
      password_char="*"),
  ],
  [
    sg.T("SMIP role:"),
    sg.In("role", enable_events=True, key="-SMIP_ROLE-", size=top_text_width-2),
  ],
  [
    sg.B("Get Token", enable_events=True, key="-GET_SMIP_TOKEN-"),
    sg.T("SMIP token expires:"),
    sg.Multiline("no token", size=(20,1),
                no_scrollbar=True, justification="t", key="-SMIP_EXPIRES-"),
    sg.B(image_filename="images/copy-icon.png",
      image_size=(16,16),
      image_subsample=4,
      enable_events=True, 
      visible=False, 
      key="-SEND_TO_CLIPBOARD-"),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.Column(
      [
        [
          sg.T("Attribute id:"),
          sg.In("", size=(5, 1), key="-ATTRIBUTE_ID-"),
        ],
        [
          sg.B("Validate Id", enable_events=True, key="-VALIDATE_ID-"),
          sg.B("Delete data from ID", button_color="red", enable_events=True, visible=False, key="-DELETE_DATA_FROM_ID-")
        ],
        [
          sg.In("", visible=False, key='-UPLOAD_FILENAME-', enable_events=True),
          sg.FileBrowse("Upload file to attribute", enable_events=True, target="-UPLOAD_FILENAME-"),
        ],
        [
          sg.Radio("Replace All", group_id="InsertReplace", default=True, key="-REPLACE_ALL-" ),
          sg.Radio("Insert", group_id="InsertReplace", default=False, key="-INSERT_DATA-" )
        ],
        [
          LEDIndicator(key="-TIMESERIES_LED-"), sg.T("Timeseries", font=("Helvetica", 16)),
          sg.Push(),
          LEDIndicator(key="-LOT_LED-"), sg.T("Lot data", font=("Helvetica", 16)),
          sg.Push(),
          sg.Push(),
        ],
        [
          sg.B("Download attribute data", enable_events=True, key="-DOWNLOAD_ATTRIBUTE-", visible=False)
        ],
        [
          sg.T("Attribute name"), 
        ],
        [
          sg.In("ATTRIBUTE NAME", size=25, enable_events=True, key="-ATTRIBUTE_NAME-") ,
        ],
        [
          sg.B("Send attribute to BDA", enable_events=True, key="-ATTRIBUTE_TO_BDA-")
        ]
      ],
      vertical_alignment='top', justification='l', p=10
    ),
    sg.Column(
      [
        [
          sg.T("Eq/Prop Description"),
        ],
        [
          sg.Multiline("",size=(35,30), key="-EP_DESCRIPTION-")
        ]
      ],
      element_justification='l',justification='l'
    ),
  ],
]
