# -*- coding: utf-8 -*-

#Audio Peak Analyzer v1.1.5
#BY http://steamcommunity.com/id/OMGTheresABearInMyOatmeal/
#feel free to modify the script for your own use
# Created: Mon Feb 25 13:57:52 2019


from PySide import QtCore, QtGui

try:
  import numpy
except ImportError:
  raise ImportError("You must add numpy to sfm by downloading this: https://www.dropbox.com/s/iigg6x9hntj4rlo/numpy-1.10.1.zip?dl=1 then extract the folders here:'SourceFilmmaker\game\sdktools\python\global\lib\site-packages'")

import wave,re,os,array
import filesystem.valve,sfm,sfmClipEditor,sfmApp,vs
class AudioFileAnalyze(object):
    

    def __init__(self, wavefile,overwriteChunk=None,printinfo=True):
        """ Init audio stream """ 

        self.wf = wave.open(wavefile, 'rb')
	self.printInfo=printinfo
        #acts like a buffer
        if overwriteChunk:
            self.chunk=overwriteChunk
        else:
            self.chunk=int(self.wf.getframerate()/sfmApp.GetFramesPerSecond())#each chunk is roughly one frame long
	if self.printInfo:
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
        self.progressbarWindow.setWindowTitle('Reading File: '+wavefile)
        self.progressbarWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.progressbar = QtGui.QProgressBar(self.progressbarWindow)
        self.progressbar.resize(600,30)
	self.progressbarWindow.show()
	
        #https://www.cameronmacleod.com/blog/reading-wave-python
	#instead of reading the wav file one chunk at a time we place the whole thing in memory and break it into sample chunks
        fmt_size = "h" if self.wf.getsampwidth() == 2 else "i"        
        self.DatawaveArray = array.array(fmt_size)
        self.DatawaveArray.fromfile(open(wavefile, 'rb'), os.path.getsize(wavefile)//self.DatawaveArray.itemsize)
        self.DatawaveArray = self.DatawaveArray[44//self.wf.getsampwidth():]#skips over header frame
	
	#normlize the array so its scaled to sfm value range of 0-1
	
	self.DatawaveArray=numpy.interp(self.DatawaveArray, (numpy.min(self.DatawaveArray), numpy.max(self.DatawaveArray)), (0.0, 1.0))
	
	#print numpy.max(self.DatawaveArray)
	#self.DatawaveArrayInterp=list(self.divide_chunks(self.DatawaveArrayInterp, int(self.chunk)))
	#print self.DatawaveArray
	#numpy.min(self.DatawaveArray)
        self.DatawaveArray=list(self.divide_chunks(self.DatawaveArray, int(self.chunk)))
	




	#divides a list into even chunks 
    def divide_chunks(self,l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


        #return sfm frame time of a single buffer
    def getBufferFrameTime(self,numofchunks=1):


        return vs.DmeTime_t(5.00000+(1.0/self.wf.getframerate())*(self.chunk*numofchunks))







    def analyze(self,dataValue,freqvalue,function,startframe,endframe):
        
        self.progressbarWindow.setWindowTitle('Calculating...')
        self.progressbar.setMinimum(0)       
        self.progressbar.setValue(0)
        


	duration=endframe-startframe
        swidth = self.wf.getsampwidth()
        RATE = self.wf.getframerate()
	
         
        index=0
        datachunk=self.DatawaveArray[index]
	#datachunkNormalized=self.DatawaveArrayInterp[index]
        #loops though entire wav file
        while len(datachunk) == self.chunk:
            
            self.progressbar.setValue(self.progressbar.value()+1)
            

	  
	  #peak value in chunk , not sure which one is better
	    dataValue.append(function(datachunk))
	   
          #  dataValue.append(float(numpy.max((datachunk)))/2.0**15)
	    
            #dataValue.append(float(numpy.average(numpy.abs(datachunk)))/2.0**15)
            
            
            #https://stackoverflow.com/questions/2648151/python-frequency-detection
            # Take the fft and square each value
            fftData=numpy.abs(numpy.fft.rfft(datachunk))**2.0
	    
            # find the maximum
            which = fftData[1:].argmax() + 1

            # use quadratic interpolation around the max
            if which != len(fftData)-1:
                y0,y1,y2 = numpy.log(fftData[which-1:which+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                 #find the frequency and output it
                freqvalue.append( (which+x1)*RATE/self.chunk)
		#print "The freq is %f Hz." %(freqvalue[-1])
            else:
                freqvalue.append(which*RATE/self.chunk)



	    if self.printInfo:
		framenum= (vs.DmeTime_t((startframe * (1.0 / sfmApp.GetFramesPerSecond()))) + self.getBufferFrameTime(numofchunks=index + 1)).ToFractionalFrame(vs.DmeFramerate_t(sfmApp.GetFramesPerSecond()))-(sfmApp.GetFramesPerSecond()*5.0)
		
		print "Chunk: %d | Frame: %d | Freq: %.02fHz." %(index,numpy.round(framenum),freqvalue[-1])

            
            #checks if we hit the endframe       
            if index >= (float(RATE/sfmApp.GetFramesPerSecond())*duration)//self.chunk:
                break    
            
           
            index+=1
            datachunk=self.DatawaveArray[index]
        
        self.wf.close()







        #not needed for this script but incase someone wants to use it,pyaudio needs to be added to sfm first
    def play(self):
        """ Play entire file """
        import pyaudio
        
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
    
    
   
    
    
    
    def __init__(self):
        
        self.Dialog = QtGui.QDialog()
	self.animset = sfm.GetCurrentAnimationSet()
        self.setupUi(self.Dialog)
        
        self.ExpandToolBox()
        self.audiofilepath = None
	self.audioAnalyze = None
	
	
	if  len(sfmClipEditor.GetSelectedClips("CDmeSoundClip"))==0 :
	    self.ErrorBox("One Wav file needs to be selected!")
	    return	
	
	self.sfmCDmeSoundClip=sfmClipEditor.GetSelectedClips()[0]
	ClipName= self.sfmCDmeSoundClip.GetName().replace('\\', '/')
	
	if "wav" not in ClipName[-4:]:
	    self.ErrorBox("Sound file Needs to be .wav")
	    return	    
	
	#we need to search though sfm mod paths cache because CDmeSoundClip does not contain a full file path
	
	search_paths=filesystem.valve.GameInfoFile(filesystem.valve.mod()+"/gameinfo.txt").getSearchMods()
	
	for index in range(len(search_paths)):
	    if os.path.isfile(search_paths[index]+"/sound/"+ClipName):
		self.audiofilepath= search_paths[index]+"/sound/"+ClipName
		

        
	





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
        
           
        
        #get start and end time of wav clip
        endFramevalue=self.sfmCDmeSoundClip.GetEndTime().ToFractionalFrame(vs.DmeFramerate_t(sfmApp.GetFramesPerSecond()))
        
        startFramevalue=self.sfmCDmeSoundClip.GetStartTime().ToFractionalFrame(vs.DmeFramerate_t(sfmApp.GetFramesPerSecond()))
	

	
  
        
        
        ###loops though all the pages and adds them to the dict if they are enabled
        ##key=control name: value=[min value,max value,min freq,max freq]
        controldict={}
        
        for index in range(self.control_toolBox.count ()):

            if self.control_toolBox.widget(index).IsEnabled():
                
                minvalue,maxvalue= self.control_toolBox.widget(index).GetValueRange()
		
		if self.control_toolBox.widget(index).IsFreqEnable():
		    minfreqvalue,maxfreqvalue= self.control_toolBox.widget(index).GetFreqRange()
		    controldict[self.control_toolBox.itemText(index)]=[minvalue,maxvalue,minfreqvalue,maxfreqvalue]
		else:
		    controldict[self.control_toolBox.itemText(index)]=[minvalue,maxvalue]

        ####
        
        if  not controldict:
            self.ErrorBox("No Controls were Enabled!")
            return

	# Change the operation mode to passthrough so changes chan be made temporarily
	sfm.SetOperationMode("Pass")	
	sfmApp.SetTimelineMode(2) 
	
        self.Dialog.hide()
        
        #inits audio class
        self.audioAnalyze = AudioFileAnalyze(self.audiofilepath,self.spinBox_buffer.value() if self.checkBox_overrideBuffer.isChecked() else None,self.checkBox_printfreq.isChecked() )
    
	
	
        #used to calulate the number of chunks ,for progressbar
	
        numframes=(numpy.ceil(float((self.audioAnalyze.wf.getframerate()/sfmApp.GetFramesPerSecond())*(endFramevalue-startFramevalue))/self.audioAnalyze.chunk))
        
        
        #set max for progressbar
        self.audioAnalyze.progressbar.setMaximum(numframes*2*len(controldict.keys()))

	
	if self.radioMax.isChecked():
	  function=numpy.max
	  
	elif self.radioAvg.isChecked():
	  function=numpy.mean
	  
	  
	elif self.radioMin.isChecked():
	  function=numpy.min	

	
	
	
        #fill up array with the data
        dataValue = []
	freqvalues=[]
        self.audioAnalyze.analyze(dataValue,freqvalues,function,startFramevalue,endFramevalue)#fill up the array with data points
       
	dataValue=numpy.interp(dataValue, (numpy.min(dataValue), numpy.max(dataValue)), (0.0, 1.0))


        #loop though the dict 
        for control in controldict.keys():

	    #add a blank key 1 frame before we start 
            beforetime=vs.DmeTime_t(5.0+((startFramevalue-1) * (1.0 / sfmApp.GetFramesPerSecond())))	    
            val=  self.GetKeyFrameValue(str(control),beforetime)	    
            self.AddKeyFrame(str(control),beforetime,val)
            
            #loop though data array
            for index in range(len(dataValue)):
		
		if len(controldict[control])==2:#only peak
		    
		    self.AddKeyFrame(str(control),
			             vs.DmeTime_t((startFramevalue * (1.0 / sfmApp.GetFramesPerSecond()))) + self.audioAnalyze.getBufferFrameTime(numofchunks=index + 1),
			             dataValue[index],controldict[control][0],controldict[control][1])	
		    
                if len(controldict[control])>2 and  controldict[control][2] <= freqvalues[index] <=controldict[control][3]:#only on freq
		    
		    
		    self.AddKeyFrame(str(control),
			             vs.DmeTime_t((startFramevalue * (1.0 / sfmApp.GetFramesPerSecond()))) + self.audioAnalyze.getBufferFrameTime(numofchunks=index + 1),
			             dataValue[index],controldict[control][0],controldict[control][1])
		    
		else:#give min value when not in freq range
		    self.AddKeyFrame(str(control),
			             vs.DmeTime_t((startFramevalue * (1.0 / sfmApp.GetFramesPerSecond()))) + self.audioAnalyze.getBufferFrameTime(numofchunks=index + 1),
			             controldict[control][0])		    
	    
		
                
                self.audioAnalyze.progressbar.setValue(self.audioAnalyze.progressbar.value() + 1)

            
            #set last key to value before the clip
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
            self.animset.FindControl(controlName).rightvaluechannel.log.FindOrAddKey(time,vs.DmeTime_t(1.0),numpy.clip(value,low,high))
            self.animset.FindControl(controlName).leftvaluechannel.log.FindOrAddKey(time,vs.DmeTime_t(1.0),numpy.clip(value,low,high)) 
        else:
            self.animset.FindControl(controlName).channel.log.FindOrAddKey(time,vs.DmeTime_t(1.0),numpy.clip(value,low,high))        
        
        
        
        
    def GetKeyFrameValue(self,controlName,time):
	
	if self.animset.FindControl(controlName).HasAttribute("rightvaluechannel"):
	    return numpy.average([self.animset.FindControl(controlName).rightvaluechannel.log.GetValue(time), self.animset.FindControl(controlName).leftvaluechannel.log.GetValue(time)] )

	else:
	    return self.animset.FindControl(controlName).channel.log.GetValue(time)        
                
        
        
        
        
        
    
        
        #adds a control page for each control slider in the animset
    def ExpandToolBox(self):
        
        for element in self.animset.controls:
            if type(element) is vs.datamodel.CDmElement:
		self.control_toolBox.addItem(TemplateControlPageWidget(),str(element.name))
                  
        

    def setupUi(self, Dialog):
	Dialog.setObjectName("Dialog")
	Dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	#Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
	Dialog.resize(800, 500)
	sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
	sizePolicy.setHorizontalStretch(0)
	sizePolicy.setVerticalStretch(0)
	sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
	Dialog.setSizePolicy(sizePolicy)
	Dialog.setMinimumSize(QtCore.QSize(750, 0))
	Dialog.setMaximumSize(QtCore.QSize(800, 16777215))
	font = QtGui.QFont()
	font.setPointSize(10)
	Dialog.setFont(font)
	Dialog.setFocusPolicy(QtCore.Qt.TabFocus)
	Dialog.setSizeGripEnabled(True)
	#Dialog.setModal(True)
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
	self.spinBox_buffer.setMinimum(2)
	self.spinBox_buffer.setMaximum(65536)
	self.spinBox_buffer.setSingleStep(1)
	self.spinBox_buffer.setValue(2048)
	self.spinBox_buffer.setObjectName("spinBox_buffer")
	self.horizontalLayout_3.addWidget(self.spinBox_buffer)
	spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
	
	self.checkBox_printfreq = QtGui.QCheckBox(self.groupBox)
	self.checkBox_printfreq.setText("Print Frequency")
	
	
	self.label = QtGui.QLabel(self.groupBox)
	self.label.setText("Data Function:")
	
	self.radioMin=QtGui.QRadioButton(self.groupBox)
	self.radioMin.setText("Min")
	
	self.radioMax=QtGui.QRadioButton(self.groupBox)
	self.radioMax.setText("Max")
	self.radioMax.setChecked(True)
	
	self.radioAvg=QtGui.QRadioButton(self.groupBox)
	self.radioAvg.setText("Avg")	
	
	self.line2 = QtGui.QFrame(self.groupBox)
	self.line2.setFrameShape(QtGui.QFrame.VLine)
	self.line2.setFrameShadow(QtGui.QFrame.Sunken)	
	self.horizontalLayout_3.addWidget(self.line2)
	self.horizontalLayout_3.addWidget(self.label)
	self.horizontalLayout_3.addWidget(self.radioMin)
	self.horizontalLayout_3.addWidget(self.radioMax)
	self.horizontalLayout_3.addWidget(self.radioAvg)
	
	self.line3 = QtGui.QFrame(self.groupBox)
	self.line3.setFrameShape(QtGui.QFrame.VLine)
	self.line3.setFrameShadow(QtGui.QFrame.Sunken)
	self.horizontalLayout_3.addWidget(self.line3)
	
	
	self.horizontalLayout_3.addWidget(self.checkBox_printfreq)
	
	
	
	
	#self.horizontalLayout_3.addItem(spacerItem)
	
	
	
	
	self.verticalLayout_4.addLayout(self.horizontalLayout_3)
	self.verticalLayout.addWidget(self.groupBox)
	self.buttonBox = QtGui.QPushButton("Start")
	
	#self.buttonBox.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

	#printfreq = QtGui.QAction(self.buttonBox)
	#printfreq.setText("Print Frequency")
	#printfreq.triggered.connect(self.printButton)
	#self.buttonBox.addAction(printfreq)

    	
	
	
	self.buttonBox.setObjectName("buttonBox")
	self.buttonBox.setAutoDefault(False)
	self.verticalLayout.addWidget(self.buttonBox)
	
      
        self.retranslateUi(Dialog)
        self.control_toolBox.setCurrentIndex(0)
        self.control_toolBox.layout().setSpacing(8)

        QtCore.QObject.connect(self.checkBox_overrideBuffer, QtCore.SIGNAL("toggled(bool)"), self.spinBox_buffer.setEnabled)
       
	self.buttonBox.clicked.connect(self.startAnalyze)
     #   QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("Clicked()"), self.startAnalyze)
        
        QtCore.QMetaObject.connectSlotsByName(Dialog)


	self.MiscBox.setTitle(self.animset.GetName()+" control options")














    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Audio Peak Analyzer v1.1.5", None, QtGui.QApplication.UnicodeUTF8))


	self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Misc options", None, QtGui.QApplication.UnicodeUTF8))
	self.addBookmarkCheckBox.setText(QtGui.QApplication.translate("Dialog", "Add Bookmarks", None, QtGui.QApplication.UnicodeUTF8))
	self.checkBox_overrideBuffer.setText(QtGui.QApplication.translate("Dialog", "Override BufferSize", None, QtGui.QApplication.UnicodeUTF8))
	
    #custom QWidget for control page
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
	self.MinFreq_doubleSpinBox.setProperty("value", 50.0)
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
	
	self.MinFreq_doubleSpinBox.editingFinished.connect(lambda: self.ValadateRange(self.MinFreq_doubleSpinBox,self.MinFreq_doubleSpinBox,self.MaxFreq_doubleSpinBox)) 
	self.MaxFreq_doubleSpinBox.editingFinished.connect(lambda: self.ValadateRange(self.MaxFreq_doubleSpinBox,self.MinFreq_doubleSpinBox,self.MaxFreq_doubleSpinBox)) 
	
	self.doubleSpinBox_minvalue.editingFinished.connect(lambda: self.ValadateRange(self.doubleSpinBox_minvalue,self.doubleSpinBox_minvalue,self.doubleSpinBox_maxvalue)) 
	self.doubleSpinBox_maxvalue.editingFinished.connect(lambda: self.ValadateRange(self.doubleSpinBox_maxvalue,self.doubleSpinBox_minvalue,self.doubleSpinBox_maxvalue)) 	
    
    
    
	self.groupBox_control.setTitle(QtGui.QApplication.translate("Dialog", "Enable", None, QtGui.QApplication.UnicodeUTF8))
	self.label_6.setText(QtGui.QApplication.translate("Dialog", "Min Value", None, QtGui.QApplication.UnicodeUTF8))
	self.label_7.setText(QtGui.QApplication.translate("Dialog", "Max Value", None, QtGui.QApplication.UnicodeUTF8))
	self.freq_checkBox.setText(QtGui.QApplication.translate("Dialog", "Set Frequency Range", None, QtGui.QApplication.UnicodeUTF8))
	self.label.setText(QtGui.QApplication.translate("Dialog", "Slider Value Range", None, QtGui.QApplication.UnicodeUTF8))
	self.MinFreq_doubleSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", "Hz", None, QtGui.QApplication.UnicodeUTF8))
	self.MaxFreq_doubleSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", "Hz", None, QtGui.QApplication.UnicodeUTF8))
	self.label_3.setText(QtGui.QApplication.translate("Dialog", "Min Frequency ", None, QtGui.QApplication.UnicodeUTF8))
	self.label_4.setText(QtGui.QApplication.translate("Dialog", "Max Frequency ", None, QtGui.QApplication.UnicodeUTF8))
	#self.control_toolBox.setItemText(self.control_toolBox.indexOf(self.page_control_setting), QtGui.QApplication.translate("Dialog", "control name", None, QtGui.QApplication.UnicodeUTF8))    
    
    
    


audioscript = Audio_Dialog()
