import cv2
import numpy as np

class ImageEditor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.load_image()
        
    def load_image(self):
        self.image = cv2.imread(self.image_path)
        if self.image is None:
            raise ValueError(f"Unable to load image, please check the path: {self.image_path}")
        
    def mark_text_box(self, save_path):
        self.load_image()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
            # 使用 OTSU 阈值方法
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # 使用 RETR_TREE 提取所有轮廓
        contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        input_boxes = []
        
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            (x, y, w, h) = cv2.boundingRect(approx)
            
            # 过滤掉面积过小的轮廓
            if cv2.contourArea(cnt) > 100 and w > 10 and h > 30: 
                input_boxes.append((x, y, w, h))

        
    
        unique_boxes = []

        for box in input_boxes:
            if not any(is_overlap(box, other_box) for other_box in unique_boxes):
                unique_boxes.append(box)
        
        box_number = 0

        for (x, y, w, h) in unique_boxes:
            cv2.rectangle(self.image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            
            circled_char = str(box_number) 
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            text_color = (0, 0, 255)  
            circle_color = (0, 0, 255)  
            thickness = 2
            
            (text_w, text_h), _ = cv2.getTextSize(circled_char, font, font_scale, thickness)
            radius = max(text_w, text_h) // 2 + 5 
            text_x = x 
            text_y = y + h - radius - 15  
            
            cv2.putText(
                self.image, circled_char,
                (text_x + radius - text_w//2, text_y + radius + text_h//2),
                font, font_scale,
                text_color, thickness,
                cv2.LINE_AA
            )

            box_number += 1
            
        cv2.imwrite(save_path, self.image)
        return unique_boxes
    
    def detect_table_lines(self, save_path):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        border_size = 0
        height, width = thresh.shape
        cropped_thresh = thresh[border_size:height-border_size, border_size:width-border_size]

        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))  # 水平核
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))  # 垂直核
        horizontal = cv2.morphologyEx(cropped_thresh, cv2.MORPH_OPEN, kernel_h)
        vertical = cv2.morphologyEx(cropped_thresh, cv2.MORPH_OPEN, kernel_v)
        table_lines = cv2.add(horizontal, vertical)
        
        lines = cv2.HoughLinesP(table_lines, 1, np.pi/180, 100, minLineLength=300, maxLineGap=10)
        
        # contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # largest_contour = max(contours, key=cv2.contourArea)
        # x, y, w, h = cv2.boundingRect(largest_contour)

        horizontal, vertical = merge_lines(lines)

        mask_horizontal = lines_to_mask((1400, 2240), horizontal, thickness=2)
        mask_vertical = lines_to_mask((1400, 2240), vertical, thickness=2)

        table_lines = cv2.add(mask_horizontal, mask_vertical)

        contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        horizontal_table = []
        vertical_table = []

        for line in horizontal:
            x1, y1, x2, y2 = line
            if (x1 >= x and x2 <= x+w and y1 >= y and y2 <= y+h and (x2 - x1)> w/2):
                horizontal_table.append((x, y1, x+w, y2))
                cv2.line(self.image, (x, y1), (x+w, y2), (255, 0, 0), 2)
        for line in vertical:
            x1, y1, x2, y2 = line
            if (x1 >= x and x2 <= x+w and y1 >= y and y2 <= y+h and  (y2 - y1)> h/2):
                vertical_table.append((x1, y, x2, y+h))
                cv2.line(self.image, (x1, y), (x2, y+h), (255, 0, 0), 2)

        horizontal_table.sort(key=lambda x: x[1])
        vertical_table.sort(key=lambda x: x[0])

        # contours, _ = cv2.findContours(table_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # largest_contour = max(contours, key=cv2.contourArea)
        # x, y, w, h = cv2.boundingRect(largest_contour)
        # table_roi = img[y:y+h, x:x+w]

        cv2.imwrite(save_path, self.image)
        return horizontal_table, vertical_table

    
    def draw_grid_and_labels(self, save_path, label_offset):
        self.load_image()

        height, width = self.image.shape[:2]

        alpha = 0.20 
        cols = 35
        rows = 55
        resize_width = width // 2
        resize_height = height // 2
        font_size = 0.15

        stepx = resize_width / cols
        stepy = resize_height / rows

        img_resize  = cv2.resize(self.image,(resize_width,resize_height))
        gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        overlay = gray_bgr.copy()

        num_cols = cols
        num_rows = rows

        
        for i in range(num_rows+3):
            for j in range(num_cols+3):
                center_x = int(j * stepx + stepx // 2 - label_offset * 5)
                center_y = int(i * stepy + stepy // 2 - label_offset * 5)
                label = f"{j + i * num_cols}"
                cv2.putText(overlay, label, (center_x - 3, center_y + 1),
                            cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                # if(j + i * cols == 621) :
                #     print(i)
        
        final_image = cv2.addWeighted(overlay, alpha, gray_bgr, 1 - alpha, 0)
        
        cv2.imwrite(save_path, final_image)
        
        return cols, rows
    

    def labels_to_position(self, cols, rows, grid_cell, label_offset):

        self.load_image()

        height, width = self.image.shape[:2]

        stepx = width / cols
        stepy = height / rows

        num_cols = cols
        # num_rows = rows + 3

        i = grid_cell // num_cols
        j = grid_cell % num_cols

        center_x = int(j * stepx + stepx // 2 - label_offset * 10)
        center_y = int(i * stepy + stepy // 2 - label_offset * 10)

        return center_x, center_y
    
    def add_X(self, x, y, radius, save_path):
        # Reload the original image to prevent overlapping drawings
        self.load_image()

        # Convert the image to grayscale
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Convert grayscale image back to BGR to draw colored shapes
        self.image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

        # Define red color in BGR format
        red = (0, 0, 255)
        thickness = 2  # Adjust line thickness as needed

        # Draw the diagonal lines forming the "X"
        cv2.line(self.image, (x - radius, y - radius), (x + radius, y + radius), red, thickness)
        cv2.line(self.image, (x - radius, y + radius), (x + radius, y - radius), red, thickness)

        # Resize the image if necessary
        height, width = self.image.shape[:2]
        resize_width = width
        resize_height = height
        img_resize = cv2.resize(self.image, (resize_width, resize_height))

        # Save the modified image
        cv2.imwrite(save_path, img_resize)

        return save_path
        
    def get_image_size(self):
        self.load_image()
        return self.image.shape[:2]



def merge_lines(lines, angle_threshold=10, merge_threshold=1):
    horizontal = []
    vertical = []
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        angle = np.degrees(np.arctan2(abs(dy), abs(dx)) if dx != 0 else np.pi/2)
        
        if angle < angle_threshold or angle > 180 - angle_threshold:
            horizontal.append(line[0])
        elif 90 - angle_threshold < angle < 90 + angle_threshold:
            vertical.append(line[0])
    
    horizontal_sorted = sorted(horizontal, key=lambda x: (x[1] + x[3])/2)
    merged_h = []
    current_group = []
    
    for line in horizontal_sorted:
        y_center = (line[1] + line[3])/2
        if not current_group:
            current_group.append(line)
        else:
            last_y = (current_group[-1][1] + current_group[-1][3])/2
            if abs(y_center - last_y) <= merge_threshold:
                current_group.append(line)
            else:
                merged_h.append(current_group)
                current_group = [line]
    if current_group:
        merged_h.append(current_group)
    
    final_horizontal = []
    for group in merged_h:
        min_x = min(min(line[0], line[2]) for line in group)
        max_x = max(max(line[0], line[2]) for line in group)
        avg_y = int(np.mean([(line[1] + line[3])/2 for line in group]))
        final_horizontal.append([min_x, avg_y, max_x, avg_y])
     
    vertical_sorted = sorted(vertical, key=lambda x: (x[0] + x[2])/2)
    merged_v = []
    current_group = []
    
    for line in vertical_sorted:
        x_center = (line[0] + line[2])/2
        if not current_group:
            current_group.append(line)
        else:
            last_x = (current_group[-1][0] + current_group[-1][2])/2
            if abs(x_center - last_x) <= merge_threshold:
                current_group.append(line)
            else:
                merged_v.append(current_group)
                current_group = [line]
    if current_group:
        merged_v.append(current_group)
    
    final_vertical = []
    for group in merged_v:
        min_y = min(min(line[1], line[3]) for line in group)
        max_y = max(max(line[1], line[3]) for line in group)
        avg_x = int(np.mean([(line[0] + line[2])/2 for line in group]))
        final_vertical.append([avg_x, min_y, avg_x, max_y])
    
    return final_horizontal, final_vertical

def lines_to_mask(image_shape, lines, thickness=2):
    mask = np.zeros(image_shape, dtype=np.uint8)  
    for line in lines:
        x1, y1, x2, y2 = line
        cv2.line(mask, (x1, y1), (x2, y2), color=255, thickness=thickness)
    return mask

def is_overlap(box1, box2, threshold=0.5):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    overlap_area = x_overlap * y_overlap

    area1 = w1 * h1
    area2 = w2 * h2

    iou = overlap_area / float(area1 + area2 - overlap_area)

    return iou > threshold

# folder_path = "log\\screenshot\\0430130056\\screenshot_2_flow_steps_2.png"
# save_path = "log\\screenshot\\0430130536\\screenshot_2_flow_steps_2.png"
# image = ImageEditor(folder_path)
# image.mark_text_box(save_path)





    



    