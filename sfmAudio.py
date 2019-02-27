# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Python34/Lib/site-packages/PySide/sfmAudio.ui'
#
# Created: Sun Feb 24 13:34:57 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import pyaudio,os,wave,numpy 



class AudioFile:
    

    def __init__(self, wavefile):
        """ Init audio stream """ 
        self.wf = wave.open(wavefile, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )
	self.chunk=int(self.wf.getframerate()/sfmApp.GetFramesPerSecond())#each chunk is roughly one frame long

    def play(self,func,animset,controlName):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
	rgb=255
	#wave frame leagth self.wf.getnframes()/float(self.chunk)
        while data != '':
            
            #self.stream.write(data)
            
            dataarray = numpy.fromstring(data,dtype=numpy.int16)
            peak=numpy.average(numpy.abs(dataarray))*2
            #bars="#"*int(50*peak/2**16)
           # print("%d %s"%((255*peak)/2**16,bars))            
            rgb=float(1*peak)/2**15
	    frame=int(self.wf.tell()/self.chunk)
	    print (self.FrametoDmeTime(frame))
	    func(animset,controlName,self.FrametoDmeTime(frame),rgb)
	    #current frame self.wf.tell()/self.chunk
            
	    data = self.wf.readframes(self.chunk)


        self.stream.close()
        self.p.terminate()

    def FrametoDmeTime(self,frame):
	
	return vs.DmeTime_t(5.0+frame*(1.0/sfmApp.GetFramesPerSecond()))






class Audio_Dialog(object):
    def __init__(self):
        
        self.Dialog = QtGui.QDialog()
        self.setupUi(self.Dialog)
        #self.Dialog.show()
        self.Dialog.exec_()        
	
	
        
        
        
    
    def test(self):
        sfmApp.SetTimelineMode(2)
        sound=AudioFile("C:/Program Files (x86)/Steam/steamapps/common/SourceFilmmaker/game/tf/sound/music/bonus_round_30.wav")
	
        sound.play(self.AddKeyFrame,self.comboBox_animset.itemData(self.comboBox_animset.currentIndex() ),"horizontalFOV")
       
	#print self.comboBox_animset.itemData(self.comboBox_animset.currentIndex() )
        self.Dialog.accept()
       


    def FindAllLightsinShot(self):
	shot = sfmClipEditor.GetSelectedShots()[0]
	

	for animationSet in shot.animationSets:
	    if animationSet.HasAttribute("light"):
		self.comboBox_animset.addItem(animationSet.GetName(),animationSet)
		
       
    def AddKeyFrame(self,animset,controlName,time,value):
	
	#animset.FindControl(controlName).channel.log.AddBookmark(time,0)	
	animset.FindControl(controlName).channel.log.GetLayer(0).FindOrAddKey(time,vs.DmeTime_t(10000),value)
    
    
    def setupUi(self, Dialog):
	
	
        Dialog.setObjectName("Dialog")
        Dialog.resize(486, 345)
        
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.fileLabel = QtGui.QLabel(Dialog)
        self.fileLabel.setObjectName("fileLabel")
        self.gridLayout.addWidget(self.fileLabel, 0, 0, 1, 1)
        self.comboBox_animset = QtGui.QComboBox(Dialog)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBox_animset.setFont(font)
        self.comboBox_animset.setObjectName("comboBox_animset")
        self.gridLayout.addWidget(self.comboBox_animset, 1, 1, 1, 1)
        self.getfileButton = QtGui.QToolButton(Dialog)
        self.getfileButton.setObjectName("getfileButton")
        self.gridLayout.addWidget(self.getfileButton, 0, 2, 1, 1)
        self.filePath_lineedit = QtGui.QLineEdit(Dialog)
        self.filePath_lineedit.setEnabled(False)
        self.filePath_lineedit.setFrame(True)
        self.filePath_lineedit.setDragEnabled(True)
        self.filePath_lineedit.setReadOnly(True)
        self.filePath_lineedit.setObjectName("filePath_lineedit")
        self.gridLayout.addWidget(self.filePath_lineedit, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.MiscBox = QtGui.QGroupBox(Dialog)
        self.MiscBox.setObjectName("MiscBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.MiscBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.toolBox = QtGui.QToolBox(self.MiscBox)
        self.toolBox.setFrameShape(QtGui.QFrame.NoFrame)
        self.toolBox.setFrameShadow(QtGui.QFrame.Plain)
        self.toolBox.setLineWidth(2)
        self.toolBox.setMidLineWidth(1)
        self.toolBox.setObjectName("toolBox")
        self.page_bright = QtGui.QWidget()
        self.page_bright.setGeometry(QtCore.QRect(0, 0, 448, 125))
        self.page_bright.setObjectName("page_bright")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.page_bright)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(self.page_bright)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.page_bright)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.label_3 = QtGui.QLabel(self.page_bright)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.doubleSpinBox_2 = QtGui.QDoubleSpinBox(self.page_bright)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.horizontalLayout.addWidget(self.doubleSpinBox_2)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.toolBox.addItem(self.page_bright, "")
        self.page_zoom = QtGui.QWidget()
        self.page_zoom.setGeometry(QtCore.QRect(0, 0, 448, 125))
        self.page_zoom.setObjectName("page_zoom")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.page_zoom)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtGui.QLabel(self.page_zoom)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.doubleSpinBox_3 = QtGui.QDoubleSpinBox(self.page_zoom)
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_3)
        self.label_5 = QtGui.QLabel(self.page_zoom)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.doubleSpinBox_4 = QtGui.QDoubleSpinBox(self.page_zoom)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.horizontalLayout_2.addWidget(self.doubleSpinBox_4)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.toolBox.addItem(self.page_zoom, "")
        self.page_color = QtGui.QWidget()
        self.page_color.setObjectName("page_color")
        self.toolBox.addItem(self.page_color, "")
        self.verticalLayout_2.addWidget(self.toolBox)
        self.verticalLayout.addWidget(self.MiscBox)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.toolBox.setCurrentIndex(0)
	
	
	self.FindAllLightsinShot()
	
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),  self.test)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "light animset", None, QtGui.QApplication.UnicodeUTF8))
        self.fileLabel.setText(QtGui.QApplication.translate("Dialog", "wave file", None, QtGui.QApplication.UnicodeUTF8))
        self.getfileButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.MiscBox.setTitle(QtGui.QApplication.translate("Dialog", "light options", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialog", "max", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_bright), QtGui.QApplication.translate("Dialog", "brightness", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialog", "min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialog", "max", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_zoom), QtGui.QApplication.translate("Dialog", "zoom", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_color), QtGui.QApplication.translate("Dialog", "color", None, QtGui.QApplication.UnicodeUTF8))



    


audioscript=Audio_Dialog()




