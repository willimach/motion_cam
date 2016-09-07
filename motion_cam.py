import io
import os
import picamera
import time
from datetime import datetime
from PIL import Image
from time import sleep

camera = picamera.PiCamera()
camera.rotation = 0
# sets black/white pictures
camera.color_effects= (128,128)  

difference = 40
pixels = 25

pic_width = 2592
pic_height = 1944
vid_width = 1024
vid_height = 768
vid_length=5

def mylog(text):
   logfile=open('/home/pi/share/motion_cam/motion_cam.log', 'a')
   logfile.write('\n' + str(text))
   os.fsync(logfile)
   logfile.close()


def mytimestamp():
   mytime=datetime.now()	
   date = "%04d%02d%02d-%02d%02d%02d" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   return(date)

def compare():
   camera.resolution = (100, 75)
   stream = io.BytesIO()
   camera.capture(stream, format = 'bmp') 
   stream.seek(0)
   im = Image.open(stream)
   buffer = im.load()
   stream.close()
   return im, buffer


def newimage(pic_width, pic_height,changedpixels):
   mytime = mytimestamp()
   filename = "motion_diff_pixels"+"_"+str(mytime)+"_"+str(difference)+"-"+str(pixels)+"_"+str(changedpixels)+".jpg"
#   filenamevid = "motion-%04d%02d%02d-%02d%02d%02d.h264" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   camera.resolution = (pic_width, pic_height)
   camera.capture('/home/pi/share/motion_cam/'+filename)
   camera.resolution = (vid_width,vid_height)
#   camera.start_recording(filenamevid)
#   time.sleep(vid_length)
#   camera.stop_recording()
   mylog(filename)
   myftp(filename)
#   print "Captured %s" % filename

def myftp(filename):
    from ftplib import FTP
    import configparser

    config=configparser.ConfigParser()
    config.read('motion_config.txt')

    server=config['FTP']['server']
    user=config['FTP']['user']
    passwd=config['FTP']['passwd']

    ftp=FTP(server,user=user,passwd=passwd)
    file=open(filename,'rb')
    ftp.cwd('www')
    ftp.storbinary('STOR motion.jpg',file)
    file.close()
    ftp.quit()




image1, buffer1 = compare()

logfile=open('/home/pi/share/motion_cam/motion_cam.log', 'a')
logfile.write('       '+str(mytimestamp())+': motion_cam started.\n')
os.fsync(logfile)
logfile.close()

while (True):

   image2, buffer2 = compare()

   changedpixels = 0
   for x in range(0, 100):
      for y in range(0, 75):
         pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
         if pixdiff > difference:
            changedpixels += 1

   mytime=round(time.time())
   if changedpixels > pixels:
      newimage(pic_width, pic_height,changedpixels)
   elif mytime % (30*60)== 0:
      newimage(pic_width, pic_height,changedpixels)
   elif mytime % (60)== 0:
      logfile=open('/home/pi/share/motion_cam/motion_cam.log', 'a')
      logfile.write('\t'+str(datetime.now().minute))
      os.fsync(logfile)
      logfile.close()
   image1 = image2
   buffer1 = buffer2


