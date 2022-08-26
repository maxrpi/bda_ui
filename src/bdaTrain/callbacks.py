 
from bdaTrain.UI import page as page

def add_attribute(attrib_id, attrib_name, window):

  if attrib_name not in page.known_attributes:
    page.avail_keys.append(attrib_name)
    page.known_attributes[attrib_name] = attrib_id
    window['-ATTRIBUTE_LIST-'].update(values=page.avail_keys)
    new_index = page.avail_keys.index(attrib_name)
    window['-ATTRIBUTE_LIST-'].update(set_to_index=[new_index],
    scroll_to_index=new_index)
  else:
    page.known_attributes[attrib_name] = attrib_id
  
  callbacks = {
    "add_attribute": add_attribute
  }