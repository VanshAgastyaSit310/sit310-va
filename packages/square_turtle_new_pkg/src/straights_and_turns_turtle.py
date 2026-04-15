#!/usr/bin/env python3

import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math

class TurtlesimController:
    def __init__(self):

        # -------- STATE --------
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0

        self.start_x = 0.0
        self.start_y = 0.0

        self.goal_distance = 0.0
        self.target_theta = 0.0

        self.dist_active = False

        rospy.init_node('turtlesim_controller', anonymous=True)

        # -------- SUBSCRIBERS --------
        rospy.Subscriber("/turtle1/pose", Pose, self.pose_callback)
        rospy.Subscriber("/goal_distance", Float64, self.distance_callback)
        rospy.Subscriber("/goal_angle", Float64, self.angle_callback)

        # -------- PUBLISHER --------
        self.pub = rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)

        rospy.Timer(rospy.Duration(0.01), self.control_loop)

        rospy.loginfo("FINAL WORKING CONTROLLER STARTED 🚀")
        rospy.spin()

    # =============================
    # CALLBACKS
    # =============================

    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta

    def angle_callback(self, msg):
        rospy.loginfo("Rotate by: %f", msg.data)

        self.target_theta = self.current_theta + msg.data
        self.dist_active = False   # stop any movement

    def distance_callback(self, msg):
        rospy.loginfo("Move distance: %f", msg.data)

        self.goal_distance = abs(msg.data)

        self.start_x = self.current_x
        self.start_y = self.current_y

        # 🔥 KEY FIX: decide direction using rotation
        if msg.data >= 0:
            self.target_theta = self.current_theta
        else:
            self.target_theta = self.current_theta + math.pi

        self.dist_active = True

    # =============================
    # HELPER
    # =============================

    def angle_diff(self, a, b):
        return math.atan2(math.sin(a - b), math.cos(a - b))

    # =============================
    # MAIN LOOP
    # =============================

    def control_loop(self, event):
        cmd = Twist()

        # -------- ROTATE FIRST --------
        angle_error = self.angle_diff(self.target_theta, self.current_theta)

        if abs(angle_error) > 0.05:
            cmd.angular.z = 2.0 if angle_error > 0 else -2.0

        # -------- THEN MOVE --------
        elif self.dist_active:

            dx = self.current_x - self.start_x
            dy = self.current_y - self.start_y
            distance_moved = math.sqrt(dx**2 + dy**2)

            if distance_moved >= self.goal_distance:
                rospy.loginfo("Reached target distance!")
                self.dist_active = False
            else:
                cmd.linear.x = 1.0   # ALWAYS forward

        self.pub.publish(cmd)


if __name__ == '__main__':
    try:
        TurtlesimController()
    except rospy.ROSInterruptException:
        pass
