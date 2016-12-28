import picamera, time
from motion_cam_lib import *
import motion_conf
from threading import Thread, active_count

difference = motion_conf.difference
pixels     = motion_conf.pixels

max_uploads = motion_conf.max_uploads
uploads     = motion_conf.uploads

pic_compare_width  = motion_conf.pic_compare_width
pic_compare_height = motion_conf.pic_compare_height


camera = picamera.PiCamera()
camera.rotation = 0
# sets black/white pictures
camera.color_effects= (128,128)
camera.resolution = (motion_conf.pic_compare_width, motion_conf.pic_compare_height)

# start main code:
buffer1 = compare(camera)

while (True):
   tic=time.time()
   
   buffer2 = compare(camera) #takes 0.5s
   changedpixels = 0
   for x in range(0, pic_compare_width): #takes 0.1s
      for y in range(0, pic_compare_height):
         pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
         if pixdiff > difference:
            changedpixels += 1
   mytime=round(time.time())
   if changedpixels > pixels:
      #makes picture and uploads it
      #filename = newimage(changedpixels,camera)
      t = Thread(target=myftp, args=(newimage(changedpixels,camera),))
      t.start()
   elif mytime % (60*60)== 0:
      # only picture, no upload
      newimage(changedpixels,camera) #takes 0.8s
   buffer1 = buffer2
   print(str(round(time.time()-tic,1))+ ' end' + str(active_count()),end='\r')
