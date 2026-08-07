"""Application entry point for Q-S-Ali Media Downloader."""

import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from qsali_media_downloader.engine import APP_NAME
from qsali_media_downloader.theme import STYLESHEET
from qsali_media_downloader.ui.main_window import ORG, MainWindow, resource


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG)
    app.setStyleSheet(STYLESHEET)

    icon_path = resource('icon.ico')
    if os.path.isfile(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    QTimer.singleShot(0, lambda: window.folder_edit.setCursorPosition(0))
    return app.exec()
