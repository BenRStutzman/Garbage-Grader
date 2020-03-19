from PIL import Image
import os
import time
import shutil

source_dir = '/home/BenS/GarbageGrader/RPiPics/incoming_frames'
dest_picture = '/home/BenS/NeuralNet/current_composite.jpg'

def paste_into_composite(frame_file, position, comp_file = dest_picture):

    comp = Image.open(comp_file)
    frame = Image.open(frame_file)

    x = position % 2 * 1600
    y = position // 2 * 1600

    comp.paste(frame.crop((466, 0, 2066, 1600)),
                    (x, y, x + 1600, y + 1600))

    comp.save(comp_file)

    composite.close()
    frame.close()

position = 0
while True:
    for pic in os.scandir(pic_dir + 'incoming_frames'):
        paste_into_composite(pic.path, position)
        os.remove(pic)
        positions = (position + 1) % 4
