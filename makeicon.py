#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
import tempfile
from os import path
from shutil import copy2, move, rmtree

from PIL import Image

cliParser = argparse.ArgumentParser(description='Make iOS .appiconsets')
cliParser.add_argument(
    'sourceImage',
    nargs=1,
    help='A image file at least 1024x1024 pixels'
)

namespace = cliParser.parse_args().sourceImage

sourceImagePath = path.expanduser(namespace[0])
sourceImage = Image.open(sourceImagePath)
destDir = path.join(path.dirname(sourceImagePath), 'AppIcon.appiconset')

scriptDir = sys.path[0]
contentsJSONPath = path.join(scriptDir, 'Contents.json')


def makeIcons(outDir):
  '''
  Copy and update `Contents.json` file with proper file namees to destination
  folder.
  Generate icons using `Pillow`.
  '''

  copy2(contentsJSONPath, outDir)
  with open(contentsJSONPath) as file:
    contents = json.load(file)

  print('Generate:')

  # collect sizes & update file names
  sizes = set()
  for imageInfo in contents['images']:
    sizeString = imageInfo['size']
    points = float(sizeString[:sizeString.find('x')])
    scale = float(imageInfo['scale'][0])
    pixels = int(points * scale)

    sizes.add(pixels)
    imageInfo['filename'] = f'App-Icon-{pixels}.png'

  sizes = list(sizes)
  sizes.sort()

  with open(contentsJSONPath, 'w') as file:
    json.dump(contents, file)

  # generate icon files
  for pixels in sizes:
    fileName = f'App-Icon-{pixels}.png'
    print(f'- {fileName}')

    outImage = sourceImage.resize((pixels, pixels), resample=Image.BICUBIC)
    outImage.save(path.join(outDir, fileName))


try:
  # create temp dir
  tmpDir = tempfile.mkdtemp()
  umask = os.umask(0o077)

  # populate temp dir
  makeIcons(tmpDir)

  # move temp dir to destination
  if path.exists(destDir):
    print(f'\nDelete existing destination directory: {destDir}')
    rmtree(destDir)

  move(tmpDir, destDir)
  os.system(f'open {path.dirname(destDir)}')

finally:
  os.umask(umask)
