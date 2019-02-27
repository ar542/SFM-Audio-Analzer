# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:/Python34/Lib/site-packages/PySide/sfmAudio.ui'
#
# Created: Mon Feb 25 13:57:52 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import pyaudio,os,wave,numpy,audioop 

class AudioFileAnalyze(object):
    

    def __init__(self, wavefile,overwriteChunk=None):
        """ Init audio stream """ 

        self.wf = wave.open(wavefile, 'rb')

        #acts like a buffer
        if overwriteChunk:
            self.chunk=overwriteChunk
        else:
            self.chunk=float(self.wf.getframerate()/sfmApp.GetFramesPerSecond())#each chunk is roughly one frame long

        print(
        """
Audio File Info:
 File: %s
 channels: %d
 Rate: %dHz
 BufferSize: %.02f
 Duration: %.02fsec

        
        
        """%(wavefile,self.wf.getnchannels(),self.wf.getframerate(),self.chunk,float(self.wf.getnframes()/self.wf.getframerate() )))

        self.progressbarWindow = QtGui.QWidget()
        self.progressbarWindow.resize(600, 30)
        self.progressbarWindow.setWindowTitle('Calculating...')
        self.progressbarWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.progressbar = QtGui.QProgressBar(self.progressbarWindow)
        self.progressbar.resize(600,30) 



    


        #return sfm frame time of a single buffer
    def getBufferFrameTime(self,numofchunks=1):


        return vs.DmeTime_t(5.00000+(1.0/self.wf.getframerate())*(self.chunk*numofchunks))

    def analyze(self,dataValue,EndFrame=None):




     #   nframes=(self.wf.getnframes()/self.chunk) if  EndFrame==0 else numpy.ceil(float((self.wf.getframerate()/sfmApp.GetFramesPerSecond())*EndFrame)/self.chunk)


        

        self.progressbar.setMinimum(0)
       # self.progressbar.setMaximum(nframes*2)
        self.progressbar.setValue(0)

        self.progressbarWindow.show()



        data = self.wf.readframes(int(self.chunk))

        while data != '':
            self.progressbar.setValue(self.progressbar.value()+1)
            dataarray = numpy.fromstring(data,dtype=numpy.int16)
            dataValue.append(float(numpy.average(numpy.abs(dataarray))*2)/2.0**15)   
            if EndFrame and self.wf.tell()>=(float(self.wf.getframerate()/sfmApp.GetFramesPerSecond())*EndFrame):
                break             
            data = self.wf.readframes(int(self.chunk))


        
        self.wf.close()


        
    def play(self):
        """ Play entire file """
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

        data = self.wf.readframes(int(self.chunk))        
        while data != '':            
            self.stream.write(data)            
            data = self.wf.readframes(int(self.chunk))

        self.stream.close()
        self.p.terminate()





