import math
from imutils import perspective, contours
import numpy as np
import argparse
import imutils
import cv2
import pytesseract
from PIL import Image
from imutils.perspective import four_point_transform
from matplotlib import pyplot as plt


class Run:
    def __init__(self, imagePath=''):
        # self.out = {}
        print("init")
        self._imagePath = imagePath

    def order_points_old(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # return the ordered coordinates
        return rect

    def mainCode(self):
        output = {}
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        # Load image, convert to HSV, color threshold to get mask
        # img = Image.open('images/img.png')
        img = Image.open(self._imagePath)

        new_image = img.resize((900, 746))
        new_image.save('image_resize.jpg')
        image = cv2.imread('image_resize.jpg')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 0])
        upper = np.array([100, 175, 110])
        mask = cv2.inRange(hsv, lower, upper)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)

        # Find rotated bounding box then perspective transform
        cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        rect = cv2.minAreaRect(cnts[0])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(image, [box], 0, (36, 255, 12), 2)
        warped = four_point_transform(255 - mask, box.reshape(4, 2))

        # OCR(final removing noise)
        data = pytesseract.image_to_string(warped, lang='eng', config='--psm 6')

        cv2.imwrite('image_resize.jpg', close)

        # noise 2

        image = cv2.imread('image_resize.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        # Filter using contour area and remove small noise
        cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 5500:
                cv2.drawContours(thresh, [c], -1, (0, 0, 0), -1)
        # Morph close and invert image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        close = 255 - cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        # cv2.imshow('close', close)
        cv2.imwrite('image_resize.jpg', close)
        ap = argparse.ArgumentParser()
        ap.add_argument("-n", "--new", type=int, default=-1)
        args = vars(ap.parse_args())
        image = cv2.imread('image_resize.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        # find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # sort the contours from left-to-right
        # point colors
        (cnts, _) = contours.sort_contours(cnts)
        colors = ((0, 0, 255), (240, 0, 159), (255, 0, 0), (255, 255, 0))

        # loop over the contours individually
        for (i, c) in enumerate(cnts):
            if cv2.contourArea(c) < 100:
                continue
            # draw the contours
            box = cv2.minAreaRect(c)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
            # show the original coordinates
            print("Object #{}:".format(i + 1))


            # print(box)

            # split the numpy to find the greatest elements in y's
            x0, y0 = np.split(box, 2, axis=1)
            arr_x0 = np.array(x0)
            arr_y0 = np.array(y0)

            r1 = arr_y0[0]
            num1 = 0
            for i1 in range(len(arr_y0)):
                if r1 <= arr_y0[i1]:
                    r1 = arr_y0[i1]
                    num1 = i1
            x1 = arr_x0[num1]
            y1 = arr_y0[num1]

            arr_y0 = np.delete(arr_y0, num1, axis=0)
            r2 = arr_y0[0]
            num2 = 0
            for i2 in range(len(arr_y0)):
                if r2 <= arr_y0[i2]:
                    r2 = arr_y0[i2]
                    num2 = i2
            x2 = arr_x0[num2]
            y2 = arr_y0[num2]
            # finding the line slope
            if x1 - x2 == 0:
                line_slope = 0
            else:
                line_slope = (y1 - y2) / (x1 - x2)
                np.float64(line_slope)

            degree = line_slope * 180 / math.pi
            print("line slope: ", np.float64(degree))

            if degree >= 0:
                print('point+:', x1, '  ', y1)
                output[i + 1] = {"x": int(x1), "y": int(y1), "z": np.float64(degree)}
            elif degree < 0:
                print('point-:', x2, '  ', y2)
                output[i + 1] = {"x": int(x2), "y": int(y2), "z": np.float64(degree)}
            # else:
            #     print('no point')

            rect = np.zeros((4, 2), dtype="float32")
            s = box.sum(axis=1)
            rect[0] = box[np.argmin(s)]
            rect[2] = box[np.argmax(s)]
            diff = np.diff(box, axis=1)
            rect[1] = box[np.argmin(diff)]
            rect[3] = box[np.argmax(diff)]
            # rect = self.order_points_old(self, box)
            # ordering the coordinates
            if args["new"] > 0:
                rect = perspective.order_points(box)
            # loop over the original points and draw them
            for ((x, y), color) in zip(rect, colors):
                cv2.circle(image, (int(x), int(y)), 5, color, -1)
            # draw the object num at the top-left corner
            cv2.putText(image, "Object #{}".format(i + 1),
                        (int(rect[0][0] - 15), int(rect[0][1] - 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        # plt.imshow(image), plt.colorbar(), plt.show()
        print("*******************************************************")
        cv2.waitKey(0)
        return output

#
# r = Run()
# r.mainCode(imagePath="images/img.png")
# for i in out:
#     print(i)
#     print(out[i])
