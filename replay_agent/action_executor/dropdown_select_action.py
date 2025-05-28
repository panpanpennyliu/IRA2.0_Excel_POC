import easyocr
import pyautogui
import time
import cv2
import numpy as np
from PIL import ImageGrab
from utils.logger.logger_setup_data_extraction import logger

SCROLL_AMOUNT = 150  # Number of pixels to scroll each time
SCROLL_MAX = 20  # Maximum number of scroll attempts

# Initialize the OCR reader with specified languages (Chinese + English)
reader = easyocr.Reader(['en'])

def select_dropdown_option(dropdown_x, dropdown_y, target_option_text, scroll_amount=SCROLL_AMOUNT, max_scrolls=SCROLL_MAX):
    """
    Click on a dropdown and select the target option
    
    Args:
        dropdown_x, dropdown_y: Coordinates of the dropdown
        target_option_text: The text of the target option to select
        scroll_amount: Number of pixels to scroll each time
        max_scrolls: Maximum number of scroll attempts
    """
    logger.info(f"Clicking on dropdown at specified coordinates: ({dropdown_x}, {dropdown_y})")
    
    # Click on the dropdown
    pyautogui.moveTo(dropdown_x, dropdown_y, duration=0.5)
    region = get_dropdown_area(dropdown_x, dropdown_y)  # Get the dropdown area
    
    if region:
        scroll_amount = region[3] // 2  # Adjust scroll amount based on dropdown height

    # Attempt to find the target option, scrolling if necessary
    for scroll_count in range(max_scrolls + 1):
        logger.info(f"Attempting to find option (scroll {scroll_count}/{max_scrolls}): {target_option_text}")
        
        # Look for the target option
        option_location = locate_element_on_screen(target_option_text, region=region)
        
        if option_location:
            logger.info(f"Target option found at coordinates: {option_location}")
            pyautogui.moveTo(option_location[0], option_location[1], duration=0.5)
            pyautogui.click()
            logger.info(f"Option selected: {target_option_text}")
            return True
        
        # If not found, scroll down
        if scroll_count < max_scrolls:
            logger.info(f"Option not found, scrolling down {scroll_amount} pixels")
            pyautogui.scroll(-scroll_amount)
            time.sleep(0.5)
    
    logger.info(f"Option not found after {max_scrolls} scrolls: {target_option_text}")
    return False



def locate_element_on_screen(target_text, region=None, threshold=0.5):
    """
    Locate an element containing the specified text on the screen
    
    Args:
        target_text: The target text to search for
        region: The search region in the format (left, top, width, height)
        threshold: The confidence threshold for text recognition
    
    Returns:
        The center coordinates (x, y) of the element, or None if not found
    """
    # Capture the screen
    screenshot = ImageGrab.grab(bbox=None)
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Use EasyOCR to recognize text
    results = reader.readtext(screenshot_cv)
    
    # Search for matching text
    for (bbox, text, confidence) in results:
        if target_text == text and confidence >= threshold:
            # Get the center of the bounding box
            (top_left, top_right, bottom_right, bottom_left) = bbox
            center_x = (top_left[0] + bottom_right[0]) / 2
            center_y = (top_left[1] + bottom_right[1]) / 2
            if region:
                # If a search region is specified, check if the center is within the region
                if (region[0] <= center_x <= region[0] + region[2] and
                    region[1] <= center_y <= region[1] + region[3]):
                    # Return the center coordinates
                    return (center_x, center_y)
            else:
                # If no region is specified, return the center coordinates directly
                return (center_x, center_y)
    
    return None


def capture_screenshot():
    """Capture the current screen and return an image in OpenCV format"""
    screenshot = ImageGrab.grab()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def detect_dropdown_area(before_img, after_img, click_x, click_y, threshold=30):
    """Detect the dropdown area
    
    Args:
        before_img: Image before clicking
        after_img: Image after clicking
        click_x, click_y: Coordinates of the click position
        threshold: Image difference threshold
    
    Returns:
        Bounding box of the dropdown (x, y, width, height)
    """
    # Ensure both images have the same dimensions
    if before_img.shape != after_img.shape:
        after_img = cv2.resize(after_img, (before_img.shape[1], before_img.shape[0]))
    
    # Calculate image difference
    diff = cv2.absdiff(before_img, after_img)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    # Apply morphological operations to reduce noise
    kernel = np.ones((5,5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the contour that contains the click position
    dropdown_contour = None
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if x <= click_x <= x + w and y <= click_y <= y + h:
            dropdown_contour = contour
            break
    
    # If no contour contains the click position, try to find the largest contour
    if dropdown_contour is None and contours:
        dropdown_contour = max(contours, key=lambda c: cv2.contourArea(c))
    
    if dropdown_contour is not None:
        return cv2.boundingRect(dropdown_contour)
    else:
        return None

def get_dropdown_area(click_x, click_y):    
    # Capture the screen before clicking
    logger.info("Preparing to capture screen... Please ensure the dropdown is not expanded")
    time.sleep(2)
    before_img = capture_screenshot()
    
    # Click on the dropdown
    logger.info(f"Clicking at coordinates ({click_x}, {click_y}) in 2 seconds")
    time.sleep(2)
    pyautogui.click(click_x, click_y)
    time.sleep(0.5)
    
    # Capture the screen after clicking
    after_img = capture_screenshot()
    
    # Detect the dropdown area
    bbox = detect_dropdown_area(before_img, after_img, click_x, click_y)
    
    if bbox is not None:
        x, y, w, h = bbox
        logger.info(f"Dropdown area detected: x={x}, y={y}, width={w}, height={h}")
        return bbox
    else:
        logger.info("Dropdown area not detected. Please check image differences or adjust the threshold")
        return None    