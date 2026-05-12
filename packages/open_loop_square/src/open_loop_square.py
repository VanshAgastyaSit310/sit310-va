*/
#!/usr/bin/env python3

import rospy
import os
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class DriveSquare:

    def __init__(self):

        # Get robot name automatically
        self.vehicle_name = os.environ['VEHICLE_NAME']

        # ROS message
        self.cmd_msg = Twist2DStamped()

        # ==============================
        # CALIBRATION CONSTANTS
        # ==============================

        # Forward movement
        self.LINEAR_V = 1.0       # Robot forward speed
        self.STRAIGHT_TIME = 4.0  # Time to move ~1 metre

        # Rotation movement
        self.ANGULAR_V = 2.0         # Turning speed
        self.TURN_TIME = 2.0       # Time for ~90 degree turn

        # ==============================

        # Prevent multiple triggers
        self.is_running = False

        # Initialize ROS node
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

        rospy.loginfo("Drive Square Node Initialized")

    # ==========================================
    # FSM CALLBACK
    # ==========================================
    def fsm_callback(self, msg):

        rospy.loginfo("FSM State: %s", msg.state)

        # Stop robot in manual joystick mode
        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        # Start movement for any active autonomous mode
        elif not self.is_running:

            rospy.loginfo("Starting square movement...")

            self.is_running = True

            rospy.sleep(1)

            self.move_robot()

            self.is_running = False

    # ==========================================
    # STOP ROBOT
    # ==========================================
    def stop_robot(self):

        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0

        self.pub.publish(self.cmd_msg)

    # ==========================================
    # RUN NODE
    # ==========================================
    def run(self):

        rospy.spin()

    # ==========================================
    # MOVE ROBOT IN SQUARE
    # ==========================================
    def move_robot(self):

        for side in range(4):

            rospy.loginfo(f"=== Side {side + 1}/4 ===")

            # ----------------------------------
            # MOVE FORWARD
            # ----------------------------------

            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = self.LINEAR_V
            self.cmd_msg.omega = 0.0

            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Moving forward...")

            rospy.sleep(self.STRAIGHT_TIME)

            # Stop briefly
            self.stop_robot()

            rospy.sleep(0.7)

            # ----------------------------------
            # TURN 90 DEGREES
            # ----------------------------------

            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = self.ANGULAR_V

            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Turning...")

            rospy.sleep(self.TURN_TIME)

            # Stop briefly
            self.stop_robot()

            rospy.sleep(0.7)

        # Final stop
        self.stop_robot()

        rospy.loginfo("Square complete! Robot stopped.")

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':

    try:

        node = DriveSquare()

        node.run()

    except rospy.ROSInterruptException:

        pass
        
/*
#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped


class Drive_Square:
    def __init__(self):

        self.cmd_msg = Twist2DStamped()

        rospy.init_node('drive_square_node', anonymous=True)

        self.pub = rospy.Publisher(
            '/mybota002444/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    def run(self):
        rospy.sleep(1)  # allow publisher to connect
        self.move_robot()

    def move_robot(self):

        # Tune these for ~1m square
        side_time = 1.73
        turn_time = 0.244

        for i in range(4):

            # Move forward (1 side of square)
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.5
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Side %d: Forward", i + 1)
            rospy.sleep(side_time)

            # Turn 90 degrees
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = 4.0
            self.pub.publish(self.cmd_msg)

            rospy.loginfo("Side %d: Turn", i + 1)
            rospy.sleep(turn_time)

        self.stop_robot()


if __name__ == '__main__':
    try:
        robot = Drive_Square()
        robot.run()
    except rospy.ROSInterruptException:
        pass
