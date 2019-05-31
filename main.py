import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
import noise
from PIL import  Image, ImageQt
from denoise import denoise
import glob
import time
import statistic


class App(QWidget):

    def __init__(self):
        super().__init__()

        self.title = 'Denoising image'
        self.initUI()
        self.resize(1000, 700)
        desktop = QApplication.desktop()
        x = (desktop.width() - self.frameSize().width())//2
        y = (desktop.height() - self.frameSize().height())//2
        self.move(x, y)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.grid = QtWidgets.QGridLayout()

        # Create widget
        self.set_original_img('1.png')

        self.denoising_img_lbl = QLabel(self)
        self.denoising_img_pix = QPixmap('1.png')
        self.denoising_img_lbl.setPixmap(self.denoising_img_pix.scaled(512, 512, QtCore.Qt.KeepAspectRatio))

        self.upload_btn = QtWidgets.QPushButton('Загрузить изображение')
        self.show_img_btn = QtWidgets.QPushButton('Просмотреть оригинальное изображение')
        self.save_btn = QtWidgets.QPushButton('Сохранить изображение')
        self.show_denoising_img_btn = QtWidgets.QPushButton('Просмотреть обработанное изображение')
        self.show_stat_btn = QtWidgets.QPushButton('Просмотреть статистику')
        self.show_stat_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.show_denoising_img_btn.setEnabled(False)
        self.transform_btn = QtWidgets.QPushButton('Обработать изображение')

        self.form_method = QtWidgets.QFormLayout()
        self.select_method_btn = QtWidgets.QComboBox()
        self.get_list_model()
        self.form_method.addRow('Выберите метод:', self.select_method_btn)
        self.form_method.addRow(self.show_stat_btn)
        self.form_method.addRow(self.transform_btn)
        self.method_widget = QWidget()
        self.method_widget.setLayout(self.form_method)

        self.std_input = QtWidgets.QDoubleSpinBox()
        self.apply_noise = QtWidgets.QPushButton('Наложить шум')
        self.is_img_with_noise = QtWidgets.QCheckBox()
        self.form = QtWidgets.QFormLayout()
        self.form.addRow("Дисперсия шума", self.std_input)
        self.form.addRow(self.apply_noise)
        self.form.addRow("Исходное изображение с шумом", self.is_img_with_noise)
        self.form.setFormAlignment(QtCore.Qt.AlignCenter)
        self.f = QWidget()
        self.f.setLayout(self.form)

        self.grid.addWidget(self.upload_btn, 0, 0)
        self.grid.addWidget(self.show_img_btn, 1, 0)
        self.grid.addWidget(self.save_btn, 0, 1)
        self.grid.addWidget(self.show_denoising_img_btn, 1, 1)
        self.grid.addWidget(self.original_img_lbl, 2, 0, 3, 1)
        self.grid.addWidget(self.denoising_img_lbl, 2, 1, 3, 1)
        self.grid.addWidget(self.method_widget, 5, 1)
        self.grid.addWidget(self.f, 5, 0)
        self.setLayout(self.grid)

        self.set_signal()
        icon = QIcon('icon.png')
        self.setWindowIcon(icon)
        self.show()

    def set_signal(self):
        self.upload_btn.clicked.connect(self.upload_img)
        self.show_img_btn.clicked.connect(self.show_original_img)
        self.apply_noise.clicked.connect(self.noise_image)
        self.show_denoising_img_btn.clicked.connect(self.show_denoised_img)
        self.transform_btn.clicked.connect(self.denoise_image)
        self.save_btn.clicked.connect(self.save_image)
        self.show_stat_btn.clicked.connect(self.show_stat)

    def get_list_model(self):
        self.select_method_btn.addItem("Median filter")
        models = glob.glob("./model/*.json")
        models = [m.split('\\')[1][:-5] for m in models]
        for m in models:
            self.select_method_btn.addItem(m)


    def upload_img(self):
        file = QtWidgets.QFileDialog.getOpenFileName(filter="(*.png *.jpg *.jpeg)")
        if file[0] != '':
            self.original_img_path = file[0]
            self.set_original_img(self.original_img_path)

    def set_original_img(self, path):
        try:
            self.original_img_lbl
        except:
            self.original_img_lbl = QLabel(self)
        self.original_img_path = path
        self.original_img_pix = QImage(path)
        self.original_img_pix = self.original_img_pix.convertToFormat(QImage.Format_Grayscale8)
        self.original_img_pix = QPixmap.fromImage(self.original_img_pix)
        self.noising_image = self.original_img_pix.copy()
        self.original_img_lbl.setPixmap(self.original_img_pix.scaled(512, 512, QtCore.Qt.KeepAspectRatio))
        self.original_img_lbl.setAlignment(QtCore.Qt.AlignCenter)

    def show_original_img(self):
        original_img_window = QtWidgets.QWidget(self, QtCore.Qt.Window)
        form = QtWidgets.QFormLayout()
        img_label = QLabel()
        img_label.setPixmap(self.original_img_pix)
        form.addWidget(img_label)
        original_img_window.setLayout(form)
        x = self.x() + self.size().width()//2 - self.original_img_pix.width()//2
        y = self.y() + self.size().height()//2 - self.original_img_pix.height()//2
        original_img_window.move(x, y)
        original_img_window.setWindowTitle('Исходное изображение')
        original_img_window.show()


    def show_denoised_img(self):
        original_img_window = QtWidgets.QWidget(self, QtCore.Qt.Window)
        form = QtWidgets.QFormLayout()
        img_label = QLabel()
        img_label.setPixmap(self.denoising_img_pix)
        form.addWidget(img_label)
        original_img_window.setLayout(form)
        x = self.x() + self.size().width()//2 - self.original_img_pix.width()//2
        y = self.y() + self.size().height()//2 - self.original_img_pix.height()//2
        original_img_window.move(x, y)
        original_img_window.setWindowTitle('Обработанное изображение')
        original_img_window.show()

    def noise_image(self):
        img = self.original_img_pix.toImage()
        img.save('./tmp/1.jpg')
        std = self.std_input.value()
        noise.noise_image('./tmp/1.jpg', std)
        pxmap = QImage('./tmp/1.jpg')
        pxmap = pxmap.convertToFormat(QImage.Format_Grayscale8)
        pxmap = QPixmap.fromImage(pxmap)
        self.noising_image = pxmap
        self.original_img_lbl.setPixmap(pxmap.scaled(512, 512, QtCore.Qt.KeepAspectRatio))

    def denoise_image(self):
        model = self.select_method_btn.currentText()
        self.noising_image.toImage().save('./tmp/tmp.jpg')
        t = time.time()
        denoise(model, './tmp/tmp.jpg')
        self.time = time.time() - t
        pxmap = QImage('./tmp/tmp.jpg')
        pxmap = pxmap.convertToFormat(QImage.Format_Grayscale8)
        self.denoising_img_pix = QPixmap.fromImage(pxmap)
        self.denoising_img_lbl.setPixmap(self.denoising_img_pix.scaled(512, 512, QtCore.Qt.KeepAspectRatio))
        self.show_stat_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.show_denoising_img_btn.setEnabled(True)


    def save_image(self):
        img = self.denoising_img_pix.toImage()
        file = QtWidgets.QFileDialog.getSaveFileName(filter="JPG *.jpg;; JPEG *.jpeg;; PNG *.png")
        if file[0] != '':
            img.save(file[0])

    def show_stat(self):
        self.original_img_pix.save('./tmp/clean.jpeg')
        self.noising_image.save('./tmp/noising.jpeg')
        self.denoising_img_pix.save('./tmp/denoising.jpeg')
        res = ''
        if self.is_img_with_noise.checkState() == 0:
            res = statistic.stat('./tmp/clean.jpeg',
                            './tmp/noising.jpeg',
                            './tmp/denoising.jpeg')

        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                       "Статистика",
                                       "Time: " + str(self.time) + "\n" + res,
                                       buttons=QtWidgets.QMessageBox.Ok,
                                       parent=self)
        result = dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())