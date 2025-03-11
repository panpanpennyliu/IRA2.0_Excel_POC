GENERATE_CONCEPT_JSON_REQUEST = """
Analyze the frame image and extract relavate data to JSON format.
"""

GENERATE_CONCEPT_JSON_BACKGROUND = """
You are a data analyst specializing in image processing and data extraction from video frames, alway deliver best quality outputs. 
"""

GENERATE_CONCEPT_JSON_KNOWLEDGE = """
Follow below steps to process the frame image:

1. **Extract Picture Info**: Create a JSON object field named "picture_information" to store the image information for given frame '{frame_file_name}' with relative attributes. The frame file name is composed of several parts, and each part is separated by a vertical bar'|'. All the attributes can be extracted from the file name, and each attribute is one part of it. Be carefully to extract each part accurately.
- **id**: The sequence ID of the frame image, which can be extracted from the first part of the file name.
- **action**: The action performed on the frame. Set the value based on the second part of the file name. Return 'LEFT_CLICK' for 'Click'; Return 'KEY_PRESS' for 'Press'; Return 'KEY_DOWN' for 'Down'; Return 'KEY_UP' for 'Up'.
- **applicationTitle**: The title of the operated application. It's the third part of the file name. Output it in its original format, ensuring that all characters, including special characters and the order of words, are exactly the same as in the orinigal file name. 
- **windowLeftUpperPoint**: The left-upper point of the current frame window. Extracted from the fourth part of the file name. Replace '.' with ',' for the value.
- **windowRightBottomPoint**: The right-bottom point of the current frame window. Extracted from the fifth part of the file name. Replace '.' with ',' for the value.
- **mousePoint**: Add this attribute when the second part is 'Click'. Set value with the last part of the file name. Replace '.' with ',' if it exists in the value.
- **keyCode**: Add this attribute when the second part is not 'Click'. Set value with the last part of the file name.

2. **Generate Dense Caption**: Analyze the visual elements, layout, and styling on the frame image. Generate this information into an new attribute named "dense_caption".

3. **Populate Element Description**: Extract the detailed information of each element from the frame image and store it in an new object named "element_description". This object contains the following attributes:
	- **visial_description**: Record the the visual appearance of the element, including it's shape, color, text content, and visible styling details.
	- **position_information**: Record the spatial location of the element with the relationship to other elements in the image using clear directional and relational terms.
	- **element_function**: Determine the element's probable function and how users would typically interact with it in the interface.
	- **element_type**: Clarify the UI control type (such as button, text field, dropdown) for the actioned element, using standard Windows/UI control terminology.

4. **Determine Video ID**: Create a new attribute named "video_id" and set value as '{video_folder}'. 

**Process type selection**: Select proper function to process each step based on the type value.
- **Extract Picture Info: text
- **Generate Dense Caption: image
- **Populate Element Description: image
- **Determin Video ID: text

**Model selectionv: Select proper AI modle to do each step.
- **Extract Picture Info: gpt-4o-mini
- **Generate Dense Caption: gemini-1.5-flash-002
- **Populate Element Description: gemini-1.5-flash-002
- **Determin Video ID: gpt-4o-mini
"""

GENERATE_ACTION_DESCRIPTION_REQUEST = """
Generate a concise action description from the frame's extracted picture info in one short sentence including action type, actioned value, and operated application, and save as "action_description" in JSON format.
"""

GENERATE_STATE_TRANSITION_REQUEST = """
Extract state transition information into an attribute "state_transition_caption" in the json format as the output. By comparing the previous frame image and current frame image, describe what has changed and what user interaction likely occurred between them, as describing a scene transition in a movie.
Rquirements:
- **frame_change**: Describe what was shown in last frame screenshot and what changed in current frame screenshot
- **user_action**: Explain what user action most likely happened in between, combining the action info extracted in 'picture_information' attribute.
"""

COMPILE_FRAME_JSON_REQUEST="""
Compile all the attributes for each frame into a single JSON object named 'frame' as the output.
"""

COMPILE_VIDEO_ID_REQUEST="""
Create a new JSON attribute named "video_id" and set its value with '{video_folder}' in the JSON output.
"""

COMPILE_CONCEPT_JSON_REQUEST="""
Merge the JSON date for each frame into a single JSON array named 'conceptJson' as the output. Keep attributes of diffrent frames separate. Place each frame's attributes directly under 'conceptJson', without any intermediate field. 
"""

