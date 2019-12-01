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

def photo_stream(folder = "photostream", filename = "", delay = 1,
                   shutter = None, ISO = None, brightness = None,
                   contrast = None, buffer_size = 10):

    os.system("rm %s/*" % folder)
    delay_str = "" if delay == None else " -t " + str(delay)
    shutter_str = "" if shutter == None else " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    gen_path = folder + "/" + filename

    for i in range(buffer_size):
        os.system("touch %s" % (gen_path + str(i) + ".jpg"))

    i = buffer_size
    result = 0
    while True:
            path = gen_path + str(i) + ".jpg"
            if take_pic(path, delay_str, shutter_str, ISO_str, brightness_str,
                     contrast_str):
                os.system("rm %s" % (path + '~'))
                break
            os.system("rm %s" % (gen_path + str(i - buffer_size) + ".jpg"))
            i += 1

photo_stream(shutter = 10000)
        
