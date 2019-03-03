# -*- coding: utf-8 -*-

#Audio Peak Analyzer v1.0
#BY http://steamcommunity.com/id/OMGTheresABearInMyOatmeal/
#feel free to modify the script for your own use
# Created: Mon Feb 25 13:57:52 2019


from PySide import QtCore, QtGui
import wave,numpy,re,sfm,sfmClipEditor,sfmApp,vs ,os,array

class AudioFileAnalyze(object):
    

    def __init__(self, wavefile,overwriteChunk=None):
        """ Init audio stream """ 

        self.wf = wave.open(wavefile, 'rb')

        #acts like a buffer
        if overwriteChunk:
            self.chunk=overwriteChunk
        else:
            self.chunk=int(self.wf.getframerate()/sfmApp.GetFramesPerSecond())#each chunk is roughly one frame long

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
        
        fmt_size = "h" if self.wf.getsampwidth() == 2 else "i"
        
        self.DatawaveArray = array.array(fmt_size)
        self.DatawaveArray.fromfile(open(wavefile, 'rb'), os.path.getsize(wavefile)//self.DatawaveArray.itemsize)
        self.DatawaveArray = self.DatawaveArray[44//self.wf.getsampwidth():]
        self.DatawaveArray=list(self.divide_chunks(self.DatawaveArray, int(self.chunk)))




    def divide_chunks(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


        #return sfm frame time of a single buffer
    def getBufferFrameTime(self,numofchunks=1):


        return vs.DmeTime_t(5.00000+(1.0/self.wf.getframerate())*(self.chunk*numofchunks))



    def analyze(self,dataValue,duration):
        

        self.progressbar.setMinimum(0)       
        self.progressbar.setValue(0)
        self.progressbarWindow.show()


        #reads a single chunk
        data = self.wf.readframes(int(self.chunk))
        swidth = self.wf.getsampwidth()
        RATE = self.wf.getframerate()
        # use a Blackman window
       # window = numpy.blackman(self.chunk)
        





         
        index=0
        datachunk=self.DatawaveArray[index]
        print len(data), self.chunk
        #loops though entire wav file
        while len(datachunk) == self.chunk:
            
            self.progressbar.setValue(self.progressbar.value()+1)
            
            #temp array holds the data points from the chunk
           # dataarray = numpy.array(wave.struct.unpack("%dh"%(len(data)/swidth),\
                                       #  data))*window

           
            #after averaging the array to a single value appends it to the out array
           # datachunk=numpy.array(datachunk)
          #  datachunk=datachunk[datachunk>=0]
            dataValue.append(float(numpy.max((datachunk)))/2.0**15)
            
            # Take the fft and square each value
            fftData=abs(numpy.fft.rfft(datachunk))**2
            # find the maximum
            which = fftData[1:].argmax() + 1
            
            # use quadratic interpolation around the max
            if which != len(fftData)-1:
                y0,y1,y2 = numpy.log(fftData[which-1:which+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                 #find the frequency and output it
                thefreq = (which+x1)*RATE/self.chunk
              #  print "The freq is %f Hz." %(thefreq)
            else:
                thefreq = which*RATE/self.chunk






            
            #checks if we hit the endframe
         #   if self.wf.tell() >= (float(RATE/sfmApp.GetFramesPerSecond())*duration):
            if index >= (float(RATE/sfmApp.GetFramesPerSecond())*duration)//self.chunk:
                break    
            
           # data = self.wf.readframes(int(self.chunk))
            index+=1
            datachunk=self.DatawaveArray[index]
        
        self.wf.close()


        #not needed for this script but incase someone wants to use it,pyaudio needs to be added to sfm first
    #def play(self):
        #""" Play entire file """
        #import pyaudio
        
        #self.p = pyaudio.PyAudio()
        #self.stream = self.p.open(
            #format = self.p.get_format_from_width(self.wf.getsampwidth()),
            #channels = self.wf.getnchannels(),
            #rate = self.wf.getframerate(),
            #output = True
        #)

        #data = self.wf.readframes(int(self.chunk))        
        #while data != '':            
            #self.stream.write(data)            
            #data = self.wf.readframes(int(self.chunk))

        #self.stream.close()
        #self.p.terminate()





class Audio_Dialog(object):
    
    
   
    
    
    
    def __init__(self):
        
        self.Dialog = QtGui.QDialog()
        self.setupUi(self.Dialog)
        self.animset = sfm.GetCurrentAnimationSet()
        self.ExpandToolBox()
        self.audiofilepath = None
        self.audioAnalyze = None
	
	
	if  type(sfmClipEditor.GetSelectedClips()[0]) is not vs.movieobjects.CDmeSoundClip:
	    self.ErrorBox("One Wav file needs to be selected!")
	    return	
	ClipName= sfmClipEditor.GetSelectedClips()[0].GetName().replace('\\', '/')
	
	if "wav" not in ClipName[-4:]:
	    self.ErrorBox("Sound file Needs to be .wav")
	    return	    
	
	#we need to search though sfm file cache because CDmeSoundClip does not hold full file path
	with open("build_file_cache.txt", 'r') as inF:
	    for line in inF:
		if  ClipName in line:
		    
		    self.audiofilepath= re.search(r'game.*?\.wav',line).group()[5:]
		    break          








        self.Dialog.closeEvent = self.closeEvent
        #allows user to somewhat interact with sfm while script is active. any changes to scene will happen once script is closed
        self.Dialog.show()
        #important!!, any gui that needs to alter animset values for animation needs to be .exec_() else sfm will crash
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
        msgBox.addButton("&Retry", QtGui.QMessageBox.RejectRole)
        if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:pass
        
        
      
        
    def startAnalyze(self):
        
        if not self.audiofilepath:
            self.ErrorBox("No Wave file picked!")
            return
        
           
        
        #get start and end time
        endFramevalue=sfmClipEditor.GetSelectedClips()[0].GetEndTime().ToFractionalFrame(vs.DmeFramerate_t(sfmApp.GetFramesPerSecond()))
        
        startFramevalue=sfmClipEditor.GetSelectedClips()[0].GetStartTime().ToFractionalFrame(vs.DmeFramerate_t(sfmApp.GetFramesPerSecond()))
	
	
	
	
        # Change the operation mode to passthrough so changes chan be made
        # temporarily
        sfm.SetOperationMode("Pass")	
        sfmApp.SetTimelineMode(2)     
        
        
        ###loops though all the pages and adds them to the dict if they are enabled
        ##key=control name: value=[min value,max value]
        controldict={}
        
        for index in range(self.control_toolBox.count ()):

            if self.control_toolBox.widget(index).IsEnabled():
                
                minvalue,maxvalue= self.control_toolBox.widget(index).GetValueRange()
               
                controldict[self.control_toolBox.itemText(index)]=[minvalue,maxvalue]

        ####
        
        if  not controldict:
            self.ErrorBox("No Controls were Enabled!")
            return


        self.Dialog.hide()
        
        #inits audio class
        self.audioAnalyze = AudioFileAnalyze(self.audiofilepath,self.spinBox_buffer.value() if self.checkBox_overrideBuffer.isChecked() else None)
        


        #used to calulate the number of chunks ,for progressbar
	
        numframes=(numpy.ceil(float((self.audioAnalyze.wf.getframerate()/sfmApp.GetFramesPerSecond())*(endFramevalue-startFramevalue))/self.audioAnalyze.chunk))
        
        
        #set max for progressbar
        self.audioAnalyze.progressbar.setMaximum(numframes*2*len(controldict.keys()))


        #fill up array with the data
        dataValue = []
        self.audioAnalyze.analyze(dataValue,endFramevalue-startFramevalue)#fill up the array with data points
       

        #loop though the dict 
        for control in controldict.keys():

            beforetime=vs.DmeTime_t(5.0+((startFramevalue-1) * (1.0 / sfmApp.GetFramesPerSecond())))
            val=self.animset.FindControl(str(control)).channel.log.GetValue(beforetime)
            self.AddKeyFrame(str(control),beforetime,
                                 self.animset.FindControl(str(control)).channel.log.GetValue(beforetime))
            
            #loop though data array
            for index in range(len(dataValue)):
                
                self.AddKeyFrame(str(control),
                                 vs.DmeTime_t((startFramevalue * (1.0 / sfmApp.GetFramesPerSecond()))) + self.audioAnalyze.getBufferFrameTime(numofchunks=index + 1),
                                 dataValue[index],controldict[control][0],controldict[control][1])
                
                self.audioAnalyze.progressbar.setValue(self.audioAnalyze.progressbar.value() + 1)

            
            
            self.AddKeyFrame(str(control),vs.DmeTime_t(5.0+((endFramevalue+1) * (1.0 / sfmApp.GetFramesPerSecond()))),val)



        #cleanup
        del self.audioAnalyze
        self.Dialog.accept()

        
        #adds key value that can be clamped
        #controlName:str
        #time:vs.DmeTime_t
        #value:float
    def AddKeyFrame(self,controlName,time,value,low=0.0,high=1.0):


        
        if self.addBookmarkCheckBox.isChecked():
            if self.animset.FindControl(controlName).HasAttribute("rightvaluechannel"):
                self.animset.FindControl(controlName).rightvaluechannel.log.AddBookmark(time,0)
                self.animset.FindControl(controlName).leftvaluechannel.log.AddBookmark(time,0)
            else:
                self.animset.FindControl(controlName).channel.log.AddBookmark(time,0)	

        if self.animset.FindControl(controlName).HasAttribute("rightvaluechannel"):
            self.animset.FindControl(controlName).rightvaluechannel.log.FindOrAddKey(time,vs.DmeTime_t(10000),numpy.clip(value,low,high))
            self.animset.FindControl(controlName).leftvaluechannel.log.FindOrAddKey(time,vs.DmeTime_t(10000),numpy.clip(value,low,high)) 
        else:
            self.animset.FindControl(controlName).channel.log.FindOrAddKey(time,vs.DmeTime_t(1.0),numpy.clip(value,low,high))        
        
        
 
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
        
        
        #adds a control page for each control slider in the animset
    def ExpandToolBox(self):
        
        for element in self.animset.controls:
            if type(element) is vs.datamodel.CDmElement:
		self.control_toolBox.addItem(TemplateControlPageWidget(),str(element.name))
               # self.AddControlTab(element.name)     
        

    def setupUi(self, Dialog):
	Dialog.setObjectName("Dialog")
	Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
	Dialog.resize(660, 500)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
	Dialog.setSizePolicy(sizePolicy)
	Dialog.setMinimumSize(QtCore.QSize(660, 0))
	Dialog.setMaximumSize(QtCore.QSize(660, 16777215))
	font = QtGui.QFont()
	font.setPointSize(10)
	Dialog.setFont(font)
	Dialog.setFocusPolicy(QtCore.Qt.TabFocus)
	Dialog.setSizeGripEnabled(True)
	Dialog.setModal(True)
	self.verticalLayout = QtGui.QVBoxLayout(Dialog)
	self.verticalLayout.setObjectName("verticalLayout")
	self.MiscBox = QtGui.QGroupBox(Dialog)
	self.MiscBox.setFlat(False)
	self.MiscBox.setCheckable(False)
	self.MiscBox.setObjectName("MiscBox")
	self.verticalLayout_2 = QtGui.QVBoxLayout(self.MiscBox)
	self.verticalLayout_2.setObjectName("verticalLayout_2")
	self.scrollArea = QtGui.QScrollArea(self.MiscBox)
	self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
	self.scrollArea.setWidgetResizable(True)
	self.scrollArea.setObjectName("scrollArea")
	self.scrollAreaWidgetContents = QtGui.QWidget()
	self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 622, 164))
	self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
	self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
	self.verticalLayout_3.setObjectName("verticalLayout_3")
	self.control_toolBox = QtGui.QToolBox(self.scrollAreaWidgetContents)
	self.control_toolBox.setEnabled(True)
	self.control_toolBox.setFrameShape(QtGui.QFrame.NoFrame)
	self.control_toolBox.setFrameShadow(QtGui.QFrame.Plain)
	self.control_toolBox.setLineWidth(2)
	self.control_toolBox.setMidLineWidth(1)
	self.control_toolBox.setObjectName("control_toolBox")
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
	self.control_toolBox.setSizePolicy(sizePolicy)
	
	#self.control_toolBox.addItem(TemplateControlPageWidget(), "test")
	
	###########
	self.verticalLayout_3.addWidget(self.control_toolBox)
	self.scrollArea.setWidget(self.scrollAreaWidgetContents)
	self.verticalLayout_2.addWidget(self.scrollArea)
	self.verticalLayout.addWidget(self.MiscBox)
	self.groupBox = QtGui.QGroupBox(Dialog)
	self.groupBox.setObjectName("groupBox")
	self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox)
	self.verticalLayout_4.setObjectName("verticalLayout_4")
	self.horizontalLayout_3 = QtGui.QHBoxLayout()
	self.horizontalLayout_3.setObjectName("horizontalLayout_3")
	self.addBookmarkCheckBox = QtGui.QCheckBox(self.groupBox)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.addBookmarkCheckBox.sizePolicy().hasHeightForWidth())
	self.addBookmarkCheckBox.setSizePolicy(sizePolicy)
	self.addBookmarkCheckBox.setToolTip("")
	self.addBookmarkCheckBox.setWhatsThis("")
	self.addBookmarkCheckBox.setTristate(False)
	self.addBookmarkCheckBox.setObjectName("addBookmarkCheckBox")
	self.horizontalLayout_3.addWidget(self.addBookmarkCheckBox)
	self.line = QtGui.QFrame(self.groupBox)
	self.line.setFrameShape(QtGui.QFrame.VLine)
	self.line.setFrameShadow(QtGui.QFrame.Sunken)
	self.line.setObjectName("line")
	self.horizontalLayout_3.addWidget(self.line)
	self.checkBox_overrideBuffer = QtGui.QCheckBox(self.groupBox)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.checkBox_overrideBuffer.sizePolicy().hasHeightForWidth())
	self.checkBox_overrideBuffer.setSizePolicy(sizePolicy)
	self.checkBox_overrideBuffer.setObjectName("checkBox_overrideBuffer")
	self.horizontalLayout_3.addWidget(self.checkBox_overrideBuffer)
	self.spinBox_buffer = QtGui.QSpinBox(self.groupBox)
	self.spinBox_buffer.setEnabled(False)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.spinBox_buffer.sizePolicy().hasHeightForWidth())
	self.spinBox_buffer.setSizePolicy(sizePolicy)
	self.spinBox_buffer.setAccelerated(True)
	self.spinBox_buffer.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.spinBox_buffer.setMinimum(32)
	self.spinBox_buffer.setMaximum(65536)
	self.spinBox_buffer.setSingleStep(1)
	self.spinBox_buffer.setObjectName("spinBox_buffer")
	self.horizontalLayout_3.addWidget(self.spinBox_buffer)
	spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
	self.horizontalLayout_3.addItem(spacerItem)
	self.verticalLayout_4.addLayout(self.horizontalLayout_3)
	self.verticalLayout.addWidget(self.groupBox)
	self.buttonBox = QtGui.QDialogButtonBox(Dialog)
	self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
	self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
	self.buttonBox.setObjectName("buttonBox")
	self.verticalLayout.addWidget(self.buttonBox)
	
      
        self.retranslateUi(Dialog)
        self.control_toolBox.setCurrentIndex(0)
        self.control_toolBox.layout().setSpacing(8)

        QtCore.QObject.connect(self.checkBox_overrideBuffer, QtCore.SIGNAL("toggled(bool)"), self.spinBox_buffer.setEnabled)
       
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.startAnalyze)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)


















    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Audio Peak Analyzer v1.1", None, QtGui.QApplication.UnicodeUTF8))

	self.MiscBox.setTitle(QtGui.QApplication.translate("Dialog", "light control options", None, QtGui.QApplication.UnicodeUTF8))

	self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Misc options", None, QtGui.QApplication.UnicodeUTF8))
	self.addBookmarkCheckBox.setText(QtGui.QApplication.translate("Dialog", "Add Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
	self.checkBox_overrideBuffer.setText(QtGui.QApplication.translate("Dialog", "override BufferSize", None, QtGui.QApplication.UnicodeUTF8))
	
    
class TemplateControlPageWidget(QtGui.QWidget):
    
    
    def __init__(self):
	super(TemplateControlPageWidget, self).__init__()
	self.Setupwidget()
    
    def IsEnabled(self):
	return self.groupBox_control.isChecked()
    
    
    def IsFreqEnable(self):
	return self.freq_checkBox.isChecked()
    
    def GetFreqRange(self):
	return self.MinFreq_doubleSpinBox.value(), self.MaxFreq_doubleSpinBox.value()    
    
    def GetValueRange(self):
	return self.doubleSpinBox_minvalue.value(), self.doubleSpinBox_maxvalue.value()
    
    def ValadateRange(self,this,minspinn,maxspin):
	if this==minspinn:
	    if minspinn.value()>maxspin.value():
		minspinn.setValue(maxspin.value())
	else:
	    if maxspin.value()<minspinn.value():
		maxspin.setValue(minspinn.value())
	
    
    def Setupwidget(self):
	
	self.setGeometry(QtCore.QRect(0, 0, 604, 116))
	self.setObjectName("page_control_setting")
	self.gridLayout_2 = QtGui.QGridLayout(self)
	self.gridLayout_2.setObjectName("gridLayout_2")
	self.groupBox_control = QtGui.QGroupBox(self)
	
	self.groupBox_control.setCheckable(True)
	self.groupBox_control.setChecked(False)
	self.groupBox_control.setObjectName("groupBox_control")
	self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_control)
	self.gridLayout_3.setObjectName("gridLayout_3")
	self.doubleSpinBox_minvalue = QtGui.QDoubleSpinBox(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.doubleSpinBox_minvalue.sizePolicy().hasHeightForWidth())
	self.doubleSpinBox_minvalue.setSizePolicy(sizePolicy)
	self.doubleSpinBox_minvalue.setFrame(True)
	self.doubleSpinBox_minvalue.setAccelerated(True)
	self.doubleSpinBox_minvalue.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.doubleSpinBox_minvalue.setDecimals(4)
	self.doubleSpinBox_minvalue.setMaximum(1.0)
	self.doubleSpinBox_minvalue.setSingleStep(0.01)
	self.doubleSpinBox_minvalue.setObjectName("doubleSpinBox_minvalue")
	self.gridLayout_3.addWidget(self.doubleSpinBox_minvalue, 1, 3, 1, 1)
	self.label_6 = QtGui.QLabel(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
	self.label_6.setSizePolicy(sizePolicy)
	self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	self.label_6.setObjectName("label_6")
	self.gridLayout_3.addWidget(self.label_6, 1, 2, 1, 1)
	self.label_7 = QtGui.QLabel(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
	self.label_7.setSizePolicy(sizePolicy)
	self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	self.label_7.setObjectName("label_7")
	self.gridLayout_3.addWidget(self.label_7, 1, 4, 1, 1)
	self.doubleSpinBox_maxvalue = QtGui.QDoubleSpinBox(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.doubleSpinBox_maxvalue.sizePolicy().hasHeightForWidth())
	self.doubleSpinBox_maxvalue.setSizePolicy(sizePolicy)
	self.doubleSpinBox_maxvalue.setWrapping(False)
	self.doubleSpinBox_maxvalue.setFrame(True)
	self.doubleSpinBox_maxvalue.setAccelerated(True)
	self.doubleSpinBox_maxvalue.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.doubleSpinBox_maxvalue.setDecimals(4)
	self.doubleSpinBox_maxvalue.setMaximum(1.0)
	self.doubleSpinBox_maxvalue.setSingleStep(0.01)
	self.doubleSpinBox_maxvalue.setProperty("value", 1.0)
	self.doubleSpinBox_maxvalue.setObjectName("doubleSpinBox_maxvalue")
	self.gridLayout_3.addWidget(self.doubleSpinBox_maxvalue, 1, 5, 1, 1)
	self.freq_checkBox = QtGui.QCheckBox(self.groupBox_control)
	self.freq_checkBox.setObjectName("freq_checkBox")
	self.gridLayout_3.addWidget(self.freq_checkBox, 0, 1, 1, 1)
	self.label = QtGui.QLabel(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
	self.label.setSizePolicy(sizePolicy)
	self.label.setObjectName("label")
	self.gridLayout_3.addWidget(self.label, 1, 1, 1, 1)
	self.MinFreq_doubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox_control)
	self.MinFreq_doubleSpinBox.setEnabled(False)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.MinFreq_doubleSpinBox.sizePolicy().hasHeightForWidth())
	self.MinFreq_doubleSpinBox.setSizePolicy(sizePolicy)
	self.MinFreq_doubleSpinBox.setReadOnly(False)
	self.MinFreq_doubleSpinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.MinFreq_doubleSpinBox.setMinimum(1.0)
	self.MinFreq_doubleSpinBox.setMaximum(30000.0)
	self.MinFreq_doubleSpinBox.setSingleStep(10.0)
	self.MinFreq_doubleSpinBox.setProperty("value", 100.0)
	self.MinFreq_doubleSpinBox.setObjectName("MinFreq_doubleSpinBox")
	self.gridLayout_3.addWidget(self.MinFreq_doubleSpinBox, 0, 3, 1, 1)
	self.MaxFreq_doubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox_control)
	self.MaxFreq_doubleSpinBox.setEnabled(False)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.MaxFreq_doubleSpinBox.sizePolicy().hasHeightForWidth())
	self.MaxFreq_doubleSpinBox.setSizePolicy(sizePolicy)
	self.MaxFreq_doubleSpinBox.setCorrectionMode(QtGui.QAbstractSpinBox.CorrectToNearestValue)
	self.MaxFreq_doubleSpinBox.setMinimum(1.0)
	self.MaxFreq_doubleSpinBox.setMaximum(30000.0)
	self.MaxFreq_doubleSpinBox.setSingleStep(10.0)
	self.MaxFreq_doubleSpinBox.setProperty("value", 300.0)
	self.MaxFreq_doubleSpinBox.setObjectName("MaxFreq_doubleSpinBox")
	self.gridLayout_3.addWidget(self.MaxFreq_doubleSpinBox, 0, 5, 1, 1)
	self.label_3 = QtGui.QLabel(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
	self.label_3.setSizePolicy(sizePolicy)
	self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	self.label_3.setObjectName("label_3")
	self.gridLayout_3.addWidget(self.label_3, 0, 2, 1, 1)
	self.label_4 = QtGui.QLabel(self.groupBox_control)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
	self.label_4.setSizePolicy(sizePolicy)
	self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
	self.label_4.setObjectName("label_4")
	self.gridLayout_3.addWidget(self.label_4, 0, 4, 1, 1)
	self.gridLayout_2.addWidget(self.groupBox_control, 0, 1, 1, 1)    
	QtCore.QObject.connect(self.freq_checkBox, QtCore.SIGNAL("toggled(bool)"), self.MinFreq_doubleSpinBox.setEnabled)
	QtCore.QObject.connect(self.freq_checkBox, QtCore.SIGNAL("toggled(bool)"), self.MaxFreq_doubleSpinBox.setEnabled)
	
	self.MinFreq_doubleSpinBox.valueChanged.connect(lambda: self.ValadateRange(self.MinFreq_doubleSpinBox,self.MinFreq_doubleSpinBox,self.MaxFreq_doubleSpinBox)) 
	self.MaxFreq_doubleSpinBox.valueChanged.connect(lambda: self.ValadateRange(self.MaxFreq_doubleSpinBox,self.MinFreq_doubleSpinBox,self.MaxFreq_doubleSpinBox)) 
	
	self.doubleSpinBox_minvalue.valueChanged.connect(lambda: self.ValadateRange(self.doubleSpinBox_minvalue,self.doubleSpinBox_minvalue,self.doubleSpinBox_maxvalue)) 
	self.doubleSpinBox_maxvalue.valueChanged.connect(lambda: self.ValadateRange(self.doubleSpinBox_maxvalue,self.doubleSpinBox_minvalue,self.doubleSpinBox_maxvalue)) 	
    
    
    
	self.groupBox_control.setTitle(QtGui.QApplication.translate("Dialog", "Enable", None, QtGui.QApplication.UnicodeUTF8))
	self.label_6.setText(QtGui.QApplication.translate("Dialog", "min", None, QtGui.QApplication.UnicodeUTF8))
	self.label_7.setText(QtGui.QApplication.translate("Dialog", "max", None, QtGui.QApplication.UnicodeUTF8))
	self.freq_checkBox.setText(QtGui.QApplication.translate("Dialog", "Use freq range", None, QtGui.QApplication.UnicodeUTF8))
	self.label.setText(QtGui.QApplication.translate("Dialog", "Slider Value Range", None, QtGui.QApplication.UnicodeUTF8))
	self.MinFreq_doubleSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", "Hz", None, QtGui.QApplication.UnicodeUTF8))
	self.MaxFreq_doubleSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", "Hz", None, QtGui.QApplication.UnicodeUTF8))
	self.label_3.setText(QtGui.QApplication.translate("Dialog", "min", None, QtGui.QApplication.UnicodeUTF8))
	self.label_4.setText(QtGui.QApplication.translate("Dialog", "max", None, QtGui.QApplication.UnicodeUTF8))
	#self.control_toolBox.setItemText(self.control_toolBox.indexOf(self.page_control_setting), QtGui.QApplication.translate("Dialog", "control name", None, QtGui.QApplication.UnicodeUTF8))    
    
    
    


audioscript = Audio_Dialog()