GENERATE_CONCEPT_JSON_KNOWLEDGE0 = """
To analyze from frame pictures in a folder and extract data to make a JSON
1. **Identify the parent folder containing subfolders named by the video name for each subfolder. 
2. **Read and analyze frame image files from subfolders.
3. **Extract relevant data from the file names to populate the attribute "picture_info".
4. **Process the screen content of each frame image to extract the attribute "screen_data".
5. **Extract the video ID form the subfodler name to populate the attribute "video_id".
6. **Generate a step descriptoin based on the action and context to populate the attribute "step_description".
7. **Compile the extracted data into a JSON string.

Example subfodler name: "H18FAFI12PS0000_10.14.190.37_pl12345_1719822686609_outputfiles"
Example frame image file names:
- "297____Click____FLEXCUBE4.9TransactionInput____-8.-8_2568.1408____293.11.png"
- "8982____Down____Test.xlsx-Excel____-8.-8_2568.1408____Ctrl.png"

Example JOSN structure:
{
    "conceptJson":[
        {
            "picture_info": {
                "windowRightBottomPoint": "2560,1408",
                "applicationTitle": "FLEXCUBE4.9TransactionInput",
                "windowLeftUpperPoint": "0,0",
                "mousePoint": "293,11",
                "relativeMouseClickPoint": "1,1",
                "action": "LEFT_CLICK",
                "id": 297
            },
            "dense_caption":"",
            "element_desc": {
                "visial_desc":"",
                "position_info":"",
                "element_func":"",
                "element_type":""         
            },
            "state_transition_caption":"",
            "video_id": "H18FAFI12PS0000_10.14.190.37_pl12345_1719822686609"
        },
        {
            "picture_info": {
                "keyCode": "Ctrl"
                "windowRightBottomPoint": "2560,1408",
                "windowLeftUpperPoint": "0,0",
                "action": "KEY_DOWN",
                "id": 8982
            },
            "dense_caption":"",
            "element_desc": {
                "visial_desc":"",
                "position_info":"",
                "element_func":"",
                "element_type":""         
            },
            "state_transition_caption":"",
            "video_id": "H18FAFI12PS0000_10.14.190.37_pl12345_1719822686609"
        }
    ]
}
"""

GENERATE_CONCEPT_JSON_KNOWLEDGE_bk = """
Follow below steps to process each individual frame image:
1. **Extract Picture Info: Create a JSON object field named "picture_information". Extract its attributes based on the file name of the frame image '{frame_image}'. There are two types of operations: mouse operation and keyboard operation.
	Here are examples:
	1) Example for mouse operation file name: 297____Click____FLEXCUBE4.9TransactionInput____-8.-8_2568.1408____293.11.png
		Resulting attributes values:
			"windowRightBottomPoint": "2560,1408",
			"applicationTitle": "FLEXCUBE4.9TransactionInput",
			"windowLeftUpperPoint": "0,0",
			"mousePoint": "293,11",
			"relativeMouseClickPoint": "1,1",
			"action": "LEFT_CLICK",
			"id": 297	
	2) Example for keyboard operation file name: 8982____Down____Test.xlsx-Excel____-8.-8_2568.1408____Ctrl.png
		Resulting attributes values:
			"keyCode": "Ctrl"
			"windowRightBottomPoint": "2560,1408",
            "applicationTitle": "Test.xlsx-Excel",
			"windowLeftUpperPoint": "0,0",
			"action": "KEY_DOWN",
			"id": 8982
		
2. **Generate Dense Caption: Analyze the visual elements, layout, and styling on the frame image. Generate this information into an new attribute named "dense_caption".

3. **Populate Element Description: Extract the detailed information of each element from the frame image and store it in an new object named "element_description". This object contains the following attributes:
	1) visial_description: Record the the visual appearance of the element, including it's shape, color, text content, and visible styling details.
	2) position_information: Record the spatial location of the element with the relationship to other elements in the image using clear directional and relational terms.
	3) element_function: Determine the element's probable function and how users would typically interact with it in the interface.
	4) element_type: Clarify the UI control type (such as button, text field, dropdown) for the actioned element, using standard Windows/UI control terminology.

4. **Extract State Transition Information: Create a separate field "state_transition_caption" in the JSON data. By comparing the previous frame image and current frame image, describe what has changed and what user interaction likely occurred between them, as describing a scene transition in a movie.
	Rquirements:
	1) Describe what was shown in last frame screenshot
    2) Describe what changed in current frame screenshot
    3) Explain what user action most likely happened in between.

5. **Determine Video ID: Identify the folder name from the frame image path '{frame_image}' that is located between the last two slashes and closest to file name, to save into a new attribute named "video_id". For example, return "TEST_10.14.190.37_ab12345_1719822600609_outputfiles" if the path is like "..\\TEST_10.14.190.37_ab12345_1719822600609_outputfiles\\300____Press____Test.xlsx-Excel____0.0_2557.1379____S.png"

Process type selection: Select proper function to process each step based on the type value.
1) Extract Picture Info: text
2) Generate Dense Caption: image
3) Populate Element Description：image
4) Extract State Transition Information：text
5) Determin Video ID：text

Model selection: Select proper AI modle to do each step.
1) Extract Picture Info: gpt-4o-mini
2) Generate Dense Caption:gemini-1.5-flash-002
3) Populate Element Description：gemini-1.5-flash-002
4) Extract State Transition Information：gpt-4o-mini
5) Determin Video ID：gpt-4o-mini
"""