def mytimestamp():
   from datetime import datetime
   mytime=datetime.now()	
   date = "%04d%02d%02d-%02d%02d%02d" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   return(date)

def compare(camera):
   import io, os, picamera
   from PIL import Image   
   stream = io.BytesIO()
   #use_video_port=True makes it way faster (but a bit blurrier?)
   camera.capture(stream, format = 'bmp',use_video_port=True) #takes 0.6s (100%of time)
   stream.seek(0)
   im = Image.open(stream)
   buffer = im.load()
   stream.close()
   return buffer


def newimage(changedpixels,camera):
   import motion_conf,time
   mytime = mytimestamp()
   filename = "z_diff_pix"+"_"+str(mytime)+"_"+str(motion_conf.difference)+"-"+str(motion_conf.pixels)+"_"+str(changedpixels)+".jpg"
   camera.annotate_text_size=70
   camera.annotate_text = str(mytime)
   
   camera.resolution = (motion_conf.pic_width, motion_conf.pic_height) #takes 0.1s
   camera.capture('/home/pi/share/motion_cam/'+filename,use_video_port=False) # takes 0.6s 
   #use_video_port=True makes it way faster (but a bit blurrier?)
   camera.resolution = (motion_conf.pic_compare_width, motion_conf.pic_compare_height) #takes 0.1s
   return filename
   
   
def newvid(changedpixels):
   import motion_conf
   mytime = mytimestamp()
   filenamevid = "motion-%04d%02d%02d-%02d%02d%02d.h264" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   camera.resolution = (motion_conf.vid_width, motion_conf.vid_height)
   camera.capture('/home/pi/share/motion_cam/'+filename)
   camera.start_recording(filenamevid)
   time.sleep(motion_conf.vid_length)
   camera.stop_recording()
   myftp(filename)
#   print "Captured %s" % filename


def myftp(filename):
    from ftplib import FTP
    import motion_conf,os
    
    os.chdir(os.path.dirname(__file__))
      
    ftp=FTP(motion_conf.server, user=motion_conf.user, passwd=motion_conf.passwd)
    file=open(filename,'rb')
    ftp.cwd('www')
    ftp.storbinary('STOR motion_'+str(motion_conf.uploads)+'.jpg',file)
    motion_conf.uploads=motion_conf.uploads+1
    if motion_conf.uploads>motion_conf.max_uploads:
       motion_conf.uploads=1
    file.close()
    ftp.quit()
