from re import T
import PySimpleGUI as sg

sg.theme('Dark Amber')
top_text_width=16
layout = [
  [
    sg.T("URL:"),
    sg.In("URL", enable_events=True, key="-SMIP_URL-", size=top_text_width),
    sg.T("SMIP Username:"),
    sg.In("username", enable_events=True, key="-SMIP_USER-", size=top_text_width),
    sg.T("SMIP password:"),
    sg.In("password", enable_events=True, key="-SMIP_PASSWORD-", size=top_text_width),
    sg.T("SMIP token:"),
    sg.Multiline(size=(top_text_width,5), no_scrollbar=True, justification="t", key="-SMIP_TOKEN-"),
  ],
  [
    sg.B("Get Token", enable_events=True, key="-GET_TOKEN-"),
    sg.B("Send to BDA", enable_events=True, key="-SEND_TO_BDA")
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.Column(
      [
        [
          sg.T("Eq/Property tag:"),
          sg.In(size=(5, 1), enable_events=True, key="-EQPROPTAG-") ,
        ],
        [sg.B("Validate Tag", enable_events=True, key="-VALIDATE_TAG-")],
      ],
      vertical_alignment='top', justification='l', p=10
    ),
    sg.Column(
      [
        [
          sg.T("Eq/Prop Description"),
        ],
        [
          sg.Output(size=(40,30), key="-EP_DESCRIPTION-")
        ]
      ],
      element_justification='r',justification='r'
    ),
  ],
]

if __name__ == "__main__":
  window = sg.Window('test', layout, font=('Helvetica', '14'))
  while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
      break

  window.close()
