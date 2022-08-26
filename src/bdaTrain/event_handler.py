
def event_handler(page, event, values, window):
    
  for triggers, action in page.actions.items():
    if action(page, event, values, window):
      return True

  return False
