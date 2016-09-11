def mytimestamp():
   from datetime import datetime
   mytime=datetime.now()	
   date = "%04d%02d%02d-%02d%02d%02d" % (mytime.year, mytime.month, mytime.day, mytime.hour, mytime.minute, mytime.second)
   return(date)

def compare(camera):
   import io, os, picamera
   from PIL import Image
   stream = io.BytesIO()
   camera.capture(stream, format = 'bmp') 
   stream.seek(0)
   im = Image.open(stream)
   buffer = im.load()
   stream.close()
   return buffer


def newimage(changedpixels,camera):
   import motion_conf

   mytime = mytimestamp()
   filename = "z_diff_pix"+"_"+str(mytime)+"_"+str(motion_conf.difference)+"-"+str(motion_conf.pixels)+"_"+str(changedpixels)+".jpg"
   camera.resolution = (motion_conf.pic_width, motion_conf.pic_height)
   camera.capture('/home/pi/share/motion_cam/'+filename)
   camera.resolution = (motion_conf.pic_compare_width, motion_conf.pic_compare_height)
   return filename
#   print "Captured %s" % filename
   
   
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
    import motion_conf

    ftp=FTP(motion_conf.server, user=motion_conf.user, passwd=motion_conf.passwd)
    file=open(filename,'rb')
    ftp.cwd('www')
    ftp.storbinary('STOR motion_'+str(motion_conf.uploads)+'.jpg',file)
    motion_conf.uploads=motion_conf.uploads+1
    if motion_conf.uploads>motion_conf.max_uploads:
       motion_conf.uploads=1
    file.close()
    ftp.quit()
