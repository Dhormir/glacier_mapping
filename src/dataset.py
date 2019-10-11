import os
import math

import numpy as np
import pandas as pd

from torch.utils.data import Dataset
import torchvision.transforms as T

class GlacierDataset(Dataset):
  def __init__(self, base_dir, data_file, img_transform=None, mode='train', borders=False):
    super().__init__()
    self.base_dir = base_dir
    data_path = os.path.join(base_dir, data_file)
    self.data = pd.read_csv(data_path)
    self.data = self.data[self.data.train == mode]
    self.img_transform = img_transform
    self.borders = borders
    
  def __getitem__(self, i):
    pathes = ['img_path', 'mask_path', 'border_path']
    image_path, mask_path, border_path = self.data.iloc[i][pathes]
    image_path = os.path.join(self.base_dir, image_path)
    mask_path = os.path.join(self.base_dir, mask_path)
    
    img = np.load(image_path)
    if self.img_transform is not None:
      img = self.img_transform(img)
    else:
      img = T.ToTensor()(img)
      
    
    if (self.borders) and (not pd.isnull(border_path)):
      border_path = os.path.join(self.base_dir, border_path)
      border = np.load(border_path)
      border = np.expand_dims(border, axis=0)
      img = np.concatenate((img, border), axis=0)

                         
    return img, np.load(mask_path)
    
  def __len__(self):
    return len(self.data)