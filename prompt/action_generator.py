PURPOSE = """
Create a new transaction in Money Manager Ex using value in IRA_test.xlsx.
"""

# PURPOSE = """
# Enter "a" into the 'Amount' field.
# """

ANALYZE_REQUEST_STEPS= """
Based on the steps in the knowledge base, give the steps to implement PURPOSE.

{
    "steps": 
    {
        "1":"",
        "2": "",
        ...
        "N": ""
    }
}

"""

ANALYZE_REQUEST= """
Based on the information in the knowledge base, describe how to implement PURPOSE in the interface shown in the picture.

1. Based on the state_transition_caption attribute in the knowledge base, find the same type of action and its action ID required to implement PROPOSE. 
In Excel, click_Element has the following types: buttons with text, cells, and text boxes that can be entered except cells
If the required action_type is in the knowledge base, and this action_type does not contain "CLICK", it can be regarded as an action with the same id. 
If the required action_type contain "CLICK", and the required click_Element and the knowledge base are of the same type, it can be regarded as an action with the same id.
If there is no same action_type or similar click_Element, the action_type and id is "unknow"

2. If the action is "LEFT_CLICK", "click_Element" and "click_Element_type" are returned at the same time, and their values are the element name and element type of the mouse click.
If the action contains "KEY", "key_code" is also returned, and its value is the value required in PURPOSE.

3. Ensure that the order of actions is correct. The action chain must be generated strictly in the order specified by the user. The order of each action is represented by action_index, counting from 1.

4. Return actions in the following json format
    {
        "actions": [
            {
            "action_index":"",
            "action_type": "",
            "id": ,
            (Optional)"key_code": "",
            (Optional)"click_element": "",
            (Optional)"click_element_type": "",
            "description":"",
            }
        ]
    }

"""

ANALYZE_REQUEST_ACTION= """

1. According to the state_transition_caption attribute of actions in the knowledge base, select the action_type and id of the next action to be performed by PURPOSE in the interface shown in the image.
If the action_type of the next step is in the knowledge base and the action_type does not contain "CLICK", it can be regarded as an action with the same ID.
If the next action type contains "CLICK", the click_Element to be clicked includes the following click_Element_type types: buttons with text, cell, and text boxes that can be entered in addition to cells. If the click_Element of the next step is the same type as the knowledge base, it can be regarded as an action with the same ID.
If the next action that can be executed in the image interface is not found in the knowledge base, the id and action_type are "unknow".
If the next action is the last step to complete PURPOSE, the attribute "last_step":"yes"

2. If the action is "LEFT_CLICK", "click_Element" and "click_Element_type" are returned at the same time, and their values are the element name and element type of the mouse click.
If action contains "KEY", "key_code" is also returned, and its value is the value required in PURPOSE, and it is guaranteed that the input position has been selected in the image.

3. Return the following action in json format
{
    "action_type": "",
    "id": ,
    (optional)"key_code": "",
    (optional)"click_element": "",
    (optional)"click_element_type":"",
    "description":"",
    "last_step":""
}

"""


ACTION_VERIFY = """
Whether the current step is executed successfully:{description}
{{
    "executed":"true/false/unable judge",
    "reason":""
}}


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

VERIFY_POSITION_0= """
In Excel, is {element_name} selected?
If one of the following conditions occurs, it can be considered selected:
1. The border becomes thicker or brighter
2. There is a text input cursor inside
3. The text inside is selected
{{
    "{element_name}":
    {{
        "selected": "yes/no" 
    }}
}}

"""

VERIFY_POSITION= """
Is red X inside {element_name}?
{{
    "position":"yes/no"
}}

"""


GET_LABELS = """
Is there {element_name} in the image?
If yes, there are blue numbers on the picture, please find the best blue number in the "{element_name}"
{{
    "{element_name}":
    {{
        "exists": "true/false",
        "grid_cell": ""
    }}
}}
"""

IDENTIFY_TEXT_BOX_LABELS = """
Please identify the red number in the blue box corresponding to the {element_name} in the picture.
{{
    "exists": "true/false",
    "number": ""
}}
"""

GET_TABLE_INITIAL_VALUE = """
Describe the row and column labels of the red X in the cell.
{
    "row":"",
    "column":""
}
"""

DETERMINE_ACTION="""
In Action, select the next action that should be performed to achieve the purpose in the image.
If there is no executable action, return action_index: unknow, and describe the reason. 
{
    "action_index":"",
    "description":""
}

"""

DETERMINE_STEP_0="""
According to the screenshot, select next step in steps to achieve the purpose, and convert this step into the following action format.
If no step can be selected, return step_index, step_description and unknown_reason, and step_index is unknown.
The action_type describes the type of each operation in the step.
The click_Element has the following types: text_button, cell, and text_box that can be entered except cells
If the action_type contains "CLICK", "click_Element" and "click_Element_type" are returned at the same time, and their values are the element name and element type of the mouse click.
If action contains "KEY", "key_code" is also returned, and its value is the value required in PURPOSE, and it is guaranteed that the input position has been selected in the image.
* Important: According to the image select one step!!!
{
    "step_index":"",
    "step_description":"",
    "action_type": "LEFT_CLICK/RIGHT_CLICK/KEY_WRITE/KEY_PRESS/KEY_HOTKEY",
    (optional)"key_code": "",
    (optional)"click_element": "",
    (optional)"click_element_type":"text_button/cell/text_box/unknown",
    (optional)"unknown_reason":""
}

"""

DETERMINE_STEP_0="""
Step:{step} 
According to the screenshot, 
1. Determine whether the current screen can execute this step. 
2. Confirm whether step has been executed. 
{{
    "can_execute":"True/False",
    "executed":"True/False/Unable",
    "description":""
}}

"""

DETERMINE_STEP="""

Can I directly execute the operation {step} on the current screen image?
If the step contains the words "open application" or "switch application", this step can be executed directly and returns True.
{{
    "can_execute":"True/False",
    "reason":""
}}

"""

STEP_TO_ACTION="""
According to the screenshot, convert this step into the format of one or more actions.
Step:{step} 
The action_type describes the type of each operation in the step.
The action_type MUST be limited to the following types: LEFT_CLICK/RIGHT_CLICK/KEY_WRITE/KEY_PRESS/KEY_HOTKEY/KEY_DOWN/KEY_UP/SWITCH(application).
The click_Element has the following types: text_button, cell, and text_box that can be entered except cells
If the action_type contains "CLICK", "key_element" and "key_element_type" are returned at the same time, and their values are the element name and element type of the mouse click.
If action_type contains "KEY", "key_element" is also returned, and its value is the value required in PURPOSE, and it is guaranteed that the input position has been selected in the image.
Before performing an input action, you must ensure that the input box has been selected or a Click action has been performed.
If the action_type is "SWITCH", "key_element" is the name of the application to be switched.
If the action_type is "SCROLL" or "HSCROLL", "key_element" specifies the position of the mouse, and "distance" represents the scroll distance, which can be a positive or negative integer.
{{
    "actions": 
    [
        {{
            "action_index":"",
            "description":"",
            "action_type": "LEFT_CLICK/RIGHT_CLICK/KEY_WRITE/KEY_PRESS/KEY_HOTKEY/KEY_DOWN/KEY_UP/SWITCH/SCROLL/HSCROLL",
            "key_element": "",
            "key_element_type":"text_button/cell/input_box/unknown",
            "distance": ""
        }}
    ]
    
}}

"""


