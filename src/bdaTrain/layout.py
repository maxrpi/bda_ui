import PySimpleGUI as sg

layer_keys = {
  "type"        : "-DT_LAYER_{}",
  "activation"  : "-DT_ACTIVATION_{}",
  "units"       : "-DT_UNITS_{}",
  "rate"        : "-DT_RATE_{}",
  "regularizer" : "-DT_REG_{}",
  "lambda"      : "-DT_LAMBDA_{}",
}
layer_types = ["-", "dense", "dropout", "variational", "concrete"]
activation_types = ["linear", "relu", "tanh", "sigmoid"]
reg_types = ["L2", "L1"]
loss_functions = ["mse"]
optimizers = ["adam"]
number_of_layers = 5

training_options = [
  [
    sg.T("batchsize:"),sg.In("32", enable_events=True, size=5, key="-DT_BATCHSIZE-"),
    sg.T("epoch length:"),sg.In("300", enable_events=True, size=5, key="-DT_EPOCH-"),
    sg.T("rate sched:"),sg.In("[(0, 0.001)]", enable_events=True, size=20, key="-DT_LR_SCHEDULE-"),
  ],
  [
    sg.T("loss function:"),sg.Combo(default_value="mse", values=loss_functions, enable_events=True, size=5, key="-DT_LOSSFUNCTION-"),
    sg.T("optimizer:"),sg.Combo(default_value="adam", values=optimizers, enable_events=True, size=5, key="-DT_OPTIMIZER-"),
  ],
  [
    sg.Checkbox("Autocalibrate", default=False, enable_events=True, key="-DT_AUTOCALIBRATE-"),
  ],
  [
    sg.Column(
      [
        [
          sg.Combo(default_value="-",values=layer_types, enable_events=True, size=10, readonly=True, key="-DT_LAYER_0" ),
          sg.Combo(default_value="linear",values=activation_types, visible=False, size=6, readonly=True, key="-DT_ACTIVATION_0" ),
          sg.Combo(default_value="L2",values=reg_types, visible=False, size=4, readonly=True, key="-DT_REG_0" ),
          sg.In("0.01", enable_events=True, visible=False, size=5, key="-DT_LAMBDA_0"),
          sg.In("10", size=3, visible=False, key="-DT_UNITS_0"),
          sg.In("0.9", size=4, key="-DT_RATE_0", visible=False)
        ],
        [
          sg.Combo(default_value="-",values=layer_types, enable_events=True, size=10, readonly=True, key="-DT_LAYER_1" ),
          sg.Combo(default_value="linear",values=activation_types, visible=False, size=6, readonly=True, key="-DT_ACTIVATION_1" ),
          sg.Combo(default_value="L2",values=reg_types, visible=False, size=4, readonly=True, key="-DT_REG_1" ),
          sg.In("0.01", enable_events=True, visible=False, size=5, key="-DT_LAMBDA_1"),
          sg.In("10", size=3, visible=False, key="-DT_UNITS_1"),
          sg.In("0.9", size=4, key="-DT_RATE_1", visible=False)
        ],
        [
          sg.Combo(default_value="-",values=layer_types, enable_events=True, size=10, readonly=True, key="-DT_LAYER_2" ),
          sg.Combo(default_value="linear",values=activation_types, visible=False, size=6, readonly=True, key="-DT_ACTIVATION_2" ),
          sg.Combo(default_value="L2",values=reg_types, visible=False, size=4, readonly=True, key="-DT_REG_2" ),
          sg.In("0.01", enable_events=True, visible=False, size=5, key="-DT_LAMBDA_2"),
          sg.In("10", size=3, visible=False, key="-DT_UNITS_2"),
          sg.In("0.9", size=4, key="-DT_RATE_2", visible=False)
        ],
        [
          sg.Combo(default_value="-",values=layer_types, enable_events=True, size=10, readonly=True, key="-DT_LAYER_3" ),
          sg.Combo(default_value="linear",values=activation_types, visible=False, size=6, readonly=True, key="-DT_ACTIVATION_3" ),
          sg.Combo(default_value="L2",values=reg_types, visible=False, size=4, readonly=True, key="-DT_REG_3" ),
          sg.In("0.01", enable_events=True, visible=False, size=5, key="-DT_LAMBDA_3"),
          sg.In("10", size=3, visible=False, key="-DT_UNITS_3"),
          sg.In("0.9", size=4, key="-DT_RATE_3", visible=False)
        ],
        [
          sg.Combo(default_value="-",values=layer_types, enable_events=True, size=10, readonly=True, key="-DT_LAYER_4" ),
          sg.Combo(default_value="linear",values=activation_types, visible=False, size=6, readonly=True, key="-DT_ACTIVATION_4" ),
          sg.Combo(default_value="L2",values=reg_types, visible=False, size=4, readonly=True, key="-DT_REG_4" ),
          sg.In("0.01", enable_events=True, visible=False, size=5, key="-DT_LAMBDA_4"),
          sg.In("10", size=3, visible=False, key="-DT_UNITS_4"),
          sg.In("0.9", size=4, key="-DT_RATE_4", visible=False)
        ],
      ]
    ),
  ],
  [
    sg.HorizontalSeparator()
  ],
  [
    sg.Frame(title="Presets", layout=[[
      sg.Combo(values=[],size=10,bind_return_key=True,enable_events=True,key="-PRESET_MENU-"),
      sg.B("Save Preset"),
      sg.B("Delete Preset"),
    ]])
  ],
  [ 
    sg.T("OnDeck MKO:"),
    sg.In("", size=8, readonly=True, pad=1, key="-DT_ONDECK_MKO-"),
    sg.T("Train as name:", pad=1),
    sg.In("", size=8, pad=1, key="-DT_TRAIN_AS_NAME-"),
    sg.B("Train", enable_events=True, pad=1, button_color="green" ,key="-TRAIN_MKO-"),
  ],
]

