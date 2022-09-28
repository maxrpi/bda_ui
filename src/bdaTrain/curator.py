from bdaTrain.layout import (
  layer_keys,
  number_of_layers,
  layer_types,
  activation_types,
  loss_functions,
  optimizers
  )

def get_layer_spec(values):
  layers = []
  for index in range(number_of_layers):
    l_type = values[layer_keys["type"].format(index)]
    if l_type == 'variational': l_type = 'variational_dropout'
    if l_type == "-":
      continue
    l_activation = values[layer_keys["activation"].format(index)]
    l_units = int(values[layer_keys["units"].format(index)])
    l_rate = float(values[layer_keys["rate"].format(index)])
    if l_type in ["dropout", "variational_dropout"]: # These layers actually filter dense layers
      layer = {
        "type": "dense",
        "activation": l_activation,
        "units": l_units,
      }
      l_activation="linear"
      layers.append(layer)
    layer = {
      "type": l_type,
      "activation": l_activation,
      "units": l_units,
      "rate" : l_rate
    }
    layers.append(layer)
  return layers
  
def get_hyperparameter_spec(values):
  batch_size = int(values['-DT_BATCHSIZE-'])
  epochs = int(values['-DT_EPOCH-'])
  learning_rate = float(values['-DT_LEARNING_RATE-'])
  loss_function = values['-DT_LOSSFUNCTION-']
  optimizer = values['-DT_OPTIMIZER-']

  hypers = {
    "batch_size"    : batch_size,
    "epochs"        : epochs,
    "learning_rate" : learning_rate,
    "loss_function" : loss_function,
    "optimizer"     : optimizer,
  }
  return hypers

def get_hypers_from_mko(service, mko):
  data = service.get_mko_as_dict(mko)
  return data.get('hyperparameters', {})

def get_topology_from_mko(service, mko):
  data = service.get_mko_as_dict(mko)
  return data.get('topology', [])

def topology_to_ui(topology, window):
  skip = False
  tmpology = []
  for i in range(len(topology)-1, -1, -1):
    if skip:
      skip = False
      continue
    layer = topology[i]
    if layer['type'] in ['dropout', 'variational_dropout']:
      skip = True
    tmpology.insert(0,layer)
  
  for i, layer in enumerate(tmpology):
    l_type = layer['type']
    if l_type == 'variational_dropout': l_type = 'variational'
    if l_type not in layer_types:
      raise ValueError(f"Layer type {l_type} unsupported")
    i_type = layer_types.index(l_type)
    l_activation = layer['activation']
    if l_activation not in activation_types:
      raise ValueError(f"Activation type {l_activation} unsupported")
    i_activation = activation_types.index(l_activation)

    window[layer_keys['type'].format(i)].update(set_to_index=i_type)
    window[layer_keys['activation'].format(i)].update(set_to_index=i_activation)
    if 'units' in layer:
      window[layer_keys['units'].format(i)].update(value=layer['units'])
    if 'rate' in layer:
      window[layer_keys['rate'].format(i)].update(value=layer['rate'])

  return

def hypers_to_ui(hypers, window):
  if 'batch_size' in hypers:
    window['-DT_BATCHSIZE-'].update(hypers['batch_size'])
  if 'epochs' in hypers:
    window['-DT_EPOCH-'].update(hypers['epochs'])
  if 'learning_rate' in hypers:
    window['-DT_LEARNING_RATE-'].update(hypers['learning_rate'])
  if 'loss_function' in hypers:
    index = loss_functions.index(hypers['loss_function'])
    window['-DT_LOSSFUNCTION'].update(set_to_index=index)
  if 'optimizer' in hypers:
    index = optimizers.index(hypers['optimizer'])
    window['-DT_OPTIMIZER'].update(set_to_index=index)
  return