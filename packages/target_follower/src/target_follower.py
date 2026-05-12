#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class Target_Follower:
    def __init__(self):
        rospy.init_node('target_follower_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)

        # Get robot name from environment/namespace
        self.veh = rospy.get_namespace().strip("/")
        if self.veh == "":
            self.veh = "YOUR_ROBOT_NAME"

        # Publisher and subscriber
        self.cmd_vel_pub = rospy.Publisher(
            f'/{self.veh}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        rospy.Subscriber(
            f'/{self.veh}/apriltag_detector_node/detections',
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        # ===== Controller parameters =====
        # Seek mode: rotate until object appears
        self.search_omega = 2.2

        # Look-at-object mode: proportional steering
        self.kp = 6.0
        self.deadband = 0.02
        self.min_omega = 1.0
        self.max_omega = 3.0

        rospy.loginfo(f"[target_follower] Started for vehicle: {self.veh}")
        rospy.spin()

    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def publish_cmd(self, v, omega):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = v
        cmd_msg.omega = omega
        self.cmd_vel_pub.publish(cmd_msg)

    def choose_target(self, detections):
        """
        Pick one tag if multiple are visible.
        We choose the nearest tag using smallest z distance.
        """
        best_det = None
        best_z = float("inf")

        for det in detections:
            z = det.transform.translation.z
            if z < best_z:
                best_z = z
                best_det = det

        return best_det

    def move_robot(self, detections):
        # ===============================
        # Feature 1: Seek an object
        # If no tags are detected, rotate in place
        # ===============================
        if len(detections) == 0:
            rospy.loginfo_throttle(1.0, "No object detected -> SEEK mode")
            self.publish_cmd(0.0, self.search_omega)
            return

        # ===============================
        # Feature 2: Look at the object
        # Keep the object centered using in-place rotation only
        # ===============================
        target = self.choose_target(detections)

        x = target.transform.translation.x
        y = target.transform.translation.y
        z = target.transform.translation.z
        tag_id = target.tag_id

        rospy.loginfo_throttle(
            0.5,
            f"LOOK mode | tag_id={tag_id}, x={x:.3f}, y={y:.3f}, z={z:.3f}"
        )

        # Error = horizontal offset of tag in camera frame
        # Goal: x -> 0
        error_x = x

        # Deadband: if tag is nearly centered, stop turning
        if abs(error_x) < self.deadband:
            omega = 0.0
        else:
            # Proportional control
            omega = -self.kp * error_x

            # Apply minimum angular velocity so robot actually moves
            if abs(omega) < self.min_omega:
                omega = self.min_omega if omega > 0 else -self.min_omega

            # Clamp to maximum velocity
            if omega > self.max_omega:
                omega = self.max_omega
            elif omega < -self.max_omega:
                omega = -self.max_omega

        # No forward/backward movement for this task
        self.publish_cmd(0.0, omega)


if __name__ == '__main__':
    try:
        Target_Follower()
    except rospy.ROSInterruptException:
        pass
