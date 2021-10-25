from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    w = Widget()
    w.show()

    sys.exit(app.exec_())