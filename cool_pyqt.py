# 使用例子
import sys
import os
from qt_material import apply_stylesheet
# from PySide6 import QtWidgets
# from PySide2 import QtWidgets
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem, QDesktopWidget, QStatusBar
from material_ui import Ui_MainWindow

from tqdm import trange
import pandas as pd

import estimate

USING_DP = False
if USING_DP:
    import dp_code
else:
    import deposition_replenishment_algorithm

class MyMainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.move(400, 100)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.pushButton_importSupply.clicked.connect(self.importSupply_clicked)
        self.pushButton_browseSupply.clicked.connect(self.importSupply_clicked)
        self.action_importSupply.triggered.connect(self.importSupply_clicked)

        self.pushButton_importSales.clicked.connect(self.importSales_clicked)
        self.pushButton_browseSales.clicked.connect(self.importSales_clicked)
        self.action_importSales.triggered.connect(self.importSales_clicked)

        self.pushButton_exit.clicked.connect(self.exit_clicked)
        self.action_exit.triggered.connect(self.exit_clicked)

        self.pushButton_estimateParams.clicked.connect(
            self.estimate_params_clicked)

        self.pushButton_calculate.clicked.connect(self.make_plan)

        self.action_CSV.triggered.connect(self.export_csv)
        self.action_Excel.triggered.connect(self.export_excel)
        self.action_clipboard.triggered.connect(self.export_clipboard)
        self.action_HTML.triggered.connect(self.export_html)

        self.cwd = os.getcwd()
        self.df_supply = None
        self.df_sales = None
        self.df_plan = None

    def importSupply_clicked(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "导入供应数据", self.cwd,
                                                         "CSV文件(*.csv);;Excel文件(*.xls;*.xlsx)")
        self.tabWidget.setCurrentWidget(self.tab_supply)
        if(filename == ""):
            return
        if(filetype == "CSV文件(*.csv)"):
            self.setWindowTitle("导入中，请坐和放宽")
            self.lineEdit_supplyPath.setText(filename)
            print(f'正在读取{filename}')
            self.df_supply = pd.read_csv(filename, encoding="gbk")
            ret = QMessageBox.question(
                self, "是否加载数据到图形界面", "是否加载数据到图形界面？这可能会花费非常多时间", QMessageBox.Yes | QMessageBox.No)
            if(ret == QMessageBox.Yes):
                row_count = self.df_supply.shape[0] + 1
                self.tableWidget_supply.clear()
                self.tableWidget_supply.setRowCount(row_count)
                self.tableWidget_supply.setColumnCount(
                    len(self.df_supply.columns))
                for i in range(len(self.df_supply.columns)):
                    item = QTableWidgetItem(self.df_supply.columns[i])
                    self.tableWidget_supply.setItem(0, i, item)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                for j in trange(row_count - 1):
                    for i in range(len(self.df_supply.columns)):
                        item = QTableWidgetItem(
                            str(self.df_supply[self.df_supply.columns[i]][j]))
                        self.tableWidget_supply.setItem(j+1, i, item)
                        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.setWindowTitle("采购计划制定系统")
            self.statusbar.showMessage("导入供应数据完成", 5000)
        elif(filetype == "Excel文件(*.xls;*.xlsx)"):
            QMessageBox.information(
                self, "提示", filetype + "暂不支持，敬请期待", QMessageBox.Yes)

    def importSales_clicked(self):
        filename, filetype = QFileDialog.getOpenFileName(self, "导入销售数据", self.cwd,
                                                         "CSV文件(*.csv);;Excel文件(*.xls;*.xlsx)")
        self.tabWidget.setCurrentWidget(self.tab_sales)
        if(filename == ""):
            return
        if(filetype == "CSV文件(*.csv)"):
            self.setWindowTitle("导入中，请坐和放宽")
            self.lineEdit_salesPath.setText(filename)
            print(f'正在读取{filename}')
            self.df_sales = pd.read_csv(filename, encoding="gbk")
            ret = QMessageBox.question(
                self, "是否加载数据到图形界面", "是否加载数据到图形界面？这可能会花费非常多时间", QMessageBox.Yes | QMessageBox.No)
            if(ret == QMessageBox.Yes):
                row_count = self.df_sales.shape[0] + 1
                self.tableWidget_sales.clear()
                self.tableWidget_sales.setRowCount(row_count)
                self.tableWidget_sales.setColumnCount(
                    len(self.df_sales.columns))
                for i in range(len(self.df_sales.columns)):
                    item = QTableWidgetItem(self.df_sales.columns[i])
                    self.tableWidget_sales.setItem(0, i, item)
                    item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                for j in trange(row_count - 1):
                    for i in range(len(self.df_sales.columns)):
                        item = QTableWidgetItem(
                            str(self.df_sales[self.df_sales.columns[i]][j]))
                        self.tableWidget_sales.setItem(j+1, i, item)
                        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.setWindowTitle("采购计划制定系统")
            self.statusbar.showMessage("导入销售数据完成", 5000)
        elif(filetype == "Excel文件(*.xls;*.xlsx)"):
            QMessageBox.information(
                self, "提示", filetype + "暂不支持，敬请期待", QMessageBox.Ok)

    def estimate_params_clicked(self):
        if(self.df_sales is None and self.df_supply is None):
            QMessageBox.information(
                self, "提示", "请导入供应数据与销售数据", QMessageBox.Ok)
            return
        if(self.df_sales is None):
            QMessageBox.information(
                self, "提示", "请导入销售数据", QMessageBox.Ok)
            return
        if(self.df_supply is None):
            QMessageBox.information(
                self, "提示", "请导入供应数据", QMessageBox.Ok)
            return
        self.estimate_params()

    def estimate_params(self):
        try:
            self.lamda = estimate.estimate_lambda(
                self.df_sales, resample=self.lineEdit_L_base.text()+'d')
            self.c, self.L = estimate.estimate_c_L(self.df_supply)
            self.lineEdit_lambda.setText(f'{self.lamda:.2f}')
            self.lineEdit_c.setText(f'{self.c:.2f}')
            self.lineEdit_L.setText(f'{self.L:.2f}')
            self.statusbar.showMessage("参数估计完成", 5000)
        except Exception as e:
            print(e)
            QMessageBox.warning(
                self, "提示", f'参数估计出错(错误消息：{e})，请检查数据正确性', QMessageBox.Ok)

    def make_plan(self):
        try:
            self.estimate_params()
            self.tabWidget.setCurrentWidget(self.tab_plan)
            T = int(self.lineEdit_T.text())
            b = float(self.lineEdit_b.text())
            h = float(self.lineEdit_h.text())
            beta = float(self.lineEdit_beta.text())
            lamda = int(self.lamda / float(self.lineEdit_lambda_base.text()))
            c = self.c
            L = int(self.L / float(self.lineEdit_L_base.text()))
            df = self.df_sales
            df['date'] = pd.to_datetime(df['下单时间'])
            df = df.set_index('date')
            daily_sales_sum = df[df['ProductName'] == '中长款无毛领羽绒服'].resample(
                self.lineEdit_L_base.text()+'d').sum(numeric_only=True)
            d = daily_sales_sum['销量'].values / \
                float(self.lineEdit_lambda_base.text())
            print('d:', d)
            d = d.astype(int)
            print('d:', d)
            if USING_DP:
                planner = dp_code.DpPlanner(T, b, h, beta, lamda, c, L)
                p = planner.dp(d)
            else:
                m = 0
                n = 0
                np = 0
                planner = deposition_replenishment_algorithm.DepositionReplenishmentAlgorithm(T, c, b, h, beta, L, m, n, np, lamda)
                q_list, min_v = planner.run(d)
                p = list(q_list.values())
            self.df_plan = pd.DataFrame(p, columns=['采购量'], index=[
                                        i for i in range(1, len(p)+1)])
            self.df_plan.index.name = '周期'
            self.update_plan_table()
            self.statusbar.showMessage("采购计划计算完成", 5000)
        except Exception as e:
            print(e)
            QMessageBox.warning(
                self, "提示", f'计算采购计划失败(错误消息：{e})', QMessageBox.Ok)

    def update_plan_table(self):
        if(self.df_plan is None):
            return
        row_count = self.df_plan.shape[0] + 1
        self.tableWidget_plan.clear()
        self.tableWidget_plan.setRowCount(row_count)
        self.tableWidget_plan.setColumnCount(2)
        item = QTableWidgetItem(self.df_plan.index.name)
        self.tableWidget_plan.setItem(0, 0, item)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        item = QTableWidgetItem(self.df_plan.columns[0])
        self.tableWidget_plan.setItem(0, 1, item)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        for i in range(1, row_count):
            item = QTableWidgetItem(str(i))
            self.tableWidget_plan.setItem(i, 0, item)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            item = QTableWidgetItem(
                str(self.df_plan[self.df_plan.columns[0]].values[i-1]))
            self.tableWidget_plan.setItem(i, 1, item)
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)

    def export_csv(self):
        if(self.df_plan is None):
            return
        filename, filetype = QFileDialog.getSaveFileName(self, "导出采购计划", self.cwd+"/采购计划.csv",
                                               "CSV文件(*.csv)")
        if(filename == ""):
            return
        self.df_plan.to_csv(filename)

    def export_excel(self):
        if(self.df_plan is None):
            return
        filename, filetype = QFileDialog.getSaveFileName(self, "导出采购计划", self.cwd+"/采购计划.xlsx",
                                               "Excel文件(*.xls;*.xlsx)")
        if(filename == ""):
            return
        self.df_plan.to_excel(filename)
        
    def export_html(self):
        if(self.df_plan is None):
            return
        filename, filetype = QFileDialog.getSaveFileName(self, "导出采购计划", self.cwd+"/采购计划.html",
                                               "html文件(*.htm;*.html)")
        if(filename == ""):
            return
        self.df_plan.to_html(filename)


    def export_clipboard(self):
        if(self.df_plan is None):
            return
        self.df_plan.to_clipboard()

    def exit_clicked(self):
        app = QtWidgets.QApplication.instance()
        app.quit()


QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(
    QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons

# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = MyMainForm()

# setup stylesheet
apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

# run
window.show()
app.exec_()