class Audio_Dialog(object):
    
    
    ##toDo loop pages add end frame
    
    
    
    def __init__(self):
        
        self.Dialog = QtGui.QDialog()
        self.setupUi(self.Dialog)
        self.animset = sfm.GetCurrentAnimationSet()
        self.ExpandToolBox()
        self.audiofilepath = "C:/Program Files (x86)/Steam/steamapps/common/SourceFilmmaker/game/tf/sound/music/bonus_round_30.wav"
        self.audioAnalyze = None

        self.Dialog.closeEvent = self.closeEvent
        self.Dialog.show()
        self.Dialog.exec_()
        

    def closeEvent(self, event):
        del self.audioAnalyze
        event.accept()               
        
        
    def ErrorBox(self,e):
        #error box

        msgBox = QtGui.QMessageBox(QtGui.QMessageBox.Critical,
                "ERROR", str(e),
                QtGui.QMessageBox.NoButton, self.Dialog)

        font = QtGui.QFont()
        font.setPointSize(10)
        msgBox.setFont(font)
        msgBox.addButton("&Continue", QtGui.QMessageBox.RejectRole)
        if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:pass
        
        
    def getfile(self):
        
        self.audiofilepath, foo = QtGui.QFileDialog.getOpenFileName(None,
                    "Load wav file","", "(*.wav)")    
        self.filePath_lineedit.setText(self.audiofilepath)        
        
    def test(self):
        
        #if not self.audiofilepath:
        #    self.ErrorBox("No Wave file picked!")
        #    return
        # Change the operation mode to passthrough so changes chan be made
        # temporarily
        sfm.SetOperationMode("Pass")	
        sfmApp.SetTimelineMode(2)     
        
        controldict={}
        
        for index in range(1,self.control_toolBox.count ()):

            if self.control_toolBox.widget(index).findChild(QtGui.QGroupBox).isChecked():
                
                minvalue= self.control_toolBox.widget(index).findChild(QtGui.QDoubleSpinBox,"doubleSpinBox_minvalue").value()
                maxvalue= self.control_toolBox.widget(index).findChild(QtGui.QDoubleSpinBox,"doubleSpinBox_maxvalue").value()
                controldict[self.control_toolBox.itemText(index)]=[minvalue,maxvalue]

      

        self.Dialog.hide()
        self.audioAnalyze = AudioFileAnalyze(self.audiofilepath,self.spinBox_buffer.value() if self.checkBox_overrideBuffer.isChecked() else None)

        numframes=(self.audioAnalyze.wf.getnframes()/self.audioAnalyze.chunk) if  self.endFrameSpinBox.value()-self.startFrameSpinBox.value()==0 else numpy.ceil(float((self.audioAnalyze.wf.getframerate()/sfmApp.GetFramesPerSecond())*self.endFrameSpinBox.value()-self.startFrameSpinBox.value())/self.audioAnalyze.chunk)
        

        self.audioAnalyze.progressbar.setMaximum(numframes*2*len(controldict.keys()))


        dataValue = []
        self.audioAnalyze.analyze(dataValue,self.endFrameSpinBox.value()-self.startFrameSpinBox.value())#fill up the array with data points
       


        for control in controldict.keys():

            print type(control)
            for index in range(len(dataValue)):

                self.AddKeyFrame(str(control),
                                 vs.DmeTime_t((self.startFrameSpinBox.value() * (1.0 / sfmApp.GetFramesPerSecond()))) + self.audioAnalyze.getBufferFrameTime(numofchunks=index + 1),
                                 dataValue[index],controldict[control][0],controldict[control][1])
                self.audioAnalyze.progressbar.setValue(self.audioAnalyze.progressbar.value() + 1)














        
       # sound=AudioFile("C:/Program Files
       # (x86)/Steam/steamapps/common/SourceFilmmaker/game/tf/sound/music/bonus_round_30.wav")
        
      #  sound.play(self.AddKeyFrame,"verticalFOV")
       
        #print
        #self.comboBox_animset.itemData(self.comboBox_animset.currentIndex() )
     #   print
     #   self.control_toolBox.widget(2).findChild(QtGui.QGroupBox).isChecked()
        
   #     print self.control_toolBox.itemText(2)
        #cleanup
        del self.audioAnalyze
        self.Dialog.accept()

        
        
    def AddKeyFrame(self,controlName,time,value,low=0.0,high=1.0):
        if self.addBookmarkCheckBox.isChecked():
            self.animset.FindControl(controlName).channel.log.AddBookmark(time,0)	
        
        self.animset.FindControl(controlName).channel.log.FindOrAddKey(time,vs.DmeTime_t(10000),numpy.clip(value,low,high))        
        
        
 
       #adds a template page to toolbox    
    def AddControlTab(self,controlName):
        tempcontrol = QtGui.QWidget()	
        
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
        label_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        label_6.setText("Min")
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
        label_7.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        label_7.setText("Max")
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
        
    def ExpandToolBox(self):
        
        for element in self.animset.controls:
            if type(element) is vs.datamodel.CDmElement:
                self.AddControlTab(element.name)     
        

    def setupUi(self, Dialog):

        Dialog.setObjectName("Dialog")
        Dialog.resize(660, 316)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(660, 0))
        Dialog.setMaximumSize(QtCore.QSize(660, 16777215))
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
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 642, 241))
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
        self.page_bright.setGeometry(QtCore.QRect(0, 0, 604, 132))
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
        self.startFrameSpinBox = QtGui.QSpinBox(self.page_bright)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startFrameSpinBox.sizePolicy().hasHeightForWidth())
        self.startFrameSpinBox.setSizePolicy(sizePolicy)
        self.startFrameSpinBox.setAccelerated(True)
        self.startFrameSpinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
        self.startFrameSpinBox.setMaximum(999999999)
        self.startFrameSpinBox.setObjectName("startFrameSpinBox")
        self.horizontalLayout.addWidget(self.startFrameSpinBox)
        self.label = QtGui.QLabel(self.page_bright)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.endFrameSpinBox = QtGui.QSpinBox(self.page_bright)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endFrameSpinBox.sizePolicy().hasHeightForWidth())
        self.endFrameSpinBox.setSizePolicy(sizePolicy)
        self.endFrameSpinBox.setMaximum(99999999)
        self.endFrameSpinBox.setObjectName("endFrameSpinBox")
        self.horizontalLayout.addWidget(self.endFrameSpinBox)
        self.line = QtGui.QFrame(self.page_bright)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.addBookmarkCheckBox = QtGui.QCheckBox(self.page_bright)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addBookmarkCheckBox.sizePolicy().hasHeightForWidth())
        self.addBookmarkCheckBox.setSizePolicy(sizePolicy)
        self.addBookmarkCheckBox.setTristate(False)
        self.addBookmarkCheckBox.setObjectName("addBookmarkCheckBox")
        self.horizontalLayout.addWidget(self.addBookmarkCheckBox)
        self.line_2 = QtGui.QFrame(self.page_bright)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        self.checkBox_overrideBuffer = QtGui.QCheckBox(self.page_bright)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox_overrideBuffer.sizePolicy().hasHeightForWidth())
        self.checkBox_overrideBuffer.setSizePolicy(sizePolicy)
        self.checkBox_overrideBuffer.setObjectName("checkBox_overrideBuffer")
        self.horizontalLayout.addWidget(self.checkBox_overrideBuffer)
        self.spinBox_buffer = QtGui.QSpinBox(self.page_bright)
        self.spinBox_buffer.setEnabled(False)
        self.spinBox_buffer.setMinimum(32)
        self.spinBox_buffer.setMaximum(32768)
        self.spinBox_buffer.setSingleStep(1)
        self.spinBox_buffer.setProperty("value", 2048)
        self.spinBox_buffer.setObjectName("spinBox_buffer")
        self.horizontalLayout.addWidget(self.spinBox_buffer)
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

        QtCore.QObject.connect(self.checkBox_overrideBuffer, QtCore.SIGNAL("toggled(bool)"), self.spinBox_buffer.setEnabled)
        QtCore.QObject.connect(self.getfileButton, QtCore.SIGNAL("clicked()"), self.getfile)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.test)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


















    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

        self.fileLabel.setText(QtGui.QApplication.translate("Dialog", "wave file", None, QtGui.QApplication.UnicodeUTF8))
        self.getfileButton.setText(QtGui.QApplication.translate("Dialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.MiscBox.setTitle(QtGui.QApplication.translate("Dialog", "light control options", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Start Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.addBookmarkCheckBox.setText(QtGui.QApplication.translate("Dialog", "Add Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
        self.control_toolBox.setItemText(self.control_toolBox.indexOf(self.page_bright), QtGui.QApplication.translate("Dialog", "Misc", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "End Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_overrideBuffer.setText(QtGui.QApplication.translate("Dialog", "override BufferSize", None, QtGui.QApplication.UnicodeUTF8))
    



audioscript = Audio_Dialog()