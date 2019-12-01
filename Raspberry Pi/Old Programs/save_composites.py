from PIL import Image
import os

def save_composite(buffer_size = 4, inp_folder = "photostream",
                    out_folder = "composites", ident = 0):

    buffer = []
    for file in os.scandir(inp_folder):
        if file.path[-1] != '~': # make sure it's not a hidden file
            buffer.append(file.path)

    paths = sorted(buffer, key = lambda path: int(path[len(inp_folder) + 1 : -4]))[-buffer_size:]
    pictures = []
    for path in paths:
        pictures.append(Image.open(path))

    # following 10ish lines are from glombard on github:
    # https://gist.github.com/glombard/7cd166e311992a828675
    
    composite = Image.new("RGB", (800, 600))

    for index, picture in enumerate(pictures):
      picture.thumbnail((400, 400), Image.ANTIALIAS)
      x = index % 2 * 400
      y = index // 2 * 300
      w, h = picture .size
      #print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
      composite.paste(picture, (x, y, x + w, y + h))

    composite.save(os.path.expanduser('%s/%d.jpg' % (out_folder, ident)))
    composite.close()


save_composite()
