import os, sys

from script import GPTWrapper

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QWidget, QMessageBox, QGroupBox, \
    QFormLayout, QSpinBox, QComboBox, QSplitter, QSizePolicy
from PyQt5.QtCore import Qt, QCoreApplication, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QFont

from apiWidget import ApiWidget
from imageView import ImageView

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))


class Thread(QThread):
    generatedFinished = pyqtSignal(str)
    errorGenerated = pyqtSignal(str)

    def __init__(self, wrapper: GPTWrapper, sex, ethnicity, age):
        super(Thread, self).__init__()
        self.__wrapper = wrapper
        self.__sex = sex
        self.__ethnicity = ethnicity
        self.__age = age

    def run(self):
        try:
            image = self.__wrapper.get_profile_image(self.__sex, self.__ethnicity, self.__age)
            self.generatedFinished.emit(image)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__wrapper = GPTWrapper()

        self.__settings_ini = QSettings('settings.ini', QSettings.IniFormat)

        self.__settings_ini.beginGroup('DALLE')

        if not self.__settings_ini.contains('sex'):
            self.__settings_ini.setValue('sex', 'Female')
        if not self.__settings_ini.contains('ethnicity'):
            self.__settings_ini.setValue('ethnicity', 'Caucasian')
        if not self.__settings_ini.contains('age'):
            self.__settings_ini.setValue('age', 30)

        self.__sex = self.__settings_ini.value('sex', type=str)
        self.__ethnicity = self.__settings_ini.value('ethnicity', type=str)
        self.__age = self.__settings_ini.value('age', type=int)

        self.__settings_ini.endGroup()

    def __initUi(self):
        self.setWindowTitle('Sample Profile Image Generator')

        self.__sexComboBox = QComboBox()
        self.__sexComboBox.addItems([
            'Male', 'Female'
        ])
        self.__sexComboBox.setCurrentText(self.__sex)

        self.__ethnicityComboBox = QComboBox()
        self.__ethnicityComboBox.addItems([
            'Caucasian',
            'African',
            'Asian',
            'Hispanic',
            'Middle Eastern',
            'Indian',
            'Native American',
        ])
        self.__ethnicityComboBox.setCurrentText(self.__ethnicity)

        self.__ageSpinBox = QSpinBox()
        self.__ageSpinBox.setRange(0, 100)
        self.__ageSpinBox.setValue(self.__age)

        self.__sexComboBox.currentTextChanged.connect(self.__paramChanged)
        self.__ethnicityComboBox.currentTextChanged.connect(self.__paramChanged)
        self.__ageSpinBox.valueChanged.connect(self.__paramChanged)

        lay = QFormLayout()
        lay.addRow('Sex', self.__sexComboBox)
        lay.addRow('Ethnicity', self.__ethnicityComboBox)
        lay.addRow('Age', self.__ageSpinBox)

        settingsGrpBox = QGroupBox('Settings')
        settingsGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(settingsGrpBox)

        leftWidget = QWidget()
        leftWidget.setLayout(lay)

        self.__apiWidget = ApiWidget()
        self.__apiWidget.apiKeyAccepted.connect(self.__setApi)
        self.__apiWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.__runBtn = QPushButton('Run')
        self.__runBtn.clicked.connect(self.__run)

        self.__imageView = ImageView()

        lay = QVBoxLayout()
        lay.addWidget(self.__runBtn)
        lay.addWidget(self.__imageView)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(leftWidget)
        splitter.addWidget(rightWidget)
        splitter.setHandleWidth(2)

        splitter.setChildrenCollapsible(False)
        splitter.setSizes([500, 500])
        splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(splitter)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

    # get change event of sex, ethnicity, age
    def __paramChanged(self, v):
        sender = self.sender()
        self.__settings_ini.beginGroup('DALLE')
        if sender == self.__sexComboBox:
            self.__sex = v
            self.__settings_ini.setValue('sex', self.__sex)
        elif sender == self.__ethnicityComboBox:
            self.__ethnicity = v
            self.__settings_ini.setValue('ethnicity', self.__ethnicity)
        elif sender == self.__ageSpinBox:
            self.__age = v
            self.__settings_ini.setValue('age', self.__age)
        self.__settings_ini.endGroup()


    def __run(self):
        self.__wrapper.set_api(self.__apiWidget.getApi())
        self.__t = Thread(self.__wrapper, self.__sex, self.__ethnicity, self.__age)
        self.__t.started.connect(self.__started)
        self.__t.finished.connect(self.__finished)
        self.__t.generatedFinished.connect(self.__imageView.setBJson)
        self.__t.errorGenerated.connect(self.__showError)
        self.__t.start()

    def __setApi(self, api):
        self.__wrapper.set_api(api)

    def __showError(self, e):
        QMessageBox.critical(self, 'Error', e)

    def __started(self):
        self.__runBtn.setEnabled(False)

    def __finished(self):
        self.__runBtn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())