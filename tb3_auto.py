#!/usr/bin/env python

import rospy

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

import sys, select, termios, tty

msg = """
w : start auto mode
a : turn left
d : turn right
x : backward
space key, s : force stop

CTRL-C to quit
"""

# Global constants
LINEAR_VEL = 0.1
ANGULAR_VEL = 0.8
    
# Global variables
laser_FC_ = 0
laser_FL_ = 0
laser_FR_ = 0
        
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], LINEAR_VEL)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def callback(data):
    global laser_FC_, laser_FL_, laser_FR_
        
    if data.ranges[0] > data.range_min and data.ranges[0] < data.range_max:
        laser_FC_ = data.ranges[0]

    if data.ranges[30] > data.range_min and data.ranges[30] < data.range_max:
        laser_FL_ = data.ranges[30]

    if data.ranges[330] > data.range_min and data.ranges[330] < data.range_max:
        laser_FR_ = data.ranges[330]
        
if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('turtlebot3_auto')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
       
    sub = rospy.Subscriber("/scan", LaserScan, callback, queue_size=10)
    
    state = 0 # 0:stop, 1:auto, 2:left, 3:right, 4:backward
    
    status = 0
    
    control_linear_vel = 0
    control_angular_vel = 0
    try:
        print msg
        while(1):
            key = getKey()
            if key == 'w' :
                if state != 1:
                    state = 1
                    print("Start AUTO MODE")
                    status = status + 1
            elif key == 'a' :
                if state != 2:
                    state = 2
                    print("TURN LEFT")
                    status = status + 1
            elif key == 'd' :
                if state != 3:
                    state = 3
                    print("TURN RIGHT")
                    status = status + 1
            elif key == 'x' :
                if state != 4:
                    state = 4
                    print("BACKWARD")
                    status = status + 1                        
            elif key == ' ' or key == 's' :
                if state != 0:
                    state = 0
                    print("STOP")
                    status = status + 1
            else:
                if (key == '\x03'):
                    break
                    
            show_sensor = "{:.3f}".format(laser_FL_) + " | " + "{:.3f}".format(laser_FC_) + " | " + "{:.3f}".format(laser_FR_)
            if state == 1 :
                if laser_FC_ > 0.6 and laser_FL_ > 0.4 and laser_FR_ > 0.4:
                    control_linear_vel = LINEAR_VEL
                    control_angular_vel = 0
                    print(show_sensor + "   Move Forward")
                    status = status + 1
                elif laser_FL_ > laser_FR_:
                    control_linear_vel = 0
                    control_angular_vel = ANGULAR_VEL
                    print(show_sensor + "   Turn Left")   
                    status = status + 1
                else:
                    control_linear_vel = 0
                    control_angular_vel = -ANGULAR_VEL
                    print(show_sensor + "   Turn Right")
                    status = status + 1
            elif state == 2 :
                    control_linear_vel = 0
                    control_angular_vel = ANGULAR_VEL
            elif state == 3 :
                    control_linear_vel = 0
                    control_angular_vel = -ANGULAR_VEL
            elif state == 4 :
                    control_linear_vel = -LINEAR_VEL
                    control_angular_vel = 0        
            else:
                control_linear_vel = 0
                control_angular_vel = 0
            
            if status >= 14:
                print msg
                status = 0
            
            twist = Twist()
            twist.linear.x = control_linear_vel; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_angular_vel
            pub.publish(twist)

    except:
        print e

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
