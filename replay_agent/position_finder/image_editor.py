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
        cols = 40
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

        
        for i in range(rows + 1):
            for j in range(cols + 1):
                center_x = int(j * stepx + stepx // 2 )
                center_y = int(i * stepy + stepy // 2 )
                label = f"{j + i * cols}"
                cv2.putText(overlay, label, (center_x, center_y),
                            cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 0, 0), thickness=1, lineType=cv2.LINE_AA)
        
        final_image = cv2.addWeighted(overlay, alpha, gray_bgr, 1 - alpha, 0)
        
        cv2.imwrite(save_path, final_image)
        
        return cols, rows
    

    def labels_to_position(self, cols, rows, grid_cell, label_offset):

        self.load_image()

        height, width = self.image.shape[:2]

        stepx = width / cols
        stepy = height / rows

        i = grid_cell // cols
        j = grid_cell % cols

        center_x = int(j * stepx + stepx // 2 )
        center_y = int(i * stepy + stepy // 2 )

        return center_x, center_y






    



    