#!/usr/bin/env python3

# Import Dependencies
import rospy 
from geometry_msgs.msg import Twist 
import time 
import math

def move_turtle_square(): 
    rospy.init_node('turtlesim_square_node', anonymous=True)
    
    # Init publisher
    velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10) 
    rospy.loginfo("Turtles are great at drawing squares!")

    # Define parameters
    side_length = 2.0        # length of each side of the square
    linear_speed = 1.0       # forward speed
    angular_speed = math.pi/2  # turning speed (radians/sec)
    
    while not rospy.is_shutdown():
        for _ in range(4):  # 4 sides of the square
            # Move forward
            move_cmd = Twist()
            move_cmd.linear.x = linear_speed
            move_cmd.angular.z = 0.0
            duration = side_length / linear_speed  # time to move one side
            t0 = rospy.Time.now().to_sec()
            while rospy.Time.now().to_sec() - t0 < duration:
                velocity_publisher.publish(move_cmd)
                rospy.sleep(0.01)

            # Turn 90 degrees
            turn_cmd = Twist()
            turn_cmd.linear.x = 0.0
            turn_cmd.angular.z = math.pi/2  # radians/sec
            turn_duration = math.pi/2 / turn_cmd.angular.z  # should be 1 sec
            t0 = rospy.Time.now().to_sec()
            while rospy.Time.now().to_sec() - t0 < turn_duration:
                velocity_publisher.publish(turn_cmd)
                rospy.sleep(0.01)

if __name__ == '__main__': 
    try: 
        move_turtle_square() 
    except rospy.ROSInterruptException: 
        pass
