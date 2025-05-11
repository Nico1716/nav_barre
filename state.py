# État global de l'application
control_all_boats = False

def toggle_control_all_boats():
    global control_all_boats
    control_all_boats = not control_all_boats
    print(f"Toggling control_all_boats to: {control_all_boats}")  # Debug print 