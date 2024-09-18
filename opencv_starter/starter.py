import cv2 as cv

img = cv.imread("photos/feed_cv_large.jpg")


def rescaleFrame( frame, scale= 0.75):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height )

    return cv.resize(frame, dimensions, interpolation=cv.INTER_AREA)
cv.imshow("torsha", img)
cv.waitKey(0)


