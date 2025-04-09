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
        
        thresh = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        input_boxes = []
        i = 0
        
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, min(30, peri * 0.05), True)
            (x, y, w, h) = cv2.boundingRect(approx)

            if len(approx) == 4 and w > 30 and h > 30:
                input_boxes.append((x, y, w, h))
                i += 1

        box_number = 0

        for (x, y, w, h) in input_boxes:
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
            
            # cv2.circle(
            #     img,
            #     (text_x + radius, text_y + radius),
            #     radius,
            #     circle_color,
            #     2  # 填充
            # )
            
            cv2.putText(
                self.image, circled_char,
                (text_x + radius - text_w//2, text_y + radius + text_h//2),
                font, font_scale,
                text_color, thickness,
                cv2.LINE_AA
            )

            box_number += 1
            
        cv2.imwrite(save_path, self.image)
        return input_boxes
    
    def add_star(self, x, y):
        self.load_image()
        center = (x, y)
        radius = 10
        points = []
        for i in range(5):
            angle = np.deg2rad(i * 72 - 90)  
            a = int(center[0] + radius * np.cos(angle))
            b = int(center[1] + radius * np.sin(angle))
            points.append((a, b))
        star_points = np.array([
            points[0], points[2], points[4], points[1], points[3]
        ], np.int32)

        cv2.polylines(self.image, [star_points], isClosed=True, color=(255, 0, 0), thickness=2)

        # text = "("+ str( x ) +", " + str( y )+")"
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # font_scale = 0.5
        # text_thickness = 2
        # text_color =  (180, 105, 255) 
        # cv2.putText(image, text, (center[0] + 20, center[1]), font, font_scale, text_color, text_thickness)

        save_path = "input\screenshot\mark_1.png"
        cv2.imwrite(save_path, self.image)
        return save_path
    
    def add_circle(self, x, y, radius, save_path):
        self.load_image()
        
        center = (x, y)  

        color = (255, 0, 0) 
        thickness = -1     

        cv2.circle(self.image, center, radius, color, thickness)

        height, width = self.image.shape[:2]
        resize_width = width // 2
        resize_height = height // 2

        img_resize  = cv2.resize(self.image,(resize_width,resize_height))

        cv2.imwrite(save_path, img_resize)


        return save_path
    

    def add_square(self, x, y, half_side):
        """
        在图片上以 (x, y) 为中心，绘制一个边长为 2 * half_side 的实心正方形
        :param x: 中心点x坐标
        :param y: 中心点y坐标
        :param half_side: 正方形半边长
        """
        # 重新加载原始图片，确保操作在未修改图片上进行
        self.load_image()
        
        # 计算正方形的左上角和右下角坐标
        top_left = (x - half_side, y - half_side)
        bottom_right = (x + half_side, y + half_side)
        
        # 指定颜色和填充：在OpenCV中，(255, 0, 0) 表示蓝色（BGR格式）
        color =  (255, 0, 0)
        thickness = 3  # -1 表示填充
        
        # 绘制实心正方形
        cv2.rectangle(self.image, top_left, bottom_right, color, thickness)
        
        # 保存图片（请注意路径中的反斜杠需进行转义或使用原始字符串）
        save_path = "input\\screenshot\\mark_1.png"
        cv2.imwrite(save_path, self.image)
        return save_path
    
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
        # 重新加载原图，防止叠加绘制
        self.load_image()
        
        # 红色在 BGR 格式中表示为 (0, 0, 255)
        red = (0, 0, 255)
        thickness = 2  # 可根据需要调整线宽

        # 绘制从左上到右下的对角线
        cv2.line(self.image, (x - radius, y - radius), (x + radius, y + radius), red, thickness)
        # 绘制从左下到右上的对角线
        cv2.line(self.image, (x - radius, y + radius), (x + radius, y - radius), red, thickness)
        
        height, width = self.image.shape[:2]
        resize_width = width 
        resize_height = height 

        img_resize  = cv2.resize(self.image,(resize_width,resize_height))

        cv2.imwrite(save_path, img_resize)

        return save_path







    



    