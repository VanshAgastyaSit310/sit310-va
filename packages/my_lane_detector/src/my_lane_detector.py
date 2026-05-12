#!/usr/bin/env python3

import numpy as np
import cv2
from cv_bridge import CvBridge
import rospy
from sensor_msgs.msg import CompressedImage


class Lane_Detector:
    def __init__(self):
        self.cv_bridge = CvBridge()

        # CHANGE THIS TOPIC NAME AFTER CHECKING rostopic list
        self.image_topic = "/camera_node/image/compressed"
        # Example alternative:
        # self.image_topic = "/mybot/camera_node/image/compressed"

        rospy.init_node("my_lane_detector", anonymous=True)
        self.image_sub = rospy.Subscriber(
            self.image_topic,
            CompressedImage,
            self.image_callback,
            queue_size=1
        )

        rospy.loginfo(f"Subscribed to: {self.image_topic}")

    def output_lines(self, original_image, lines, color=(255, 0, 0)):
        output = np.copy(original_image)

        if lines is not None:
            for i in range(len(lines)):
                l = lines[i][0]
                cv2.line(output, (l[0], l[1]), (l[2], l[3]), color, 2, cv2.LINE_AA)
                cv2.circle(output, (l[0], l[1]), 3, (0, 255, 0), -1)
                cv2.circle(output, (l[2], l[3]), 3, (0, 0, 255), -1)

        return output

    def image_callback(self, msg):
        # Convert ROS compressed image to OpenCV BGR image
        img = self.cv_bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

        # Optional: flip if your bag images appear upside down
        # Comment this out if the image orientation already looks correct
        img = cv2.flip(img, 0)

        # -----------------------------
        # 1. Crop image to road region
        # -----------------------------
        height, width, _ = img.shape

        # Keep lower half / lower region where road is visible
        crop_y_start = int(height * 0.5)
        crop = img[crop_y_start:height, 0:width]

        # -----------------------------------
        # 2. Convert cropped image to HSV
        # -----------------------------------
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # ------------------------------------------------
        # 3. White color filtering (lane boundary markers)
        # ------------------------------------------------
        lower_white = np.array([0, 0, 180], dtype=np.uint8)
        upper_white = np.array([180, 80, 255], dtype=np.uint8)
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        white_filtered = cv2.bitwise_and(crop, crop, mask=white_mask)

        # ------------------------------------------------
        # 4. Yellow color filtering (dashed center lines)
        # ------------------------------------------------
        lower_yellow = np.array([15, 80, 80], dtype=np.uint8)
        upper_yellow = np.array([40, 255, 255], dtype=np.uint8)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        yellow_filtered = cv2.bitwise_and(crop, crop, mask=yellow_mask)

        # Morphological cleanup to reduce noise
        kernel = np.ones((5, 5), np.uint8)
        white_mask = cv2.erode(white_mask, kernel, iterations=1)
        white_mask = cv2.dilate(white_mask, kernel, iterations=1)

        yellow_mask = cv2.erode(yellow_mask, kernel, iterations=1)
        yellow_mask = cv2.dilate(yellow_mask, kernel, iterations=1)

        # ------------------------------------------------
        # 5. Canny Edge Detector on cropped image
        # ------------------------------------------------
        gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_crop, 50, 150)

        # ------------------------------------------------
        # 6. Hough Transform on white-filtered image
        # ------------------------------------------------
        white_edges = cv2.Canny(white_mask, 50, 150)
        white_lines = cv2.HoughLinesP(
            white_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=30,
            minLineLength=20,
            maxLineGap=10
        )

        # ------------------------------------------------
        # 7. Hough Transform on yellow-filtered image
        # ------------------------------------------------
        yellow_edges = cv2.Canny(yellow_mask, 50, 150)
        yellow_lines = cv2.HoughLinesP(
            yellow_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=20,
            minLineLength=15,
            maxLineGap=10
        )

        # ------------------------------------------------
        # 8. Draw detected lines on cropped image
        # ------------------------------------------------
        output = np.copy(crop)

        # Draw white lines in blue
        output = self.output_lines(output, white_lines, color=(255, 0, 0))

        # Draw yellow lines in red
        output = self.output_lines(output, yellow_lines, color=(0, 0, 255))

        # ------------------------------------------------
        # Convert processed HSV images back to BGR/RGB view
        # for demonstration, as requested by the lab sheet
        # ------------------------------------------------
        hsv_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # Show results
        cv2.imshow("1_cropped_image", crop)
        cv2.imshow("2_hsv_to_bgr_demo", hsv_bgr)
        cv2.imshow("3_white_filtered", white_filtered)
        cv2.imshow("4_yellow_filtered", yellow_filtered)
        cv2.imshow("5_canny_edges", edges)
        cv2.imshow("6_white_hough_input_edges", white_edges)
        cv2.imshow("7_yellow_hough_input_edges", yellow_edges)
        cv2.imshow("8_final_output_lines", output)

        cv2.waitKey(1)

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        lane_detector = Lane_Detector()
        lane_detector.run()
    except rospy.ROSInterruptException:
        pass
