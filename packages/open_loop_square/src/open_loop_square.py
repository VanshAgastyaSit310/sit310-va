#!/usr/bin/env python3

import rospy
import os
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class DriveSquare:

    def __init__(self):
        # Get robot name dynamically
        self.vehicle_name = os.environ['VEHICLE_NAME']

        # Message
        self.cmd_msg = Twist2DStamped()

        # Calibration constants (EDIT THESE ONLY)
        self.LINEAR_V = 0.25        # m/s → forward speed
        self.STRAIGHT_TIME = 6.0    # seconds → time to travel ~1m

        self.ANGULAR_V = 1.2        # rad/s → turning speed
        self.TURN_TIME = 2.0        # seconds → time for ~90° turn

        # Safety flag (prevents multiple triggers)
        self.is_running = False

        # ROS node
        rospy.init_node('drive_square_node', anonymous=True)

        # Publisher
        self.pub = rospy.Publisher(
            f'/{self.vehicle_name}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        # Subscriber
        rospy.Subscriber(
            f'/{self.vehicle_name}/fsm_node/mode',
            FSMState,
            self.fsm_callback,
            queue_size=1
        )

    # FSM callback
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING" and not self.is_running:
            self.is_running = True
            rospy.sleep(1)
            self.move_robot()
            self.is_running = False

    # Stop robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Main loop
    def run(self):
        rospy.spin()

    # Square movement
    def move_robot(self):

        for side in range(4):
            rospy.loginfo(f"=== Side {side+1}/4 ===")

            # Move straight
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = self.LINEAR_V
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Moving straight...")
            rospy.sleep(self.STRAIGHT_TIME)

            self.stop_robot()
            rospy.sleep(0.5)

            # Turn 90 degrees
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = self.ANGULAR_V
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Turning...")
            rospy.sleep(self.TURN_TIME)

            self.stop_robot()
            rospy.sleep(0.5)

        self.stop_robot()
        rospy.loginfo("Square complete!")


if __name__ == '__main__':
    try:
        node = DriveSquare()
        node.run()
    except rospy.ROSInterruptException:
        pass
