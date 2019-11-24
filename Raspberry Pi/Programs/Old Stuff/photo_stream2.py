import os
import time

def take_pics(folder = "", filename = "", num_pics = 10, delay = None,
                   shutter = None, ISO = None, brightness = None,
                   contrast = None):

    delay_str = "" if delay == None else " -t " + str(delay)
    shutter_str = "" if shutter == None else " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    gen_path = folder + "/" + filename
    
    for i in range(num_pics):
        path = gen_path + str(i) + ".jpg"
        take_pic(path, delay_str, shutter_str, ISO_str, brightness_str,
                 contrast_str)

def take_pic(path, delay_str, shutter_str, ISO_str, brightness_str,
             contrast_str):
    
        return os.system("raspistill -o %s%s%s%s%s%s" % (path, delay_str,
                                                  shutter_str, ISO_str,
                                                  brightness_str, contrast_str))

def photo_stream(folder = "photostream", filename = "",
                   shutter = None, ISO = None, brightness = None,
                   contrast = None):

    os.system("rm %s/*" % folder)
    shutter_str = "" if shutter == None else " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    path = folder + "/" + filename

    os.system("raspistill -t 1000000000000 -tl 0 -o %s%%06d.jpg%s%s%s%s"
              % (path, shutter_str, ISO_str, brightness_str, contrast_str))

photo_stream(shutter = 10000)
        
