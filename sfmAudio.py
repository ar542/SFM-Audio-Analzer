# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Python34/Lib/site-packages/PySide/sfmAudio.ui'
#
# Created: Mon Feb 25 13:57:52 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import pyaudio,os,wave,numpy,audioop 

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
	self.chunk=float(self.wf.getframerate()/sfmApp.GetFramesPerSecond())#each chunk is roughly one frame long

    def play(self,func,controlName):
        """ Play entire file """
        data = self.wf.readframes(int(self.chunk))
	rgb=1.0
	#wave frame leagth self.wf.getnframes()/float(self.chunk)	
	
	print self.wf.getnframes()/self.chunk
	
        while data != '':
            
            #self.stream.write(data)
            
            dataarray = numpy.fromstring(data,dtype=numpy.int16)
	    volume = numpy.average(dataarray)*2
            peak=numpy.average(numpy.abs(dataarray))*2
            #bars="#"*int(50*peak/2**16)
           # print("%d %s"%((255*peak)/2**16,bars))     
            rgb=float(peak)/2.0**15
	    
	    
	    frame2=int(self.wf.tell()/self.chunk)
	    frame=((1.0/self.chunk)*self.wf.tell())*(1/24.0)
	    print frame
	    
	   # pitch = audioop.rms(dataarray, 2) 
	    #print (frame)
	    func(controlName,vs.DmeTime_t(5.0+frame),rgb)
	    #current frame self.wf.tell()/self.chunk
            
	    data = self.wf.readframes(int(self.chunk))


        self.stream.close()
        self.p.terminate()

    def FrametoDmeTime(self,frame):
	
	return vs.DmeTime_t(5.0+frame*(1.0/sfmApp.GetFramesPerSecond()))



