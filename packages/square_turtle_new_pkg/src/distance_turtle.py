#!/usr/bin/env python3

import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math

class DistanceReader:
    def __init__(self):
        
        rospy.init_node('turtlesim_distance_node', anonymous=True)

        rospy.Subscriber("/turtle1/pose", Pose, self.callback)

        self.distance_publisher = rospy.Publisher('/turtle_dist', Float64, queue_size=10)

        rospy.loginfo("Initialized distance node!")

        self.prev_x = None
        self.prev_y = None
        self.total_distance = 0.0
        
        rospy.spin()

    def callback(self, msg):

        # First reading
        if self.prev_x is None:
            self.prev_x = msg.x
            self.prev_y = msg.y
            return

        dx = msg.x - self.prev_x
        dy = msg.y - self.prev_y
        distance = math.sqrt(dx**2 + dy**2)

        self.total_distance += distance

        self.distance_publisher.publish(self.total_distance)

        rospy.loginfo("Total Distance Travelled: %f", self.total_distance)

        self.prev_x = msg.x
        self.prev_y = msg.y


if __name__ == '__main__': 
    try: 
        DistanceReader()
    except rospy.ROSInterruptException: 
        pass
