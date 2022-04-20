import sys
from PyQt5.QtWidgets import *
from main_ui import Ui_MainWindow
from reference_window import ReferenceWindow
import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
import main_project
import db


class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)
        self.refWindow = ReferenceWindow()
        self.logic = 0
        self.value = 1
        self.r = main_project.Run()
        self.ui.pushButton_live.clicked.connect(lambda: self.onClicked())
        self.ui.pushButton_camera.clicked.connect(lambda: self.CaptureClicked())
        self.ui.pushButton_reference.clicked.connect(lambda: self.refWindow.show())
        self.ui.pushButton_submit.clicked.connect(lambda: self.submit())
        self.out = {}

    # camera
    @QtCore.pyqtSlot()
    def onClicked(self):
        # cap = cv2.VideoCapture('169.254.1.75')
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()

            if ret == True:
                self.DisplayeImage(frame, 1)
                cv2.waitKey()
                if self.logic == 2:
                    self.value = self.value + 1
                    cv2.imwrite("images/img.png", frame)
                    self.logic = 1
            else:
                print("return not found")
        cap.release()
        cv2.destroyAllWindows()

    def CaptureClicked(self):
        self.logic = 2

    def DisplayeImage(self, img, window=1):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGB888
            else:
                qformat = QImage.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.ui.label_camera.setPixmap(QPixmap.fromImage(img))
        self.ui.label_picture.setPixmap(QPixmap("images/img.png"))

    def show(self):
        self.main_win.show()

    def submit(self):
        self.out = main_project.Run(imagePath="images/img.png").mainCode()
        try:
            self.ui.lbl_object1_x.setText(str(self.out[1]['x']))
            self.ui.lbl_object1_y.setText(str(self.out[1]['y']))
            self.ui.lbl_object1_z.setText(str(self.out[1]['z']))
            self.ui.label_object1_null.setText("")
        except:
            self.ui.label_object1_null.setText("Null")

        try:
            self.ui.lbl_object2_x.setText(str(self.out[2]['x']))
            self.ui.lbl_object2_y.setText(str(self.out[2]['y']))
            self.ui.lbl_object2_z.setText(str(self.out[2]['z']))
            self.ui.label_object2_null.setText("")
        except:
            self.ui.label_object2_null.setText("Null")

        try:
            self.ui.lbl_object3_x.setText(str(self.out[3]['x']))
            self.ui.lbl_object3_y.setText(str(self.out[3]['y']))
            self.ui.lbl_object3_z.setText(str(self.out[3]['z']))
            self.ui.label_object3_null.setText("")
        except:
            self.ui.label_object3_null.setText("Null")

        try:
            self.ui.lbl_object4_x.setText(str(self.out[4]['x']))
            self.ui.lbl_object4_y.setText(str(self.out[4]['y']))
            self.ui.lbl_object4_z.setText(str(self.out[4]['z']))
            self.ui.label_object4_null.setText("")
        except:
            self.ui.label_object4_null.setText("Null")

        # print(out)
        # for i in out:
        #     print(out[i])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    main_win.onClicked()
    sys.exit(app.exec_())
