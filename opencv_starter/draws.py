import cv2 as cv
import numpy as np

blank = np.zeros((500, 500, 3), dtype="uint8")
cv.imshow("blank", blank)


#paint
blank[:] = 255,255,255
cv.imshow("green", blank)

cv.waitKey(0)