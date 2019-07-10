import cv2
import numpy as np
import face_recognition
import datetime

if str(input("take photo [y/n]")) == "y":

	#Take photo using camera
	stream = cv2.VideoCapture(0)
	ret,frame = stream.read()
	stream.release()
	cv2.imwrite("bus_scan.png",frame)

	#Apply facial recognition algorithm
	image = face_recognition.load_image_file("bus_scan.png")
	face_locations = face_recognition.face_locations(image)
	
	#Print number of faces
	print(str(len(face_locations)) + " Faces Found " + (str(datetime.datetime.now())).split(" ")[0])