layout = [
  [ 
    sg.Column(
      [
        [
          sg.T("PREPPED MKOs")
        ],
        [
          sg.Table(
            values=[[]],
            headings=["MKO", "stage"],
            col_widths = [15,6],
            justification='center',
            background_color="white",
            text_color="black",
            enable_events=False,
            select_mode="browse",
            expand_x=True,
            key="-BT_PREPPED_MKOS-"
            ),
        ],
        [
          sg.B("ON DECK", enable_events=True, key="-DT_PREPPED_TO_ONDECK-")
        ],
        [
          sg.B("Delete", enable_events=True, key="-DT_PREPPED_DELETE-")
        ]
      ],
      vertical_alignment="top"
    ),
    sg.Frame("Training Options", layout=training_options, expand_x=True, expand_y=True),
  ],
  [
    sg.Column([
      [
        sg.T("IN-PROGRESS MKOs")
      ],
      [
        sg.Table(values=[[]],
          headings=["MKO", "Stage" ,"Progress"],
          col_widths = [8, 5, 10],
          auto_size_columns=False,
          justification='center',
          background_color="white",
          text_color="black",
          key="-IN_PROGRESS_MKOS-",
          display_row_numbers=False,
          num_rows=6,
          expand_x=False,
          vertical_scroll_only=True
          ),
      ],
      [
        sg.B("Unqueue MKOs", enable_events=True, key="-UNQUEUE_MKOS-")
      ]
    ], vertical_alignment="top"),
    sg.Column([
      [
        sg.T("READY MKOs")
      ],
      [
        sg.Listbox(
          [],
          size=(11,7),
          select_mode="LISTBOX_SELECT_MODE_SINGLE",
          key="-DT_READY_MKOS-"
        ),
      ],
    ], vertical_alignment="top"),
    sg.Column([
      [ sg.T("SEND TO:") ],
      [ sg.B("ON DECK", enable_events=True, key="-DT_READY_TO_ONDECK-"), ],
      [ sg.B("Infer", enable_events=True, key="-DT_TO_INFER-"), ],
      [ sg.SaveAs("File", file_types=[(".mko", "*.mko")], enable_events=True, key="-DT_READY_SAVE-"), ],
      [ sg.HorizontalSeparator(), ],
      [ sg.In("", visible=False, enable_events=True, key="-DT_READY_LOAD_FILENAME-"), ],
      [ sg.FileBrowse("Load MKO", enable_events=True, file_types=[(".mko", "*.mko")], key="-DT_READY_LOAD-") ],

    ], vertical_alignment="top"),
  ],
]