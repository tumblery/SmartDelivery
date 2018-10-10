#!/usr/bin/env python
import roslib
import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

cap = cv2.VideoCapture(0)
cap.set(3,320)
cap.set(4,240)
rospy.init_node('publisher', anonymous=True)
image_pub = rospy.Publisher("camera/image", Image)
rate = rospy.Rate(10)
bridge = CvBridge()

while not rospy.is_shutdown():
	ret, frame = cap.read()
	cv2.imshow('frame', frame)
	image_pub.publish(bridge.cv2_to_imgmsg(frame, "bgr8"))
	cv2.waitKey(3)
	rate.sleep()