class Audio_Dialog(object):
    
    
    
    
    
    
    def __init__(self):
        
        self.Dialog = QtGui.QDialog()
        self.setupUi(self.Dialog)
	self.animset=sfm.GetCurrentAnimationSet()
	self.ExpandToolBox()
        self.Dialog.show()
        self.Dialog.exec_()
	
        
        
        
        
    def test(self):
	# Change the operation mode to passthrough so changes chan be made temporarily
	sfm.SetOperationMode( "Pass" )	
        sfmApp.SetTimelineMode(2)
       # sound=AudioFile("C:/Program Files (x86)/Steam/steamapps/common/SourceFilmmaker/game/tf/sound/music/bonus_round_30.wav")
	
       # sound.play(self.AddKeyFrame,"verticalFOV")
       
	#print self.comboBox_animset.itemData(self.comboBox_animset.currentIndex() )
	
	
        self.Dialog.accept()
               
        
        
    def AddKeyFrame(self,controlName,time,value,low=None,high=None):
	
	#self.animset.FindControl(controlName).channel.log.AddBookmark(time,0)	
	
	self.animset.FindControl(controlName).channel.log.FindOrAddKey(time,vs.DmeTime_t(10000),value)        
        
        
        
        
    def ExpandToolBox(self):
	
	for element in self.animset.controls:
		if type(element) is vs.datamodel.CDmElement:
			self.AddControlTab(element.name)	
        
        
        
        
    def AddControlTab(self,controlName):
	tempcontrol= QtGui.QWidget()	
	
	gridLayout = QtGui.QGridLayout(tempcontrol)
	
	
	groupBox_control = QtGui.QGroupBox(tempcontrol)
	#groupBox_control.setFlat(True)
	groupBox_control.setCheckable(True)
	groupBox_control.setChecked(False)
	
	groupBox_control.setTitle("Enable")
	gridLayout_3 = QtGui.QGridLayout(groupBox_control)
	
	
	label_6 = QtGui.QLabel(groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(label_6.sizePolicy().hasHeightForWidth())
	
	label_6.setSizePolicy(sizePolicy)
	label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	label_6.setObjectName("label_6")
	gridLayout_3.addWidget(label_6, 0, 0, 1, 1)
	doubleSpinBox_minvalue = QtGui.QDoubleSpinBox(groupBox_control)
	doubleSpinBox_minvalue.setFrame(True)
	doubleSpinBox_minvalue.setAccelerated(True)
	doubleSpinBox_minvalue.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	doubleSpinBox_minvalue.setDecimals(4)
	doubleSpinBox_minvalue.setMaximum(1.0)
	doubleSpinBox_minvalue.setSingleStep(0.01)
	doubleSpinBox_minvalue.setObjectName("doubleSpinBox_minvalue")
	gridLayout_3.addWidget(doubleSpinBox_minvalue, 0, 1, 1, 1)
	label_7 = QtGui.QLabel(groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(label_7.sizePolicy().hasHeightForWidth())
	label_7.setSizePolicy(sizePolicy)
	label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	label_7.setObjectName("label_7")
	gridLayout_3.addWidget(label_7, 0, 2, 1, 1)
	doubleSpinBox_maxvalue = QtGui.QDoubleSpinBox(groupBox_control)
	doubleSpinBox_maxvalue.setWrapping(False)
	doubleSpinBox_maxvalue.setFrame(True)
	doubleSpinBox_maxvalue.setAccelerated(True)
	doubleSpinBox_maxvalue.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	doubleSpinBox_maxvalue.setDecimals(4)
	doubleSpinBox_maxvalue.setMaximum(1.0)
	doubleSpinBox_maxvalue.setSingleStep(0.01)
	doubleSpinBox_maxvalue.setProperty("value", 1.0)
	doubleSpinBox_maxvalue.setObjectName("doubleSpinBox_maxvalue")
	gridLayout_3.addWidget(doubleSpinBox_maxvalue, 0, 3, 1, 1)
	gridLayout.addWidget(groupBox_control, 0, 0, 1, 1)
	self.control_toolBox.addItem(tempcontrol, str(controlName))	
	
	
	
	
	
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(486, 345)
	self.verticalLayout = QtGui.QVBoxLayout(Dialog)
	self.verticalLayout.setObjectName("verticalLayout")
	self.gridLayout = QtGui.QGridLayout()
	self.gridLayout.setObjectName("gridLayout")

	self.fileLabel = QtGui.QLabel(Dialog)
	self.fileLabel.setObjectName("fileLabel")
	self.gridLayout.addWidget(self.fileLabel, 0, 0, 1, 1)

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
	self.scrollArea = QtGui.QScrollArea(Dialog)
	self.scrollArea.setWidgetResizable(True)
	self.scrollArea.setObjectName("scrollArea")
	self.scrollAreaWidgetContents = QtGui.QWidget()
	self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -11, 449, 178))
	self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
	self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
	self.verticalLayout_3.setObjectName("verticalLayout_3")
	self.MiscBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
	self.MiscBox.setFlat(False)
	self.MiscBox.setCheckable(False)
	self.MiscBox.setObjectName("MiscBox")
	self.verticalLayout_2 = QtGui.QVBoxLayout(self.MiscBox)
	self.verticalLayout_2.setObjectName("verticalLayout_2")
	self.control_toolBox = QtGui.QToolBox(self.MiscBox)
	self.control_toolBox.setEnabled(True)
	self.control_toolBox.setFrameShape(QtGui.QFrame.NoFrame)
	self.control_toolBox.setFrameShadow(QtGui.QFrame.Plain)
	self.control_toolBox.setLineWidth(2)
	self.control_toolBox.setMidLineWidth(1)
	self.control_toolBox.setObjectName("control_toolBox")
	self.page_bright = QtGui.QWidget()
	self.page_bright.setGeometry(QtCore.QRect(0, 0, 411, 69))
	self.page_bright.setObjectName("page_bright")
	self.horizontalLayout = QtGui.QHBoxLayout(self.page_bright)
	self.horizontalLayout.setObjectName("horizontalLayout")
	self.label_2 = QtGui.QLabel(self.page_bright)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
	self.label_2.setSizePolicy(sizePolicy)
	self.label_2.setObjectName("label_2")
	self.horizontalLayout.addWidget(self.label_2)
	self.spinBox = QtGui.QSpinBox(self.page_bright)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
	self.spinBox.setSizePolicy(sizePolicy)
	self.spinBox.setAccelerated(True)
	self.spinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.spinBox.setMaximum(999999999)
	self.spinBox.setObjectName("spinBox")
	self.horizontalLayout.addWidget(self.spinBox)
	self.line = QtGui.QFrame(self.page_bright)
	self.line.setFrameShape(QtGui.QFrame.VLine)
	self.line.setFrameShadow(QtGui.QFrame.Sunken)
	self.line.setObjectName("line")
	self.horizontalLayout.addWidget(self.line)
	self.checkBox = QtGui.QCheckBox(self.page_bright)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
	self.checkBox.setSizePolicy(sizePolicy)
	self.checkBox.setTristate(False)
	self.checkBox.setObjectName("checkBox")
	self.horizontalLayout.addWidget(self.checkBox)
	self.control_toolBox.addItem(self.page_bright, "")
	#

	self.verticalLayout_2.addWidget(self.control_toolBox)
	self.verticalLayout_3.addWidget(self.MiscBox)
	self.scrollArea.setWidget(self.scrollAreaWidgetContents)
	self.verticalLayout.addWidget(self.scrollArea)
	self.buttonBox = QtGui.QDialogButtonBox(Dialog)
	self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
	self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
	self.buttonBox.setObjectName("buttonBox")
	self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.control_toolBox.setCurrentIndex(0)
        self.control_toolBox.layout().setSpacing(8)
	
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.test)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


















    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

        self.fileLabel.setText(QtGui.QApplication.translate("Dialog", "wave file", None, QtGui.QApplication.UnicodeUTF8))
        self.getfileButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.MiscBox.setTitle(QtGui.QApplication.translate("Dialog", "light control options", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Start Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Dialog", "Add Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
        self.control_toolBox.setItemText(self.control_toolBox.indexOf(self.page_bright), QtGui.QApplication.translate("Dialog", "Misc", None, QtGui.QApplication.UnicodeUTF8))
        
        
       # self.control_toolBox.setItemText(self.control_toolBox.indexOf(self.page_control_setting), QtGui.QApplication.translate("Dialog", "control name", None, QtGui.QApplication.UnicodeUTF8))


audioscript=Audio_Dialog()
