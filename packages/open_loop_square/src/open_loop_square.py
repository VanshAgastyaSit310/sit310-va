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
