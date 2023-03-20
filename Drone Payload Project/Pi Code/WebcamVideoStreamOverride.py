# import the necessary packages
from threading import Thread
from multiprocessing import Process
import cv2
import YoloModel
import ArucoDetect


class WebcamVideoStream:
	def __init__(self, src=0, name="WebcamVideoStream",UseModel = False, UseAruco = False):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(0)
	
		#self.stream = cv2.VideoCapture('1664152920.7081351basicvideo2.avi')
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
		
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
		self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
		self.UseModel = UseModel
		self.UseAruco = UseAruco
		self.Model = YoloModel.Yolo()
		self.Aruco = ArucoDetect.Aruco()
			


	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()
		#t = Process(target=self.update, args=())
		#t.start()
		#t.join()
		#self.update()

		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				print("stop 4")
				cv2.destroyAllWindows()
				self.stream.release()
				return

			# otherwise, read the next frame from the stream
			(self.grabbed, frame) = self.stream.read()
			self.frame = frame
			
			#if(self.UseAruco):
			#	self.Aruco.update(frame)

			#if(self.UseModel):
			#	self.frame = self.Model.update(frame)

			#if(self.UseAruco):
			#	self.Aruco.draw(frame)
				
			#Display image
			#cv2.imshow('WebcamVideo',frame)
			#cv2.waitKey(1)

	def read(self):
		# return the frame most recently read
		return self.frame, self.grabbed

	def stop(self):
		# indicate that the thread should be stopped
		print("stop 3")
		self.stopped = True
		self.close()
