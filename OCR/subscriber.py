#!/usr/bin/env python
import rospy
import cv2, cv_bridge
import numpy as np
from sensor_msgs.msg import Image
from PIL import Image as Im #pillow
from pytesseract import * #pytesseract, tesseract
import MySQLdb #mysql-python

def GetText(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	cv2.imwrite('original.png', gray)
	gray2 = gray.copy()
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	cl1 = clahe.apply(gray2)
	cv2.imwrite('clahe.png', cl1)

	blur = cv2.GaussianBlur(cl1, (3,3), 0)
	cv2.imwrite('blur.png', cl1)

	canny = cv2.Canny(blur, 100, 200)
	cv2.imwrite('canny.png', canny)


	cnts, contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	box1=[]
	f_count=0
	select=0
	plate_width=0

	for i in range(len(contours)):
		cnt = contours[i]
		area = cv2.contourArea(cnt)
		x,y,w,h = cv2.boundingRect(cnt)
		rect_area = w*h #area size
		aspect_ratio = float(w)/h #ratio = width / height

		if  (aspect_ratio>=0.5)and(aspect_ratio<=0.7)and(rect_area>=100)and(rect_area<=500):
			cv2.rectangle(gray2,(x,y),(x+w,y+h),(0,255,0),1)
			box1.append(cv2.boundingRect(cnt))

	cv2.imwrite('rectangle.png', gray2)
	for i in range(len(box1)): ##Buble Sort on python
		 for j in range(len(box1)-(i+1)):
			  if box1[j][0]>box1[j+1][0]:
				   temp=box1[j]
				   box1[j]=box1[j+1]
				   box1[j+1]=temp

	for m in range(len(box1)):
		count=0
		for n in range(m+1,(len(box1))):
			delta_x=abs(box1[n][0]-box1[m][0])
			if delta_x > 150:
				break
		 	delta_y =abs(box1[n][1]-box1[m][1])
			if delta_x ==0:
				delta_x=1
			if delta_y ==0:
				delta_y=1
			gradient =float(delta_y) /float(delta_x)
			if gradient<0.25:
				count=count+1
			#measure number plate size
			if count > f_count:
				select = m
				f_count = count;
				plate_width=delta_x

	try:
		number_plate=gray[box1[select][1]-10:box1[select][3]+box1[select][1]+20,box1[select][0]-10:box1[select][0]+plate_width + 20]
		resize_plate=cv2.resize(number_plate,None,fx=1.8,fy=1.8,interpolation=cv2.INTER_CUBIC+cv2.INTER_LINEAR)
	except:
		return
	cv2.imwrite('resize.jpg', resize_plate)
	text = image_to_string(resize_plate)
	print('+++OCR+++')
	print(text)
	return text

class Sub:
	def __init__(self):
		self.bridge = cv_bridge.CvBridge()
		cv2.namedWindow('window', 1)
		self.image_sub = rospy.Subscriber('camera/image', Image, self.image_callback)
		self.db = MySQLdb.connect(host = 'localhost',
					user = 'root',
					passwd = 'tesseract',
					db = 'tesseract')
		self.cur = self.db.cursor()
		self.sql = 'update room set'
	def image_callback(self, msg):
		image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
#		cv2.imshow('window', image)
		text = GetText(image)
#		xpos = 1
#		ypos = 2
#		fullSql = self.sql + 'xpos = {0}, ypos = {1} where roomnum = ${0} and xpos null and ypos null'.format(xpos,ypos,text)
#		self.cur.execute(fullSql)
#		self.db.commit()
#		cv2.waitKey(10)
#		cv2.destroyAllWindows()

rospy.init_node('image_sub')
sub = Sub()
rospy.spin()
