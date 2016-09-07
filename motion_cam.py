import io, os, picamera, time, configparser
from datetime import datetime
from PIL import Image
from time import sleep
from ftplib import FTP

camera = picamera.PiCamera()
camera.rotation = 0
# sets black/white pictures
camera.color_effects= (128,128)  

config=configparser.ConfigParser()
config.read('motion_config.txt')

difference =int(config['CAM']['difference'])
pixels = int(config['CAM']['pixels'])

pic_width  = int(config['CAM']['pic_width'])
pic_height = int(config['CAM']['pic_height'])
vid_width  = int(config['CAM']['vid_width'])
vid_height = int(config['CAM']['vid_height'])
vid_length = int(config['CAM']['vid_length'])

max_uploads=10
uploads=1

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
   filename = "mc_diff_pix"+"_"+str(mytime)+"_"+str(difference)+"-"+str(pixels)+"_"+str(changedpixels)+".jpg"
#   filenamevid = "motion-%04d%02d%02d-%02d%02d%02d.h264" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   camera.resolution = (pic_width, pic_height)
   camera.capture('/home/pi/share/motion_cam/'+filename)
   camera.resolution = (vid_width,vid_height)
#   camera.start_recording(filenamevid)
#   time.sleep(vid_length)
#   camera.stop_recording()
   myftp(filename)
#   print "Captured %s" % filename



def myftp(filename):
    global uploads
    
    config=configparser.ConfigParser()
    config.read('motion_config.txt')

    server=config['FTP']['server']
    user=config['FTP']['user']
    passwd=config['FTP']['passwd']

    ftp=FTP(server,user=user,passwd=passwd)
    file=open(filename,'rb')
    ftp.cwd('www')
    #ftp.storbinary('STOR motion.jpg',file)
    ftp.storbinary('STOR motion_'+str(uploads)+'.jpg',file)
    print(uploads)
    uploads=uploads+1
    if uploads>max_uploads:
       uploads=1
    file.close()
    ftp.quit()
    



image1, buffer1 = compare()


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
   image1 = image2
   buffer1 = buffer2


