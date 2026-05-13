#!/usr/bin/env python3

import numpy as np
import cv2
from cv_bridge import CvBridge
import rospy
from sensor_msgs.msg import CompressedImage


class Lane_Detector:
    def __init__(self):
        self.cv_bridge = CvBridge()

        # Topic from your bag playback
        self.image_topic = "/mybota002833/camera_node/image/compressed"

        rospy.init_node("my_lane_detector", anonymous=True)
        self.image_sub = rospy.Subscriber(
            self.image_topic,
            CompressedImage,
            self.image_callback,
            queue_size=1
        )

        rospy.loginfo("Subscribed to: {}".format(self.image_topic))

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
        img = self.cv_bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

        # Leave this commented unless image looks upside down
        # img = cv2.flip(img, 0)

        # 1. Crop image to road region
        height, width, _ = img.shape
        crop_y_start = int(height * 0.65)
        crop_x_start = int(width * 0.05)
        crop_x_end = int(width * 0.95)
        crop = img[crop_y_start:height, crop_x_start:crop_x_end]

        # 2. Convert cropped image to HSV
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

        # 3. White filtering
        lower_white = np.array([0, 0, 200], dtype=np.uint8)
        upper_white = np.array([180, 50, 255], dtype=np.uint8)
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # 4. Yellow filtering
        lower_yellow = np.array([15, 80, 80], dtype=np.uint8)
        upper_yellow = np.array([40, 255, 255], dtype=np.uint8)
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Morphological cleanup
        kernel = np.ones((5, 5), np.uint8)
        white_mask = cv2.erode(white_mask, kernel, iterations=1)
        white_mask = cv2.dilate(white_mask, kernel, iterations=1)

        yellow_mask = cv2.erode(yellow_mask, kernel, iterations=1)
        yellow_mask = cv2.dilate(yellow_mask, kernel, iterations=1)

        white_filtered = cv2.bitwise_and(crop, crop, mask=white_mask)
        yellow_filtered = cv2.bitwise_and(crop, crop, mask=yellow_mask)

        # 5. Canny edge detector on cropped image
        gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray_crop = cv2.GaussianBlur(gray_crop, (5, 5), 0)
        edges = cv2.Canny(gray_crop, 80, 160)

        # 6. Hough transform on white-filtered image
        white_edges = cv2.Canny(white_mask, 80, 160)
        white_lines = cv2.HoughLinesP(
            white_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=40,
            minLineLength=30,
            maxLineGap=8
        )

        # 7. Hough transform on yellow-filtered image
        yellow_edges = cv2.Canny(yellow_mask, 80, 160)
        yellow_lines = cv2.HoughLinesP(
            yellow_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=20,
            maxLineGap=8
        )

        # 8. Draw lines on cropped image
        output = np.copy(crop)
        output = self.output_lines(output, white_lines, color=(255, 0, 0))
        output = self.output_lines(output, yellow_lines, color=(0, 0, 255))

        # HSV back to BGR for display
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
