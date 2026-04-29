#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState

class Drive_Square:
    def __init__(self):
        # Initialize global class variables
        self.cmd_msg = Twist2DStamped()

        # Initialize ROS node
        rospy.init_node('drive_square_node', anonymous=True)

        # Initialize Pub/Subs
        self.pub = rospy.Publisher('/mybota002833/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/mybota002833/fsm_node/mode', FSMState, self.fsm_callback, queue_size=1)

    # Robot only moves when lane following is selected on the duckiebot joystick app
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)
        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()
        elif msg.state == "LANE_FOLLOWING":
            rospy.sleep(1)  # Wait a sec for the node to be ready
            self.move_robot()

    # Sends zero velocities to stop the robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Spin forever but listen to message callbacks
    def run(self):
        rospy.spin()  # Keeps node from exiting until node has shutdown

    # Robot drives in a square (4 x 1 metre sides) then stops
    def move_robot(self):

        for side in range(4):
            rospy.loginfo("=== Side %d/4 ===", side + 1)

            # --- Drive forward approximately 1 metre ---
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.3        # linear velocity in m/s
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Driving straight...")
            rospy.sleep(3.3)            # ~1 m at 0.3 m/s  →  tune if needed

            # Brief stop before turning
            self.stop_robot()
            rospy.sleep(0.5)

            # --- Rotate 90 degrees (π/2 rad) in place ---
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = 1.5    # angular velocity in rad/s
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Turning 90 degrees...")
            rospy.sleep(1.05)           # π/2 ÷ 1.5  ≈  1.05 s  →  tune if needed

            # Brief stop after turning
            self.stop_robot()
            rospy.sleep(0.5)

        # Square complete — stop the robot
        self.stop_robot()
        rospy.loginfo("Square complete! Robot stopped.")


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
