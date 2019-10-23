import fastai
from fastai.vision import *

path = Path("P:\Senior Design\pictures")
classes = ["empty", "full"]
data = ImageDataBunch.from_folder(path, train=".", valid_pct=0.2,
        ds_tfms=get_transforms(), size=224, num_workers=4).normalize(imagenet_stats)
data.classes
