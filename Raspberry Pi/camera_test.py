import os

def take_pics(folder = "", filename = "", num_pics = 10, delay = None,
                   shutter = None, ISO = None, brightness = None,
                   contrast = None):

    delay_str = "" if delay == None else " -t " + str(delay)
    shutter_str = "" if shutter == None else " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    
    for i in range(num_pics):
        path = folder + "/" + filename + str(i) + ".jpg"
        take_pic(path, delay_str, shutter_str, ISO_str, brightness_str,
                 contrast_str)

def take_pic(path, delay, shutter, ISO, brightness, contrast):
    
        os.system("raspistill -o %s%s%s%s%s%s" % (path, delay, shutter, ISO,
                                                    brightness, contrast))


take_pics(folder = 'Data/pictures/test1', shutter = 250, delay = 1,
          contrast = 90, brightness = 80)



