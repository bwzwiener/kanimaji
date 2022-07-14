
import math

# *_BORDER_WIDTH is the width INCLUDING the border.
STOKE_BORDER_WIDTH   = 4.5
STOKE_BORDER_COLOR   = "#666"
STOKE_UNFILLED_COLOR = "#eee"
STOKE_UNFILLED_WIDTH = 3
STOKE_FILLING_COLOR  = "#f00"
STOKE_FILLED_COLOR   = "#000"
STOKE_FILLED_WIDTH   = 3.1

# brush settings
SHOW_BRUSH              = True
SHOW_BRUSH_FRONT_BORDER = True
BRUSH_COLOR             = "#f00"
BRUSH_WIDTH             = 5.5
BRUSH_BORDER_COLOR      = "#666"
BRUSH_BORDER_WIDTH      = 7

WAIT_AFTER = 1.5

# sqrt, ie a stroke 4 times the length is drawn
# at twice the speed, in twice the time.
def stroke_length_to_duration(length):
    return math.sqrt(length)/8

# global time rescale, let's make animation a bit
# faster when there are many strokes.
def time_rescale(interval):
    return math.pow(2 * interval, 2.0/3)

#
# colorful debug settings
#
#STOKE_BORDER_COLOR   = "#00f"
#STOKE_UNFILLED_COLOR = "#ff0"
#STOKE_FILLING_COLOR  = "#f00"
#STOKE_FILLED_COLOR   = "#000"
#BRUSH_COLOR = "#0ff"
#BRUSH_BORDER_COLOR = "#0f0"