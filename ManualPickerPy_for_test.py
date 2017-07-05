# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 18:17:19 2016

@author: tanakayumiko
"""

"""
**ウェルの数を自由に指定できるようにしたい
**グラフのプロットをもっと早くする
**時刻を取得しグラフに反映する
**回収したサンプルの情報を記録する
  どれをバックグラウンドにするかを選択する手間を省く
**解析したウェルの顕微鏡での番号が表示されるようにする（xmlファイルを読み込む必要）
  輝度を解析して分泌しているウェルを見つけるアルゴリズムを開発したい
"""
import sys
import csv
import numpy as np
from datetime import datetime
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import readFile_v3
import Analyze_for_test
import readXML
import sendGmail

class Run(QtGui.QWidget):
    global Roi_Data_file
    
    def __init__(self):
        super(Run, self).__init__()
        self.initUI()
        self.analyze()
        self.read()
            
    def initUI(self):
        self.analyze_btn = QtGui.QPushButton('Analyze scan:%d'%scan, self)
        self.analyze_btn.clicked.connect(self.analyze)
        self.read_btn = QtGui.QPushButton('Read', self)
        self.read_btn.clicked.connect(self.read)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.analyze_btn)
        self.layout.addWidget(self.read_btn)
        self.setLayout(self.layout)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)#60*1000)
        #self.timer.timeout.connect(self.update)
        
    def analyze(self):
        global rawData
        global rawTime
        global pic
        global scan
        rawData, rawTime = Analyze_for_test.Analyze(scan, protein, nd2_file, Roi_Data_file, status_file, time_file, n)
        self.analyze_btn.setText('Analyze scan:%d'%scan)
        scan += 1

    def read(self):
        global Data
        global Status
        global Time
        global back
        global pic
        global timelag
        global Grid
        global scan
        global body
        global suggestion2
        try:
            Status.to_csv(status_file)
        except:
            pass
        Data, Status, Time = \
        readFile_v3.readFile(Roi_Data_file, status_file, time_file, rawData, rawTime)
        suggestion,Status = readFile_v3.back_fit_suggest(scan, Data, max(scan-15,1),Status)#readFile_v2.fitting(scan, Data, timelag, threthold)
        try:
            for i in range(n):
                for j in range(4):
                    Grid[i].Button[j].setStyleSheet('QPushButton {background-color: %s }'%color[int(Status.ix[i+1,j+1]['Status'])].name())
            p =0
            fig = plt.figure(figsize=(4,3))
            for i in suggestion:
                if Status.ix[i[0],i[1]]['Status'] == 0.0 and i in suggestion2:
                    Grid[i[0]-1].Button[i[1]-1].setStyleSheet('QPushButton {background-color: #ff0000 }')
                    body = body + '%d_%d,\n'%(i[0],i[1])
                    p +=1
                    print 'scan:%d'%scan, i
                    ax = fig.add_subplot(2, 2, p)
                    ax.set_title('%d_%d'%(i[0],i[1]))
                    print 'OK0'
                    ax.plot(Data.ix[i[0],i[1]][scan-20:scan], 'r-o', markersize=2)
                    print 'OK1'                    
                    #ax.plot(range(scan-3,scan),Data.ix[i[0],i[1]][scan-3:scan],'o')
                    print 'OK2'
                    ax.set_ylim([scan-20, scan])                    
                    ax.set_ylim([min(Data.ix[i[0],i[1]][scan-20:scan])-1, max(2,max(Data.ix[i[0],i[1]][scan-20:scan]))])
                    plt.savefig('/Volumes/SINGLECELL/sampledata/20161007_max_test/plot.png')
            plt.close('all')
            if body != '分泌が疑われるサンプル：\n':
                msg = sendGmail.create_message(ADDRESS, to_addr, subject, body, mime, attach_file) 
                #送信
                sendGmail.send(ADDRESS, to_addr, msg)
                body = '分泌が疑われるサンプル：\n'
        except:
            print 'miss'
        suggestion2 = suggestion       

    def update(self):
        try:
            self.analyze()
            self.read()
        except:
            pass
            
class MatplotlibWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(160, 40, 500, 30)
        self.label.setFont(QtGui.QFont('SanSerif', 30))
        
class Plot(QtGui.QWidget):
    def __init__(self):
        super(Plot, self).__init__()
        self.initUI()
        
    def initUI(self):
        self.plot_widget = MatplotlibWidget(self)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.plot_widget)

    @QtCore.pyqtSlot(int, int)
    def singlePlot(self, address, well):
        global Time
        global Status
        if mode == 0:
            t = Time.ix[address]/60000
            line = Data.ix[address,well].values

            self.plot_widget.axis.clear()
            self.plot_widget.axis.grid()
            self.plot_widget.axis.set_xlim([max(len(line)-20,0), len(line)+1])
            self.plot_widget.axis.set_ylim([min(min(line),-0.5), max(max(line),2)])
            slope,intercept,stderr = Status.ix[address,well]['slope'],\
            Status.ix[address,well]['intercept'],Status.ix[address,well]['stderr']
            self.plot_widget.axis.plot([max(scan-15,1)-2, max(scan-5,0)],\
            [slope*(max(scan-15,1))+intercept,slope*max(scan-3,0)+intercept],'--')
            self.plot_widget.axis.plot([max(scan-15,1)-2, max(scan-2,0)],\
            [slope*(max(scan-15,1))+intercept+stderr*sigma,slope*(scan)+intercept+stderr*sigma],'--')

            self.plot_widget.axis.plot(Data.ix[address,well].values,'-o')
            try:
                self.plot_widget.axis.plot([scan-4,scan-3,scan-2],\
                [line[-3],line[-2],line[-1]],'o')#[(8/7)*(line[-3]/2+line[-4]/4+line[-5]/8),(8/7)*(line[-2]/2+line[-3]/4+line[-4]/8),(8/7)*(line[-1]/2+line[-2]/4+line[-3]/8)],'o')
            except:
                pass
            self.plot_widget.canvas.draw()
            self.plot_widget.label.setText('%d_%d : # %s'%(address, well, position[address-1][-3:]))
 
    @QtCore.pyqtSlot(int, int)
    def picture(self, address, well):
        pass
        """
        if mode == 0:
            if   well == 1: a,b,c,d = 0,512,0,512
            elif well == 2: a,b,c,d = 0,512,510,1022
            elif well == 3: a,b,c,d = 512,1024,0,512
            elif well == 4: a,b,c,d = 512,1024,510,1022
            
            pic.default_coords['c'] = protein
            image = np.array(pic[address-1][a:b,c:d])
            self.plot_widget.axis.clear()
            self.plot_widget.axis.imshow(image)
            self.plot_widget.canvas.draw()
            self.plot_widget.label.setText('%d_%d : %s'%(address, well, position[address-1]))
        """
    @QtCore.pyqtSlot(int, int)
    def merge(self, address, well):
        pass
        """
        if mode == 0:
            if   well == 1: a,b,c,d = 0,512,0,512
            elif well == 2: a,b,c,d = 0,512,510,1022
            elif well == 3: a,b,c,d = 512,1024,0,512
            elif well == 4: a,b,c,d = 512,1024,510,1022
            
            pic.default_coords['c'] = 0
            image = np.array(pic[address-1][a:b,c:d])
            self.plot_widget.axis.clear()
            self.plot_widget.axis.imshow(image, cmap = 'gray')
            self.plot_widget.canvas.draw()
            self.plot_widget.label.setText('%d_%d : %s'%(address, well, position[address-1]))
        """
#分泌検出アルゴリズムのパラメータ設定＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾＾
class Parameter(QtGui.QWidget):
    def __init__(self):
        super(Parameter, self).__init__()
        self.initUI()
        
    def initUI(self):
        #パラメーター3つ
        self.Difference = QtGui.QSlider(QtCore.Qt.Horizontal, self)#輝度の差分
        self.Timelag = QtGui.QSlider(QtCore.Qt.Horizontal, self)#いくつ前のタイムポイントと差分をとるか
        self.Threthold = QtGui.QSlider(QtCore.Qt.Horizontal, self)#最初の撮影回との差分の閾値
        
        self.layout = QtGui.QVBoxLayout()
        
        #バーの最大値・最小値・初期値
        self.Difference.setMinimum(0)
        self.Difference.setMaximum(40)
        self.Difference.setValue(difference*10)
        
        self.Timelag.setMinimum(0)
        self.Timelag.setMaximum(10)
        self.Timelag.setValue(timelag)
        
        self.Threthold.setMinimum(0)
        self.Threthold.setMaximum(1000)
        self.Threthold.setValue(threthold*100)
        #ラベル
        self.Dlabel = QtGui.QLabel(self)
        self.Dlabel.setText('Difference %.1f'%difference)
        self.Tlabel = QtGui.QLabel(self)
        self.Tlabel.setText('Timelag %d'%timelag)
        self.Plabel = QtGui.QLabel(self)
        self.Plabel.setText('Threthold %.2f'%threthold)
        #バーとラベルの埋め込み
        self.layout.addWidget(self.Dlabel)
        self.layout.addWidget(self.Difference)
        self.layout.addWidget(self.Tlabel)
        self.layout.addWidget(self.Timelag)
        self.layout.addWidget(self.Plabel)
        self.layout.addWidget(self.Threthold)
        self.setLayout(self.layout)
        #バーの値を変更した時changeValueにとぶ
        self.Difference.valueChanged[int].connect(self.changeValue)
        self.Timelag.valueChanged[int].connect(self.changeValue)
        self.Threthold.valueChanged[int].connect(self.changeValue)
        
        self.show()
        
    def changeValue(self, value):
        global difference
        global timelag
        global threthold
        
        sender = self.sender()
         
        if sender == self.Difference:
            difference = value/10.0
            self.Dlabel.setText('Difference %.1f'%difference)
        elif sender == self.Timelag:
            timelag = value
            self.Tlabel.setText('Timelag %d'%timelag)
        elif sender == self.Threthold:
            threthold = value/100.0
            self.Plabel.setText('Threthold %.2f'%threthold)
            

class Address(QtGui.QWidget):
    trigger = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super(Address, self).__init__()
        self.initUI()
        
    def initUI(self):
        global address
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #左上（開始位置）の座標
        self.xstart = 1
        self.ystart = 1
        #ボタンのサイズ
        btnSize = 22
        #同じ番地内での仕切りのあつみ
        interval = 2
        #インスタンスが作られた時のaddressの値を自身のaddressに格納する
        self.address = address
        #各ボタンをクリックすると、ボタンの色が今選択中の色に変わる
        self.btn1 = QtGui.QPushButton(str(address) + '_1', self)
        self.btn2 = QtGui.QPushButton(str(address) + '_2', self)
        self.btn3 = QtGui.QPushButton(str(address) + '_3', self)
        self.btn4 = QtGui.QPushButton(str(address) + '_4', self)
        
        self.Button = [self.btn1, self.btn2, self.btn3, self.btn4]
        
        self.loc = [[self.xstart, self.ystart, btnSize, btnSize],\
                    [self.xstart + interval + btnSize, self.ystart, btnSize, btnSize],\
                    [self.xstart, self.ystart + interval + btnSize, btnSize, btnSize],\
                    [self.xstart + interval + btnSize, self.ystart + interval + btnSize, btnSize, btnSize]]
        for i in range(4):
            self.Button[i].setGeometry(self.loc[i][0], self.loc[i][1], self.loc[i][2], self.loc[i][3])
            self.Button[i].well = i+1
            self.Button[i].address = self.address
            self.Button[i].setStyleSheet\
            ('QPushButton {background-color: %s }'%color[int(Status.ix[self.address,i+1]['Status'])].name())
            self.Button[i].clicked.connect(self.singleplot)
            self.Button[i].clicked.connect(self.setStatus)
            
    def singleplot(self):
        sender = self.sender()
        self.trigger.emit(sender.address, sender.well)
        
    def setStatus(self):
        global color
        global status
        sender = self.sender()
        if mode == 1:
            (A, W) = (sender.address, sender.well)
            sender.setStyleSheet('QPushButton {background-color: %s }'%color[status].name())
            Status.ix[A,W] = status
            if status == 3:
                clock = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                with open(sample_file, 'a') as f:
                    s_writer = csv.writer(f, delimiter = ',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    s_writer.writerow([A]+[W]+[position[A-1]]+[clock])

class setStatus(QtGui.QWidget):
    def __init__(self):
        super(setStatus,self).__init__()
        self.initUI()
        
    def initUI(self):
        vbox = QtGui.QVBoxLayout(self)
        #setStatusModeにするボタン
        self.setStatusbutton = QtGui.QPushButton('setStatusMode', self)
        self.setStatusbutton.setCheckable(True)
        self.setStatusbutton.clicked[bool].connect(self.setMode)
        vbox.addWidget(self.setStatusbutton)
        #1細胞である
        self.singlecell = QtGui.QRadioButton('SingleCell', self)
        self.singlecell.toggle()
        QtCore.QObject.connect(self.singlecell, QtCore.SIGNAL('toggled(bool)'), self.selectColor)
        vbox.addWidget(self.singlecell)

        #ごみ入りである
        self.omit = QtGui.QRadioButton('Omit', self)
        QtCore.QObject.connect(self.omit, QtCore.SIGNAL('toggled(bool)'), self.selectColor)
        vbox.addWidget(self.omit)

        #バックグラウンドにすべきである
        self.background = QtGui.QRadioButton('BackGround', self)
        QtCore.QObject.connect(self.background, QtCore.SIGNAL('toggled(bool)'), self.selectColor)
        vbox.addWidget(self.background)
        
        #回収済み
        self.collected = QtGui.QRadioButton('Collected', self)
        QtCore.QObject.connect(self.collected, QtCore.SIGNAL('toggled(bool)'), self.selectColor)
        vbox.addWidget(self.collected)
        
        self.setLayout(vbox)
        self.show()
        
    def setMode(self, pressed):
        global mode
        if pressed:
            mode = 1
        else:
            mode = 0
    #ラジオボタンを押すたびに選択中の色と文字列が変わる 
    def selectColor(self):
        global status
        sender = self.sender()
        if sender.text() == 'SingleCell':
            status = 0
        elif sender.text() == 'Omit':
            status = 1
        elif sender.text() == 'BackGround':
            status = 2
        elif sender.text() == 'Collected':
            status = 3
            
def main():
    global Roi_Data_file
    global nd2_file
    global position
    global time_file
    global sample_file
    global status_file
    global address
    global Data
    global color
    global mode
    global n
    global scan
    global status
    global difference
    global timelag
    global threthold
    global Grid
    global protein
    global to_addr
    global subject
    global body
    global sigma
    global ADDRESS
    global mime
    global attach_file
    
    app = QtGui.QApplication(sys.argv)
    """
    Roi_Data_file = 'C:/Users/YTanaka/Desktop/20161007/ROI_Data.csv'
    position_file = 'Z:/RealTimeExport/20161007_Quad2_hILC2_pick3.xml'
    nd2_file = 'Z:/images/Image'
    time_file = 'C:/Users/YTanaka/Desktop/20161007/time.csv'
    sample_file = 'C:/Users/YTanaka/Desktop/20161007/sample.csv'
    status_file = 'C:/Users/YTanaka/Desktop/20161007/status.csv'
    """
    Roi_Data_file = '/Volumes/SINGLECELL/sampledata/20161007_max_test/ROI_Data.csv'
    position_file = '/Volumes/SINGLECELL/sampledata/20161007_max_test/20161007_Quad2_hILC2_pick3.xml'
    nd2_file = '/Volumes/SINGLECELL/sampledata/20160425_IL33andIL2_qPCR'
    time_file = '/Volumes/SINGLECELL/sampledata/20161007_max_test/time.csv'
    sample_file = '/Volumes/SINGLECELL/sampledata/20161007_max_test/sample.csv'
    status_file = '/Volumes/SINGLECELL/sampledata/20161007_max_test/status.csv'
    
    n = 159#変更する
    protein = 2#フィルター
    scan = 27#新しくGUIを立ち上げる時は変更
    pos_n = 996
    #件名と本文
    subject = '2号機より'
    body = '分泌が疑われるサンプル：\n'
    #宛先アドレス
    to_addr = "gomakanabun@gmail.com" 
    #送信元アドレス
    ADDRESS = 'komamehanamuguri@gmail.com'
    #添付ファイル設定(text.txtファイルを添付)
    mime={'type':'image', 'subtype':'png'}
    attach_file={'name':'plot.png', 'path':'/Volumes/SINGLECELL/sampledata/20161007_max_test/plot.png'}
 
    #メッセージの作成(添付ファイルあり)
    mode = 0
    status = 2
    difference = 1
    timelag = 0
    threthold = 1
    sigma = 50
    color = [QtGui.QColor(100, 30, 30),#赤
            QtGui.QColor(100, 100, 100),#灰色
            QtGui.QColor(255, 255, 200),#クリーム
            QtGui.QColor(200, 255, 255)]#水色
            
    position = readXML.readXML(position_file, pos_n)
    
    main_panel = QtGui.QWidget()
    main_panel.resize(10000,1000)
    
    panel = QtGui.QWidget()
    panel2 = QtGui.QWidget()
    read_widget = Run()
    status_widget = setStatus()
    graph_widget = Plot()
    para_widget = Parameter()
    pic_widget = Plot()
    merge_widget = Plot()
    tab_widget = QtGui.QTabWidget()
    well_widget = QtGui.QWidget()
    
    main_panel_layout = QtGui.QHBoxLayout()
    panel_layout = QtGui.QVBoxLayout()
    panel2_layout = QtGui.QHBoxLayout()
    tab_layout = QtGui.QHBoxLayout()
    well_layout = QtGui.QGridLayout()

    #番地番号をまず付け足していき、そのまま各番地のインスタンスを作成
    Grid = []

    for i in np.arange(1, n+1):
        address = i
        #まずは番地番号をAddressの最後尾につけたす
        Grid.append(str(i))
        #Addressの最後尾にWellのインスタンスを作成
        Grid[-1] = Address()
        Grid[-1].trigger.connect(graph_widget.singlePlot)
        Grid[-1].trigger.connect(pic_widget.picture)
        Grid[-1].trigger.connect(merge_widget.merge)

        #その番地番号に従い、グリット状にウィジェットを配置（左上から右下へ）
        well_layout.addWidget(Grid[-1], (i-1)//10, (i-1)%10)

    tab_widget.addTab(graph_widget, 'graph')
    tab_widget.addTab(pic_widget, 'picture')
    tab_widget.addTab(merge_widget, 'merge')
    tab_layout.addWidget(tab_widget)
    panel_layout.addWidget(read_widget)
    panel2_layout.addWidget(status_widget)
    panel2_layout.addWidget(para_widget)
    panel2.setLayout(panel2_layout)
    panel_layout.addWidget(panel2)
    panel_layout.addWidget(tab_widget)
    panel.setLayout(panel_layout)
    well_widget.setLayout(well_layout)
    main_panel_layout.addWidget(well_widget)
    main_panel_layout.addWidget(panel)
    main_panel.setLayout(main_panel_layout)
    main_panel.show()
    read_widget.timer.start()
    sys.exit(app.exec_())
    
if __name__=='__main__':
    main()