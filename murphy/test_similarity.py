'''
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
'''

import image
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def report_similarity(image_file_1, image_file_2):
    print "comparing %s with %s" % (image_file_1, image_file_2)
    img2 = image.ImageHolder(image_file_1)
    img1 = image.ImageHolder(image_file_2, 0xed1c2400)
    score, coord_x, coord_y = image.find_image(img1, img2)

    perc = (float(score) / float(img1.pixel_count))

    print "Comparison score is %s of %s" % (perc, score)
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "You must specify 2 image file names for comparing"
    else:
        report_similarity(sys.argv[1], sys.argv[2])