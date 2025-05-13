# coding:utf-8
import sys
from pathlib import Path
import pdfplumber
import json
import os
import time

from PySide6.QtCore import Qt, QPoint, QSize, QUrl, QRect, QPropertyAnimation,QTimer,QRegularExpression
from PySide6.QtGui import QIcon, QFont, QColor, QPainter,QPixmap,QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGraphicsOpacityEffect,QLabel

from qfluentwidgets import (CardWidget, setTheme, Theme, IconWidget, BodyLabel, CaptionLabel, PushButton,
                            TransparentToolButton, FluentIcon, RoundMenu, Action, ElevatedCardWidget,
                            ImageLabel, isDarkTheme, FlowLayout, MSFluentTitleBar, SimpleCardWidget,
                            HeaderCardWidget, InfoBarIcon, HyperlinkLabel, HorizontalFlipView,
                            PrimaryPushButton, TitleLabel, PillPushButton, setFont, SingleDirectionScrollArea,StateToolTip,
                            VerticalSeparator, FluentWindow, NavigationItemPosition,FolderListDialog,PrimaryPushButton,PushButton,TextEdit,IndeterminateProgressBar)

from qfluentwidgets.components.widgets.acrylic_label import AcrylicBrush




class LightBox(QWidget):
    """ Light box """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
        else:
            tintColor = QColor(255, 255, 255, 160)

        self.acrylicBrush = AcrylicBrush(self, 80, tintColor, QColor(0, 0, 0, 0))

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(self.opacityEffect, b"opacity", self)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.vBoxLayout = QVBoxLayout(self)
        self.closeButton = TransparentToolButton(FluentIcon.CLOSE, self)
        self.flipView = HorizontalFlipView(self)
        self.nameLabel = BodyLabel('表格图片 1', self)
        self.pageNumButton = PillPushButton('1 / 4', self)

        self.pageNumButton.setCheckable(False)
        self.pageNumButton.setFixedSize(80, 32)
        setFont(self.nameLabel, 16, QFont.DemiBold)

        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIconSize(QSize(14, 14))
        self.closeButton.clicked.connect(self.fadeOut)

        self.vBoxLayout.setContentsMargins(26, 28, 26, 28)
        self.vBoxLayout.addWidget(self.closeButton, 0, Qt.AlignRight | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.flipView, 1)
        self.vBoxLayout.addWidget(self.nameLabel, 0, Qt.AlignHCenter)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.pageNumButton, 0, Qt.AlignHCenter)

        self.flipView.addImages([
            'resource/1_square.png', 'resource/2_square.png',
            'resource/3_square.png', 'resource/4_square.png',
        ])
        self.flipView.currentIndexChanged.connect(self.setCurrentIndex)

    def setCurrentIndex(self, index: int):
        self.nameLabel.setText(f'表格图片 {index + 1}')
        self.pageNumButton.setText(f'{index + 1} / {self.flipView.count()}')
        self.flipView.setCurrentIndex(index)

    def paintEvent(self, e):
        if self.acrylicBrush.isAvailable():
            return self.acrylicBrush.paint()

        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if isDarkTheme():
            painter.setBrush(QColor(32, 32, 32))
        else:
            painter.setBrush(QColor(255, 255, 255))

        painter.drawRect(self.rect())

    def resizeEvent(self, e):
        w = self.width() - 52
        self.flipView.setItemSize(QSize(w, w * 9 // 16))

    def fadeIn(self):
        rect = QRect(self.mapToGlobal(QPoint()), self.size())
        self.acrylicBrush.grabImage(rect)

        self.opacityAni.setStartValue(0)
        self.opacityAni.setEndValue(1)
        self.opacityAni.setDuration(150)
        self.opacityAni.start()
        self.show()

    def fadeOut(self):
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.setDuration(150)
        self.opacityAni.finished.connect(self._onAniFinished)
        self.opacityAni.start()

    def _onAniFinished(self):
        self.opacityAni.finished.disconnect()
        self.hide()



#图片展示
class GalleryCard(HeaderCardWidget):
    """ Gallery card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('对应表格图片')

        self.flipView = HorizontalFlipView(self)

        self.expandButton = TransparentToolButton(
            FluentIcon.CHEVRON_RIGHT_MED, self)
        self.expandButton.setFixedSize(32, 32)
        self.expandButton.setIconSize(QSize(12, 12))

        images = ['resource/1_square.png', 'resource/2_square.png', 'resource/3_square.png', 'resource/4_square.png']

        self.flipView.addImages(images)
        self.flipView.setBorderRadius(8)
        self.flipView.setSpacing(10)


        self.headerLayout.addWidget(self.expandButton, 0, Qt.AlignRight)
        self.viewLayout.addWidget(self.flipView)


#描述格子
class DescriptionCard(HeaderCardWidget):
    """ Description card """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.descriptionLabel = BodyLabel(
            '您PDF中的表格已被成功提取😘', self)

        self.descriptionLabel.setWordWrap(True)
        self.viewLayout.addWidget(self.descriptionLabel)
        self.setTitle('系统提示')


class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        key_format = QTextCharFormat()
        key_format.setForeground(QColor(77, 116, 255))  # 浅蓝色
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(255, 140, 0))  # 橘黄色
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor(30, 144, 255))  # 深蓝色

        self.highlighting_rules = [
            (r'".*?"\s*(?=:)', key_format),  # 匹配key并高亮为浅蓝色
            (r'(?<=:)\s*(".*?")', value_format),  # 匹配冒号后的value并高亮为橘黄色
            (r'[{}]', bracket_format)  # 匹配大括号并高亮为深蓝色
        ]

    def highlightBlock(self, text):
        for pattern, char_format in self.highlighting_rules:
            expression = QRegularExpression(pattern)
            match = expression.match(text)
            while match.hasMatch():
                length = match.capturedLength()
                self.setFormat(match.capturedStart(), length, char_format)
                match = expression.match(text, match.capturedEnd())


class LineEditCard(HeaderCardWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.textEdit = TextEdit(self)
        with open('output.json', 'r',encoding="utf-8") as file:
            jsonCode = file.read()
        self.textEdit.setPlainText(jsonCode)
        self.json_highlighter = JsonHighlighter(self.textEdit.document())
        self.viewLayout.addWidget(self.textEdit)
        self.setTitle("JSON识别结果浏览")



class ViewAppInterface(SingleDirectionScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.view = QWidget(self)

        self.vBoxLayout = QVBoxLayout(self.view)
        self.galleryCard = GalleryCard(self)
        self.descriptionCard = DescriptionCard(self)
        self.lineEdit=LineEditCard(self)

        self.lightBox = LightBox(self)
        self.lightBox.hide()
        self.galleryCard.flipView.itemClicked.connect(self.showLightBox)

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("viewAppInterface")

        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 30)
        self.vBoxLayout.addWidget(self.descriptionCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.galleryCard, 0, Qt.AlignTop)
        self.vBoxLayout.addWidget(self.lineEdit,0,Qt.AlignTop)

        
        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet('QWidget {background:transparent}')

    def showLightBox(self):
        index = self.galleryCard.flipView.currentIndex()
        self.lightBox.setCurrentIndex(index)
        self.lightBox.fadeIn()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.lightBox.resize(self.size())


class SettingAppInterface(SingleDirectionScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.input_folder = 
        # self.output_folder = 

        self.view = QWidget(self)

        self.vBoxLayout = QVBoxLayout(self.view)

        # 创建水平布局
        self.horizontalLayout = QHBoxLayout()

        # 添加“选择输入文件”文件夹列表对话框
        self.selectInputFileButton = PushButton("选择输入文件", self, FluentIcon.FOLDER)
        self.selectInputFileButton.clicked.connect(self.show_input_folder_dialog)
        self.horizontalLayout.addWidget(self.selectInputFileButton)

        # 添加“选择输出文件夹”文件夹列表对话框
        self.selectOutputFolderButton = PushButton("选择输出文件夹", self, FluentIcon.FOLDER)
        self.selectOutputFolderButton.clicked.connect(self.show_output_folder_dialog)
        self.horizontalLayout.addWidget(self.selectOutputFolderButton)

        # 将水平布局添加到垂直布局中
        self.vBoxLayout.addLayout(self.horizontalLayout)

        # 添加“开始运行”按钮
        self.startButton = PrimaryPushButton("提取表格", self, FluentIcon.PLAY)
        self.startButton.clicked.connect(self.start_execution)
        self.vBoxLayout.addWidget(self.startButton)

        self.stateTooltip = None
       

        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("settingAppInterface")

        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setContentsMargins(0, 0, 10, 30)
        

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet('QWidget {background:transparent}')

    def show_input_folder_dialog(self):
        folder_paths = []  # 输入文件夹路径列表
        title = "请选择PDF文件"
        content = "请选择输入文件所在的文件夹"
        dialog = FolderListDialog(folder_paths, title, content, parent=self)
        if dialog.exec_():
            self.input_folder = dialog.selected_folder
            self.start_execution(self.input_folder, self.output_folder)
        #dialog.exec_()

    def show_output_folder_dialog(self):
        default_output_folder = "~/Desktop"  # 默认输出文件夹为桌面
        title = "选择输出文件夹位置"
        content = "请选择输出文件的保存文件夹"
        dialog = FolderListDialog([default_output_folder], title, content, parent=self)
        if dialog.exec_():
            self.output_folder = dialog.selected_folder
            self.start_execution(self.input_folder, self.output_folder)
        #dialog.exec_()
    
    def complete_training(self):
        if self.stateTooltip:
            self.stateTooltip.setContent('表格提取完成啦 😆')
            self.stateTooltip.setState(True)
            self.stateTooltip = None
        self.timer.stop()
    
    def start_execution(self):
    #def start_execution(self, input_folder, output_folder):
        # 当点击“开始运行”按钮时执行的内容
        #default_input_folder = "~/Desktop/服务外包/interface"

        # self.progress_bar = IndeterminateProgressBar(self)
        # self.vBoxLayout.addWidget(self.progress_bar)



        default_output_folder = "C:/princ/Desktop/服务外包/interface"



        #path = os.path.join(default_input_folder, "in.pdf")
        #输入路径
        path = "C:/princ/Desktop/服务外包/interface/in.pdf"

        def has_none_value(matrix):
            for row in matrix:
                for element in row:
                    if element is None:
                        return True
            return False

        def count_consecutive_none(matrix):
            count = 0
            for row in matrix:
                if row[0] is None:
                    count += 1
            return count

        def fill_empty_with_previous(lst):
            for i in range(1, len(lst)):
                if lst[i] is None:
                    lst[i] = lst[i-1]
            return lst

        def process_table(table, table_head, keywords):
            result = []
            for row in table[1:]:
                row_data = {}
                for i, keyword in enumerate(keywords):
                    if keyword in row[0]:
                        row[0] = row[0].replace("\n", " ")
                        temp = {}
                        for j, value in enumerate(row[1:]):
                            if value:
                                value = value.replace("\n", " ")
                            temp[table_head[j]] = str(value)
                        row_data[row[0]] = temp if len(temp) > 1 else temp[table_head[0]]
                if row_data:
                    result.append(row_data)
            return result

        keywords = ['申购', '赎回', '认购', '管理']
        result = []
        T1 = time.time()
        path = r"in.pdf"
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        if has_none_value(table):
                            # 复杂表格
                            deepth = count_consecutive_none(table) + 1
                            for index in range(1, len(table)):
                                if (table[index][0] == None):
                                    table[index][0] = table[index - 1][0] 
                            if deepth == 2:
                                table[0][1:] = fill_empty_with_previous(table[0][1:])
                                table[1][1:] = fill_empty_with_previous(table[1][1:])
                                table_head = []
                                for i in range(len(table[0][1:])):
                                    table_head.append(table[0][1:][i] + table[1][1:][i])
                                print(table_head)
                                for row in table[deepth:]:
                                    row_data = {}
                                    for i, keyword in enumerate(keywords):
                                        if keyword in row[0]:
                                            row[0] = row[0].replace("\n", " ")
                                            temp = {}
                                            for j, value in enumerate(row[1:]):
                                                if value:
                                                    value = value.replace("\n", " ")
                                                table_head[j] = table_head[j].replace("\n", " ")
                                                temp[table_head[j]] = str(value)
                                            row_data[row[0]] = temp if len(temp) > 1 else temp
                                            # [table_head[0]] 这个代码接到上一行可以实现赛题示例的那个效果
                                    if row_data:
                                        result.append(row_data)
                            if deepth == 3:
                                    table[0][1:] = fill_empty_with_previous(table[0][1:])
                                    table[1][1:] = fill_empty_with_previous(table[1][1:])
                                    table[2][1:] = fill_empty_with_previous(table[2][1:])
                                    table_head = []
                                    for i in range(len(table[0][1:])):
                                        table_head.append(table[0][1:][i] + table[1][1:][i])
                                    print(table_head)
                                    for row in table[deepth - 1:]:
                                        row_data = {}
                                        for i, keyword in enumerate(keywords):
                                            if keyword in row[0]:
                                                row[0] = row[0].replace("\n", " ")
                                                temp = {}
                                                for j, value in enumerate(row[1:]):
                                                    if value:
                                                        value = value.replace("\n", " ")
                                                    table_head[j] = table_head[j].replace("\n", " ")
                                                    temp[table_head[j]] = str(value)
                                                row_data[row[0]] = temp if len(temp) > 1 else temp
                                                # [table_head[0]] 这个代码接到上一行可以实现赛题示例的那个效果
                                        if row_data:
                                            result.append(row_data)
                        else:
                            # 简单表格
                            table_head = table[0][1:]
                            for row in table[1:]:
                                row_data = {}
                                for i, keyword in enumerate(keywords):
                                    if keyword in row[0]:
                                        row[0] = row[0].replace("\n", " ")
                                        temp = {}
                                        for j, value in enumerate(row[1:]):
                                            if value:
                                                value = value.replace("\n", " ")
                                            table_head[j] = table_head[j].replace("\n", " ")
                                            temp[table_head[j]] = str(value)
                                        row_data[row[0]] = temp if len(temp) > 1 else temp
                                        # [table_head[0]] 这个代码接到上一行可以实现赛题示例的那个效果
                                if row_data:
                                    result.append(row_data)

        T2 = time.time()
        result_json = json.dumps(result, ensure_ascii=False, indent=2)
        print((T2-T1)*1000)
        #输出
        with open('output.json', 'w', encoding='utf-8') as f:
            f.write(result_json)

        self.stateTooltip = StateToolTip('正在提取表格', '客官请耐心等待哦~~', self)
        self.stateTooltip.move(510, 30)
        self.stateTooltip.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.complete_training)
        self.timer.start(2000)  # 10秒后触发 timeout 信号
        

        

        



class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        #self.initWindow()
        #创建子页面
        self.viewAppInterface = ViewAppInterface(self)
        self.settingAppInterface = SettingAppInterface(self)
        self.navigationInterface.setAcrylicEnabled(True)

        self.addSubInterface(self.settingAppInterface,FluentIcon.SETTING, "设置参数", FluentIcon.LIBRARY_FILL, isTransparent=False)
        self.addSubInterface(self.viewAppInterface,FluentIcon.EDIT, "查看结果", FluentIcon.LABEL, isTransparent=False)
        

        self.resize(880, 760)
        self.setWindowTitle('FundTableExtract pre-alpha')
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))

        self.titleBar.raise_()

if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    #设置黑夜模式
    #setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w3 = MainWindow()
    w3.show()
    app.exec_()