#!/usr/bin/env python
import numpy
import math
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from  time import sleep

def scan_callback(msg):
	global right,forward,right_back
	right = msg.ranges[270]
	forward = msg.ranges[0]
	right_back = msg.ranges[225]

right =0 
forward = 0
right_back = 0

rospy.init_node('Move_delivery')
scan_sub = rospy.Subscriber('scan',LaserScan,scan_callback)
cmd_vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
rate = rospy.Rate(5)

# info for run
run_speed = 0.2
run_angle = 0
# info for turn left
left_speed = 0
left_angle = 1.65
left_time = rospy.Duration(1)
# info for turn right
right_speed = 0
right_angle = -1.65
right_time = rospy.Duration(1)
# other info
right_back_base = 0.5*math.sqrt(2)
limit_base = 0.5
twist = Twist()
while not rospy.is_shutdown():
	global forward,right,right_back
	if (right <limit_base) & (right > 0.055):#case 1,3,4
		if forward >= limit_base: #case1
			print "case 1"
			twist.linear.x = run_speed
			twist.angular.z = run_angle
		else:#case3,4
			print "case 3,4"
			base_time = rospy.Time.now() + left_time
			while base_time > rospy.Time.now():
				twist.linear.x = left_speed
				twist.angular.z = left_angle
				cmd_vel_pub.publish(twist)
				rate.sleep()	
			twist.angular.z =0
			twist.linear.x = 0
	else: #case2
		print "case 2"
		while(right_back> right_back_base):
			twist.linear.x = run_speed
			twist.angular.z = run_angle
			cmd_vel_pub.publish(twist)
			rate.sleep()
		base_time = rospy.Time.now() + right_time
		while base_time > rospy.Time.now():
			twist.linear.x = right_speed
			twist.angular.z = right_angle
			cmd_vel_pub.publish(twist)
			rate.sleep()
		while(right > limit_base):
			twist.linear.x = run_speed
			twist.angular.z = run_speed
			cmd_vel_pub.publish(twist)
			rate.sleep()
		twist.linear.x = 0
		twist.angular.z = 0
	cmd_vel_pub.publish(twist)
	rate.sleep()
					

