import pyautogui

VERTICAL_SCROLL = 0
HORIZONTAL_SCROLL = 1

def base_scroll(distance, direction):
    try:
        distance = int(distance)
        direction = int(direction)
    except ValueError:
        return "Invalid distance or direction"
    if direction == VERTICAL_SCROLL:
        # Vertical scroll
        pyautogui.scroll(distance)
    elif direction == HORIZONTAL_SCROLL:
        # Horizontal scroll
        pyautogui.hscroll(distance)
    else:
        raise ValueError("Invalid direction. Use 0 for vertical and 1 for horizontal scroll.")

def scroll(move_to_x, move_to_y, distance, direction):
    # Move the mouse to the specified coordinates
    pyautogui.moveTo(move_to_x, move_to_y)
    
    # Perform the scroll action
    base_scroll(distance, direction)

