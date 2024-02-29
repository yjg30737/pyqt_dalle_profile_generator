import requests

from PyQt5.QtCore import QSettings, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel


class ApiWidget(QWidget):
    apiKeyAccepted = pyqtSignal(str)

    def __init__(self):
        super(QWidget, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings('settings.ini', QSettings.IniFormat)

        if not self.__settings_ini.contains('api_key'):
            self.__settings_ini.setValue('api_key', '')

        self.__api_key = self.__settings_ini.value('api_key', type=str)

    def __initUi(self):
        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)
        self.__apiLineEdit.setText(self.__api_key)

        submitBtn = QPushButton('Submit')
        submitBtn.clicked.connect(self.__setApi)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setVisible(False)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('API KEY'))
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(submitBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)

        self.setLayout(lay)

        if self.__api_key:
            self.__setApi()

    def __setApi(self):
        try:
            api_key = self.__apiLineEdit.text()
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            f = response.status_code == 200
            if f:
                self.__settings_ini.setValue('API_KEY', api_key)
                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText('API key is valid')
                self.apiKeyAccepted.emit(api_key)
            else:
                raise Exception
        except Exception as e:
            self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
            self.__apiCheckPreviewLbl.setText('API key is invalid')
            print(e)
        finally:
            self.__apiCheckPreviewLbl.show()

    def getApi(self):
        return self.__apiLineEdit.text()