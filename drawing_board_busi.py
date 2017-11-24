# -*- coding: utf-8 -*-

import sys
import logging
import os

from PyQt5.QtGui import QPainter, QPen, QPixmap, QIcon
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget,
                             QPushButton, QMenu, QFileDialog)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class DrawingBoardUIBusi(QMainWindow):
    def __init__(self):
        super(DrawingBoardUIBusi, self).__init__()

        self.resolution = QDesktopWidget().availableGeometry()  # 获取显示器的分辨率-->(0, 0, 1366, 728)
        self.monitor = QDesktopWidget()  # 获得显示器的物理尺寸
        # self.setWindowFlags(Qt.Tool | Qt.X11BypassWindowManagerHint)  # 任务栏隐藏图标
        self.setupBusi()
        self.setupUi()

    def setupUi(self):

        self.setWindowTitle('白板')  # 设置标题
        self.setWindowIcon(QIcon("qrc\Icon.png"))  # 设置图标
        # self.setWindowFlags(Qt.Tool | Qt.X11BypassWindowManagerHint)  # 任务栏隐藏图标
        self.setWindowTitle('当前' + str(self.page) + '页')

        # 创建白板的功能键
        names = ['清屏', '保存', '切换', '上一页', '下一页', '黑笔', '蓝笔', '红笔', '功能', '恢复', '加载']

        # 各个按钮的位置
        positions = [(self.resolution.width() - self.resolution.height() / 11,
                      (y * self.resolution.height() / 11)) for y in range(0, 11)]

        # 每个功能按钮的高度
        height = (self.resolution.height() / 11) / self.resolution.height() * self.monitor.height()

        # for position, name in zip(positions, names):
        #     button = QPushButton(name, self)
        #     button.resize(height * 0.9, height * 0.9)
        #     button.move(position[0], position[1])
        #     button.setEnabled(True)
        #     # button.hide()


        '''要重构这部分代码'''

        self.btn_clean = QPushButton(names[0], self)
        self.btn_clean.resize(height * 0.9, height * 0.9)
        self.btn_clean.move(positions[0][0], positions[0][1])
        self.btn_clean.clicked.connect(self.clearScree)

        self.btn_savePicture = QPushButton(names[1], self)
        self.btn_savePicture.resize(height * 0.9, height * 0.9)
        self.btn_savePicture.move(positions[1][0], positions[1][1])
        self.btn_savePicture.clicked.connect(lambda: self.savePicture(False))

        self.btn_switch = QPushButton(names[2], self)
        self.btn_switch.resize(height * 0.9, height * 0.9)
        self.btn_switch.move(positions[2][0], positions[2][1])
        self.btn_switch.clicked.connect(self.switch)

        self.btn_previousPage = QPushButton(names[3], self)
        self.btn_previousPage.resize(height * 0.9, height * 0.9)
        self.btn_previousPage.move(positions[3][0], positions[3][1])
        self.btn_previousPage.clicked.connect(self.previousPage)

        self.btn_nextPage = QPushButton(names[4], self)
        self.btn_nextPage.resize(height * 0.9, height * 0.9)
        self.btn_nextPage.move(positions[4][0], positions[4][1])
        self.btn_nextPage.clicked.connect(self.nextPage)

        self.btn_changeColor1 = QPushButton(names[5], self)
        self.btn_changeColor1.resize(height * 0.9, height * 0.9)
        self.btn_changeColor1.move(positions[5][0], positions[5][1])
        self.btn_changeColor1.clicked.connect(lambda: self.changeColor(0))
        self.btn_changeColor1.setEnabled(True)
        self.btn_changeColor1.setCheckable(True)

        self.btn_changeColor2 = QPushButton(names[6], self)
        self.btn_changeColor2.resize(height * 0.9, height * 0.9)
        self.btn_changeColor2.move(positions[6][0], positions[6][1])
        self.btn_changeColor2.clicked.connect(lambda: self.changeColor(1))
        self.btn_changeColor2.setEnabled(True)

        self.btn_changeColor3 = QPushButton(names[7], self)
        self.btn_changeColor3.resize(height * 0.9, height * 0.9)
        self.btn_changeColor3.move(positions[7][0], positions[7][1])
        self.btn_changeColor3.clicked.connect(lambda: self.changeColor(2))
        self.btn_changeColor3.setEnabled(True)

        self.btn_startSharing = QPushButton(names[8], self)
        self.btn_startSharing.resize(height * 0.9, height * 0.9)
        self.btn_startSharing.move(positions[8][0], positions[8][1])
        self.btn_startSharing.clicked.connect(self.startSharing)

        self.btn_restorePicture = QPushButton(names[9], self)
        self.btn_restorePicture.resize(height * 0.9, height * 0.9)
        self.btn_restorePicture.move(positions[9][0], positions[9][1])
        self.btn_restorePicture.clicked.connect(self.restorePicture)

        self.btn_loadPicture = QPushButton(names[10], self)
        self.btn_loadPicture.resize(height * 0.9, height * 0.9)
        self.btn_loadPicture.move(positions[10][0], positions[10][1])
        self.btn_loadPicture.clicked.connect(self.loadPicture)

    def setupBusi(self):
        '''
        实现业务（信号和槽的连接）
        '''

        # 页数记录
        self.page = 1  # 当前所在页页码
        self.pages = 1  # 总页数

        # 记录笔迹（坐标，颜色）
        self.penColor = 0  # 笔的初始颜色黑色
        self.pos_xyc = []  # [((x, y), c)]  c->0 1 2
        self.pos_pages = {}  # 存放所有页笔画路径{page : pos_xyc}

        # 设置不追踪鼠标
        self.setMouseTracking(False)

        # 使用指定的画笔，宽度，钢笔样式，帽子样式和连接样式构造笔
        self.pen = QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        # 绘制在窗体上的painter
        self.paintToWindow = QPainter(self)
        self.paintToWindow.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # 画布QPixMap
        self.pixMap = QPixmap(self.resolution.size())
        self.pixMap.fill(Qt.white)

        # 绘制在画布上的painter
        self.paintToPix = QPainter(self.pixMap)
        self.paintToPix.setRenderHint(QPainter.SmoothPixmapTransform, True)

    def paintEvent(self, event):
        '''绘图事件'''

        # 绘制在窗口上
        self.paintToWindow.begin(self)

        # 绘制在PixMap上
        self.paintToPix.begin(self.pixMap)

        '''
            首先判断pos_xy列表中是不是至少有两个点了
            然后将pos_xy中第一个点赋值给point_start
            利用中间变量pos_tmp遍历整个pos_xy列表
                point_end = pos_tmp

                判断point_end是否是断点，如果是
                    point_start赋值为断点
                    continue
                判断point_start是否是断点，如果是
                    point_start赋值为point_end
                    continue

                画point_start到point_end之间的线
                point_start = point_end
            这样，不断地将相邻两个点之间画线，就能留下鼠标移动轨迹了
        '''

        if len(self.pos_xyc) > 1:
            point_start = self.pos_xyc[0][0]

            for pos_tmp in self.pos_xyc:

                point_end = pos_tmp[0]

                if point_end == (-1, -1):
                    point_start = (-1, -1)
                    continue
                if point_start == (-1, -1):
                    point_start = point_end
                    continue

                if pos_tmp[1] == 2:
                    self.pen.setColor(Qt.red)
                elif pos_tmp[1] == 1:
                    self.pen.setColor(Qt.blue)

                elif pos_tmp[1] == 0:
                    self.pen.setColor(Qt.black)

                # 绘制在窗体和pixmap上
                self.paintToWindow.setPen(self.pen)
                self.paintToPix.setPen(self.pen)

                self.paintToWindow.drawLine(point_start[0], point_start[1], point_end[0], point_end[1])
                self.paintToPix.drawLine(point_start[0], point_start[1], point_end[0], point_end[1])

                point_start = point_end

        self.paintToPix.end()
        self.paintToWindow.end()

    def mouseMoveEvent(self, event):
        '''
            按住鼠标移动事件：将当前点添加到pos_xy列表中
            调用update()函数在这里相当于调用paintEvent()函数
            每次update()时，之前调用的paintEvent()留下的痕迹都会清空
        '''
        # 中间变量pos_tmp提取当前点
        if event.buttons() == Qt.LeftButton:
            pos_tmp = (event.pos().x(), event.pos().y())
            self.pos_xyc.append((pos_tmp, self.penColor))
            self.update()

    def mouseReleaseEvent(self, event):
        '''
            重写鼠标按住后松开的事件
            在每次松开后向pos_xyc列表中添加一个断点(-1, -1)
            然后在绘画时判断一下是不是断点就行了
            是断点的话就跳过去，不与之前的连续
        '''
        pos_test = (-1, -1)
        self.pos_xyc.append((pos_test, -1))

        self.update()

    def keyPressEvent(self, event):
        '''键盘事件--快捷键'''

        # ESC退出白板
        if event.key() == Qt.Key_Escape:
            self.showMinimized()

    def contextMenuEvent(self, event):
        '''在绘图中的右键菜单'''

        qmenu = QMenu(self)

        cleanScree = qmenu.addAction('清屏', self.clearScree)

        savePictureAct = qmenu.addAction('保存')
        savePictureAct.triggered.connect(lambda: self.savePicture(False))
        switchAct = qmenu.addAction('切换', self.switch)

        qmenu.addSeparator()
        previousPageAct = qmenu.addAction('上一页', self.previousPage)
        nextPageAct = qmenu.addAction('下一页', self.nextPage)
        qmenu.addSeparator()

        self.changeColorBlack = qmenu.addAction('黑笔')
        self.changeColorBlack.triggered.connect(lambda: self.changeColor(0))
        self.changeColorBlue = qmenu.addAction('蓝笔')
        self.changeColorBlue.triggered.connect(lambda: self.changeColor(1))
        self.changeColorRed = qmenu.addAction('红笔')
        self.changeColorRed.triggered.connect(lambda: self.changeColor(2))

        qmenu.addSeparator()

        # self.changeThickness = qmenu.addAction('笔的粗细', self.changeThickness())
        # qmenu.addSeparator()

        qmenu.addAction('功能', self.startSharing)
        qmenu.addAction('恢复', self.restorePicture)
        qmenu.addAction('加载', self.loadPicture)

        self.action = qmenu.exec_(self.mapToGlobal(event.pos()))

    def loadPicture(self):
        '''加载本地图片'''

    def restorePicture(self):
        pass

    def startSharing(self):
        pass

    def changeThickness(self):
        pass

    def changeColor(self, colorNum):
        '''换颜色'''

        colorDic = {0: Qt.black, 1: Qt.blue, 2: Qt.red}

        self.pen.setColor(colorDic[colorNum])
        self.penColor = colorNum

    def nextPage(self):
        '''
        切换下一页画布
        :return:
        '''

        if self.page == self.pages:

            # 当前页为最后一页，保存当前页的内容
            self.savePicture(True)  # 保存当前页内容
            self.pos_pages[self.page] = self.pos_xyc  # 记录当前页笔画路径

            # 开辟新一页
            self.pos_xyc = []  # 当前页路径清空
            self.pages += 1  # 页码加一

        else:

            # 当前页并非最后一页，直接读取下一页路径
            self.pos_xyc = self.pos_pages[self.page + 1]

        self.pixMap.fill(Qt.white)  # 清空画布
        self.update()   # 更新内容
        self.page = self.page + 1  # 当前页码加一
        self.setWindowTitle('当前' + str(self.page) + '/' + str(self.pages) + '页')  # 更新标题栏显示的页码

    def previousPage(self):
        '''
        切换到上一页画布
        :return:
        '''
        logger.debug('切换上一页self.page>1 %s', self.page > 1)

        if self.page == self.pages:

            # 当前页为最后一页，记录最后一页内容
            self.pos_pages[self.page] = self.pos_xyc
            self.savePicture(True)

        if self.page > 1:
            # 当前页码非第一页
            self.page -= 1
            self.pos_xyc = self.pos_pages[self.page]

        else:
            # 当前页码为第一页
            pass

        self.pixMap.fill(Qt.white)  # 清空画布
        self.update()  # 更新内容
        self.setWindowTitle('当前' + str(self.page) + '/' + str(self.pages) + '页')  # 更新标题栏显示的页码

    def switch(self):
        '''切换'''
        self.showMinimized()

    def savePicture(self, flag=True, meetingID='201711'):
        '''
            将当前白板上的内容保存成图片
            flag = True,为自动保存
            flag = False为用户保存
        '''
        # 保存目录 './save/日期+会议号/'
        time = QDateTime.currentDateTime().toString("yyyy-MM-dd_")
        meetingID = meetingID
        filePath = os.path.join(os.getcwd(), 'save', time + meetingID)
        # 创建目录
        if not os.path.exists(filePath):
            os.makedirs(filePath)
            os.makedirs(os.path.join(filePath, 'temp'))

        if flag:

            # 自动保存分为两部分：1.保存图片到本地 2.保存保存路径json文件到本地
            fileName = QDateTime.currentDateTime().toString('yyMMddhhmmss')
            logger.debug('fileName %s', fileName)
            self.pixMap.save(os.path.join(filePath, 'temp', fileName + '.png'))
            logger.debug('保存图片')

            import json
            dict = {'pox_xyc': self.pos_xyc,
                    'page': self.page,
                    'meetingID': meetingID
                    }
            # logger.debug('dict: %s', dict)

            with open(os.path.join(filePath, 'temp', fileName + '.json'), 'w') as f:
                json.dump(dict, f)
            logger.debug('保存json文件')

        else:

            # 用户手动保存
            fileName = QFileDialog.getSaveFileName(self, '保存图片', filePath, ".png;;.jpg")
            self.pixMap.save(fileName[0] + fileName[1])

    def clearScree(self):
        '''清屏'''

        self.pos_xyc.clear()
        self.update()
        self.pixMap.fill(Qt.white)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dbb = DrawingBoardUIBusi()
    # dbb.setupBusi()
    # dbb.setWindowFlags(Qt.Tool | Qt.X11BypassWindowManagerHint)
    dbb.showMaximized()
    sys.exit(app.exec_())
