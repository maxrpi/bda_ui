import json

from bdaTrain.layout import (
  layer_keys,
  number_of_layers,
  layer_types,
  activation_types,
  reg_types,
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
    l_reg = values[layer_keys["regularizer"].format(index)]
    l_lambda = float(values[layer_keys["lambda"].format(index)])
    l_units = int(values[layer_keys["units"].format(index)])
    l_rate = float(values[layer_keys["rate"].format(index)])
    if l_type in ["dropout", "variational_dropout"]: # These layers actually filter dense layers
      layer = {
        "type": "dense",
        "activation": l_activation,
        "units": l_units,
        "regularizer" : l_reg,
        "lambda" : l_lambda
      }
      l_activation="linear"
      layers.append(layer)
    layer = {
      "type": l_type,
      "activation": l_activation,
      "units": l_units,
      "rate" : l_rate,
      "regularizer" : l_reg,
      "lambda" : l_lambda
    }
    if l_type == "concrete":
      del layer['regularizer']
      del layer['lambda']
    layers.append(layer)
  return layers
  
def get_hyperparameter_spec(values):
  batch_size = int(values['-DT_BATCHSIZE-'])
  epochs = int(values['-DT_EPOCH-'])
  #learning_rate = float(values['-DT_LEARNING_RATE-'])
  loss_function = values['-DT_LOSSFUNCTION-']
  optimizer = values['-DT_OPTIMIZER-']
  lr_schedule = values['-DT_LR_SCHEDULE-']
  lr_schedule = json.loads(lr_schedule)

  hypers = {
    "batch_size"    : batch_size,
    "epochs"        : epochs,
    "loss_function" : loss_function,
    "optimizer"     : optimizer,
    "lr_schedule"   : lr_schedule
  }
  return hypers

def get_hypers_from_mko(service, mko):
  data = service.get_mko_as_dict(mko)
  return data.get('hypers', {})

def get_topology_from_mko(service, mko):
  data = service.get_mko_as_dict(mko)
  return data.get('topology', [])

def topology_to_ui(topology, window):
  skip = False
  tmpology = []
  for i in range(len(topology)-1, -1, -1):
    layer = topology[i]
    if skip:
      activation = layer['activation']
      tmpology[0]['activation'] = activation
      skip = False
      continue
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

    if 'regularizer' in layer:
      l_reg = layer['regularizer']
      if l_reg not in reg_types:
        raise ValueError(f"Regularizer type {l_reg} unsupported")
      i_reg = reg_types.index(l_reg)
      window[layer_keys['regularizer'].format(i)].update(set_to_index=i_reg)
      if 'lambda' in layer:
        window[layer_keys['lambda'].format(i)].update(value=layer['lambda'])

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
  #if 'learning_rate' in hypers:
  #  window['-DT_LEARNING_RATE-'].update(hypers['learning_rate'])
  if 'loss_function' in hypers:
    index = loss_functions.index(hypers['loss_function'])
    window['-DT_LOSSFUNCTION-'].update(set_to_index=index)
  if 'optimizer' in hypers:
    index = optimizers.index(hypers['optimizer'])
    window['-DT_OPTIMIZER-'].update(set_to_index=index)
  if 'lr_schedule' in hypers:
    window['-DT_LR_SCHEDULE-'].update(json.dumps(hypers['lr_schedule']))
  return