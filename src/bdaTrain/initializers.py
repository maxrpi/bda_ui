
def assign_settings(page, window):
  if page._settings is None:
    return
  if page.settings['url'] is not None:
    window['-BDA_URL-'].update(page.settings['url']) 
  if page.settings['username'] is not None:
    window['-BDA_USER-'].update(page.settings['username']) 
  if page.settings['password'] is not None:
    window['-BDA_PASSWORD-'].update(page.settings['password']) 

def set_bindings(page, window):
  window['-PARSE_START-'].bind('<KeyPress-Return>','RETURN')
  window['-PARSE_END-'].bind('<KeyPress-Return>','RETURN')

def initialize_data(page, window):
  page.avail_keys = []
  page.known_attributes = []
  page.inputs_keys = []
  page.outputs_keys = []


initializers = [assign_settings, initialize_data, set_bindings]
