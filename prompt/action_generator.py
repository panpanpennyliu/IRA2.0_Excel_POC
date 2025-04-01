PURPOSE = """
1.Enter the character '2' in cell G15 in Sheet2 of the excel file.
2.Save the excel.
"""

ANALYZE_REQUEST= """
Based on the information in the knowledge base, describe how to implement PURPOSE in the Excel interface.

1. Find the same type of action and action id required to implement PROPOSE based on the state_transition_caption in the knowledge base. If you cannot find a required action in the knowledge base, you need to name the required action, and the value of action id is "waiting to be added".

2. Ensure that the order of actions is correct. The action chain must be generated strictly in the order specified by the user. The order of each action is represented by action_index, counting from 1.

3. If the action is "LEFT_CLICK", "click_Element" is also returned, and its value is the name of the element clicked by the mouse.
If the action contains "KEY", "key_code" is also returned, and its value is the value required in PURPOSE.

4. Return actions in the following json format
    {
        "actions": [
            {
            "action_index":"",
            "action": "",
            "id": ,
            (Optional)"key_code": "",
            (Optional)"click_Element": "",
            "description":"",
            }
        ]
    }

"""


GET_INITIAL_POSITION="""
Image size of image_url is 2240*1400. The upper left corner is (0, 0)
Give me the pixel coordinates (x,y) for the center of {element_name} in this image. 
Coordinates should preferably be multiples of 10.
The output should be a JSON array containing the object name and coordinate. Ensure the bounding boxes accurately encapsulate the object and the coordinates are exact.
Important: Only return the below json.
{{
    "name": "",
    "coordinate": "(?, ?)"
}}


"""


MOVE_POSITION= """
Image size of image_url is 2240*1400. The upper left corner is (0, 0)

The position of RGB element in the image has been updated.
Are there any RGB(255, 0, 0) elements in the image?  
If yes, describe the shape of the element.

Is there {element_name} in the image? 
If yes, provide accurately description of the detail positional relationship between the center of RGB (0,0,255) element and the center of {element_name} of Excel, such as: the RGB element is x pixels left/right and y pixels above/below the center of {element_name}.

Important: 
If the center of RGB element is inside {element_name}, the description should return "the RGB element is 0 pixels left/right and 0 pixels above/below of {element_name}"
Use pixels as the unit of measurement. Only return the below json.

{{
    "RGB elements": 
    {{
        "exists": true/false,
        "shape": ""
    }},
    "{element_name}": 
    {{
        "exists": true/false,
        "description":"the RGB element is x pixels left/right and y pixels above/below the center of {element_name}"
    }}
}}

"""

VARIFY_POSITION= """

Is there any blue element totally inside the {element_name} of the Excel?
If yes, please describe the shape of the element. 
Important: If the blue element is not completely inside {element_name}, return no.

{{
    "{element_name}":
    {{
        "RGB_element completely inside {element_name}":"yes/no",
        "shape": "" 
    }}
}}

"""


GET_LABELS = """
The first row label is at the front of the cell, and the column label is at the top, which is not part of the cell.
Is there {element_name} in the image?
If yes, there are blue numbers on the picture, please find the blue number in the "{element_name}"
{{
    "{element_name}":
    {{
        "exists": "true/false",
        "grid_cell": ""
    }}
}}
"""