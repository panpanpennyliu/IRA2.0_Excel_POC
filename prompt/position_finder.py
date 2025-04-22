CORRECT_COORDINATE_0 = """
I want to perform click action on my computer
The action description is:
 {action_description}
I have an approximate coordinate location ({x},{y}), based on which I found several clickable targets. I've marked the clickable areas with green(#00FF00) rectangles. Can you help me determine the correct rectangle ID?
{response_format}

"""


INITIAL_COORDINATE = """
The upper left corner of the image is (0, 0) and the lower right corner is (2240, 1400). Please give the coordinate (x, y) of the center of {element_name}.
{{
    "x":"",
    "y":""
}}

"""
CORRECT_COORDINATE = """
I marked some areas with green (#00FF00) rectangles. Please select the {element_name} area number.

{{
    "Number":""
}}

"""
