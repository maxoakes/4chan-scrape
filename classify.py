import os
from nudenet import NudeDetector

BASE_PATH = r'C:\Users\Scouter\Downloads'
detector = NudeDetector()

for root, dirs, files in os.walk(BASE_PATH):
    path = root.split(os.sep)
    for file in files:
        result = detector.detect(path)
        path_string = fr'{path}\{file}'
        print((path_string, result))

# Classify single image

# Returns {'path_to_image_1': {'safe': PROBABILITY, 'unsafe': PROBABILITY}}
# Classify multiple images (batch prediction)
# batch_size is optional; defaults to 4
# classifier.classify(['path_to_image_1', 'path_to_image_2'], batch_size=BATCH_SIZE)
# Returns {'path_to_image_1': {'safe': PROBABILITY, 'unsafe': PROBABILITY},
#          'path_to_image_2': {'safe': PROBABILITY, 'unsafe': PROBABILITY}}