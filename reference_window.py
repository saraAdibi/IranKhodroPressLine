import sys
from PyQt5.QtWidgets import *
from reference_window_ui import Ui_MainWindow
import cv2
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
import db
import main_project


class ReferenceWindow:
    def __init__(self):
        self.ref_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.ref_win)
        # self.r = main_project.Run()
        self.ui.pushButton_ref_calc.clicked.connect(lambda: self.btnCalculate())
        self.ui.pushButton_ref_submit.clicked.connect(lambda: self.btnSubmit())
        self.ui.pushButton_ref_cap.clicked.connect(lambda: self.CaptureClicked())
        self.logic = 0
        self.value = 1
        self.out = {}
        self.name = ''

    def show(self):
        self.ref_win.show()
        self.onClicked()

    def btnSubmit(self):
        self.name = self.ui.lineEdit.text()
        for i in self.out:
            print(f'object#{i}')
            print('x:', self.out[i]['x'])
            print('y:', self.out[i]['y'])
            print('z:', self.out[i]['z'])
            db.insert(self.name, self.out[i]['x'], self.out[i]['y'], self.out[i]['z'])
        print('submit')

    def btnCalculate(self):
        self.name = self.ui.lineEdit.text()
        print(self.name)
        img_path = str(f"images/{self.name}.png")
        print('step0')
        self.out = main_project.Run(imagePath=img_path).mainCode()
        print('calculate')
        for i in self.out:
            self.ui.label_ref_x.setText(str(self.out[i]['x']))
            self.ui.label_ref_y.setText(str(self.out[i]['y']))
            self.ui.label_ref_z.setText(str(self.out[i]['z']))

    @QtCore.pyqtSlot()
    def onClicked(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == True:
                self.DisplayeImage(frame, 1)
                cv2.waitKey()
                if self.logic == 2:
                    self.value = self.value + 1
                    self.name = self.ui.lineEdit.text()
                    img_path = str(f"images/{self.name}.png")
                    cv2.imwrite(img_path, frame)
                    # self.out = main_project.Run.mainCode()
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
        self.ui.label_ref_live.setPixmap(QPixmap.fromImage(img))
        self.ui.label_ref_pic.setPixmap(QPixmap(f"images/{self.name}.png"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ref_win = ReferenceWindow()
    ref_win.show()
    ref_win.onClicked()
    sys.exit(app.exec_())
