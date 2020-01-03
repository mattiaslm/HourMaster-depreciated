"""
HourMaster Dialog Classes

Written with PyQt5 

Mattias Lange McPherson

June 18th, 2019

"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import datetime as dt


version = '0.1'

class NewCompanyDialog(QWidget):

    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config()

    def config(self):

        self.color_data = [255,255,255]

        self.setFixedSize(220,200)
        self.setWindowTitle('New Company')

        self.g_box = QGroupBox('Company Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout)

        self.name_label = QLabel('Co. Name:')
        self.name_edit = QLineEdit()
        self.short_lable = QLabel('Short Name:')
        self.short_edit = QLineEdit()
        self.status_label = QLabel('Status:')
        self.status_edit = QComboBox()
        self.status_edit.addItems(self.model.getAltDisplay(2)[1])
    
        self.g_box_layout.addWidget(self.name_label,0,0)
        self.g_box_layout.addWidget(self.name_edit,0,1)
        self.g_box_layout.addWidget(self.short_lable,1,0)
        self.g_box_layout.addWidget(self.short_edit,1,1)
        self.g_box_layout.addWidget(self.status_label,2,0)
        self.g_box_layout.addWidget(self.status_edit,2,1)

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show()

    def conf(self):
        name = self.name_edit.text()
        short = self.short_edit.text()
        stat = self.status_edit.currentIndex()
        model_data = [name,short,stat]
        self.model.newEntry(model_data,list(self.color_data)[0:3])
        
        self.close()            
                  
    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()

class NewRateDialog(QWidget):
    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config() 

    def config(self):
        self.color_data = [255,255,255]

        self.setFixedSize(220,200)
        self.setWindowTitle('New Rate')

        self.companies = self.model.getAltDisplay(self.model.co_col)[1]

        if not self.companies:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Add Company First')
            co_message.setWindowTitle('No Companies')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None  

        self.co_index = self.model.getAltDisplay(self.model.co_col)[0]


        self.g_box = QGroupBox('Rate Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout)

        self.name_label = QLabel('Rate Name:')
        self.name_edit = QLineEdit()
        self.rate_lable = QLabel('Rate:')
        self.rate_edit = QDoubleSpinBox()
        self.rate_edit.setRange(0,10000)
        self.min_lable = QLabel('Min:')
        self.min_edit = QDoubleSpinBox()
        self.status_label = QLabel('Status:')
        self.status_edit = QComboBox()
        self.status_edit.addItems(self.model.getAltDisplay(4)[1])
        self.co_label = QLabel('Company')
        self.co_edit = QComboBox()
        self.co_edit.addItems(self.companies)

        self.g_box_layout.addWidget(self.name_label,0,0)
        self.g_box_layout.addWidget(self.name_edit,0,1)
        self.g_box_layout.addWidget(self.rate_lable,1,0)
        self.g_box_layout.addWidget(self.rate_edit,1,1)
        self.g_box_layout.addWidget(self.min_lable,2,0)
        self.g_box_layout.addWidget(self.min_edit,2,1)
        self.g_box_layout.addWidget(self.status_label,3,0)
        self.g_box_layout.addWidget(self.status_edit,3,1)
        self.g_box_layout.addWidget(self.co_label,4,0)
        self.g_box_layout.addWidget(self.co_edit,4,1)

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show()

    def conf(self):
        name = self.name_edit.text()
        rate = self.rate_edit.value()
        min_ = self.min_edit.value()
        stat = self.status_edit.currentIndex()
        co_index = self.co_index[self.co_edit.currentIndex()]

        self.model.newEntry(
            [name,co_index,rate,min_,stat],
            list(self.color_data[:3])
        )

        self.close() 

    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()  

class NewJobDialog(QWidget):
    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config()

    def config(self):
        self.color_data = [255,255,255]

        self.setFixedSize(220,200)
        self.setWindowTitle('New Job')

        self.companies = self.model.getAltDisplay(self.model.co_col)[1]

        if not self.companies:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Add Company First')
            co_message.setWindowTitle('No Companies')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None  

        self.co_index = self.model.getAltDisplay(self.model.co_col)[0]

        self.g_box = QGroupBox('Job Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout)

        self.name_label = QLabel('Job Name:')
        self.name_edit = QLineEdit()
        self.co_label = QLabel('Company:')
        self.co_edit = QComboBox()
        self.co_edit.addItems(self.companies)
        self.co_edit.currentIndexChanged.connect(self.changeRates)
        self.rate_label = QLabel('Rate:')
        self.rate_edit = QComboBox()
        self.changeRates()

        self.g_box_layout.addWidget(self.name_label,0,0)
        self.g_box_layout.addWidget(self.name_edit,0,1)
        self.g_box_layout.addWidget(self.co_label,1,0)
        self.g_box_layout.addWidget(self.co_edit,1,1)
        self.g_box_layout.addWidget(self.rate_label,2,0)
        self.g_box_layout.addWidget(self.rate_edit,2,1)

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show() 

    def changeRates(self):
        cur_co = self.co_index[self.co_edit.currentIndex()]
        self.rate_index = self.model.db.selectByVal(
            self.model.rm.db_name,'co',cur_co
        )
        rates = [
            self.model.db.getVal(self.model.rm.db_name,i,'name') \
                for i in self.rate_index
            ]
        self.rate_edit.clear()
        self.rate_edit.addItems(rates)

    def conf(self):
        if self.rate_edit.count() == 0:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Choose a Rate')
            co_message.setWindowTitle('No Rates')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None  

        name = self.name_edit.text()
        co = self.co_index[self.co_edit.currentIndex()]
        rate = self.rate_index[self.rate_edit.currentIndex()]

        self.model.newEntry([name,co,rate],list(self.color_data[:3]))

        self.close()

    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()          
             
class NewCallDialog(QWidget):
    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config()
        
    def config(self):
        self.color_data = [255,255,255]

        self.setFixedSize(315,200)
        self.setWindowTitle('New Call')

        self.companies = self.model.getAltDisplay(self.model.co_col)[1]
        self.rates = self.model.getAltDisplay(self.model.r_col)[1]

        if not self.companies:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Add Company First')
            co_message.setWindowTitle('No Companies')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None    

        if not self.rates:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Add Rate First')
            co_message.setWindowTitle('No Rates')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None
                         
        self.co_index = self.model.getAltDisplay(self.model.co_col)[0]

        self.g_box = QGroupBox('Call Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout) 

        self.name_label = QLabel('Call Name:')
        self.name_edit = QLineEdit()
        self.date_label = QLabel('Date: ')
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.co_label = QLabel('Company:')
        self.co_edit = QComboBox()
        self.co_edit.addItems(self.companies)
        self.co_edit.currentIndexChanged.connect(self.changeRates)
        self.co_edit.currentIndexChanged.connect(self.changeJobs)
        self.rate_label = QLabel('Rate:')
        self.rate_edit = QComboBox()
        self.rate_edit.currentIndexChanged.connect(self.changeJobs)
        self.job_label = QLabel('Job')
        self.job_edit = QComboBox()
        self.s_hr_label = QLabel('Sched.')
        self.s_hr_edit = QDoubleSpinBox()
        self.a_hr_label = QLabel('Actual')
        self.a_hr_edit = QDoubleSpinBox()
        self.changeRates()
        self.changeJobs()

        self.g_box_layout.addWidget(self.name_label,0,0,1,1)
        self.g_box_layout.addWidget(self.name_edit,0,1,1,2)
        self.g_box_layout.addWidget(self.date_label,1,0,1,2)
        self.g_box_layout.addWidget(self.date_edit,1,1,1,2)
        self.g_box_layout.addWidget(self.co_label,2,0)
        self.g_box_layout.addWidget(self.co_edit,2,1)
        self.g_box_layout.addWidget(self.rate_label,2,2)
        self.g_box_layout.addWidget(self.rate_edit,2,3)
        self.g_box_layout.addWidget(self.job_label,2,4)
        self.g_box_layout.addWidget(self.job_edit,2,5)
        self.g_box_layout.addWidget(self.s_hr_label,3,0)
        self.g_box_layout.addWidget(self.s_hr_edit,3,1) 
        self.g_box_layout.addWidget(self.a_hr_label,3,2)
        self.g_box_layout.addWidget(self.a_hr_edit,3,3)       

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show()  

    def changeRates(self):
        cur_co = self.co_index[self.co_edit.currentIndex()]
        self.rate_index = self.model.db.single(self.model.db.selectByVal(
            self.model.rm.db_name,'co',cur_co
        ))
        self.rates = [
            self.model.db.getVal(self.model.rm.db_name,i,'name') \
                for i in self.rate_index
            ]
        self.rate_edit.clear()
        self.rate_edit.addItems(self.rates)

    def changeJobs(self):
        cur_co = self.co_index[self.co_edit.currentIndex()]
        cur_rate = self.rate_index[self.rate_edit.currentIndex()]
        self.job_index = [0] + self.model.db.selectByVals(
            self.model.jm.db_name,co=cur_co,rate=cur_rate
        )
        jobs = ['N/A']+[
            self.model.db.getVal(self.model.jm.db_name,i,'name') \
                for i in self.job_index[1:]
            ]
        if type(jobs[-1]) == list:
            del jobs[-1]

        self.job_edit.clear()
        self.job_edit.addItems(jobs)

    def conf(self):
        if self.rate_edit.count() == 0:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Choose a Rate')
            co_message.setWindowTitle('No Rates')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None  

        name = self.name_edit.text()
        date = self.date_edit.date().toPyDate().toordinal()
        co = self.co_index[self.co_edit.currentIndex()]
        rate = self.rate_index[self.rate_edit.currentIndex()]
        job = self.job_index[self.job_edit.currentIndex()]
        s_hrs = self.s_hr_edit.value()
        s_pay = 0
        a_hrs = self.a_hr_edit.value()
        a_pay = 0

        self.model.newEntry(
            [date,name,co,rate,job,s_hrs,s_pay,a_hrs,a_pay],
            list(self.color_data[:3])
        )

        self.close()

    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()    

class NewPayLevelDialog(QWidget):
    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config()

    def config(self):
        self.color_data = [255,255,255]

        self.setFixedSize(315,200)
        self.setWindowTitle('New Pay Level')

        self.rates = self.model.getAltDisplay(self.model.r_col)[1]

        if not self.rates:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Add Rate First')
            co_message.setWindowTitle('No Rates')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None

        self.rate_index = self.model.getAltDisplay(self.model.r_col)[0]    
        
        self.g_box = QGroupBox('Pay Level Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout)

        self.rate_label = QLabel('Rate:')
        self.rate_edit = QComboBox()
        self.rate_edit.addItems(self.rates)
        self.date_label = QLabel('Effective Date:')
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.level_label = QLabel('Pay Level:')
        self.level_edit = QDoubleSpinBox()

        self.g_box_layout.addWidget(self.rate_label,0,0)
        self.g_box_layout.addWidget(self.rate_edit,0,1)
        self.g_box_layout.addWidget(self.date_label,1,0)
        self.g_box_layout.addWidget(self.date_edit,1,1)
        self.g_box_layout.addWidget(self.level_label,2,0)
        self.g_box_layout.addWidget(self.level_edit,2,1)

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)        

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show()

    def conf(self):
        if self.rate_edit.count() == 0:
            co_message = QMessageBox()
            co_message.setIcon(QMessageBox.Warning)
            co_message.setText('Choose a Rate')
            co_message.setWindowTitle('No Rates')
            co_message.setStandardButtons(QMessageBox.Ok)
            val = co_message.exec_()
            return None  

        rate = self.rate_index[self.rate_edit.currentIndex()]
        date = self.date_edit.date().toPyDate().toordinal()
        level = self.level_edit.value()

        self.model.newEntry(
            [rate,level,date],
            list(self.color_data[:3])
        )

        self.close()

    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()            
    
class AddRaiseDialog(QWidget):
    def __init__(self,rate_id,model,parent=None):
        super().__init__(parent)
        self.rate_id = rate_id
        self.model = model
        self.config()

    def config(self):
        self.color_data = [255,255,255]

        self.setFixedSize(315,200)
        self.setWindowTitle('Add Raise') 

        self.g_box = QGroupBox('Raise Info',self)
        self.g_box_layout = QGridLayout()
        self.g_box.setLayout(self.g_box_layout)

        self.date_label = QLabel('Effective Date:')
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.level_label = QLabel('Pay Level:')
        self.level_edit = QDoubleSpinBox().setRange(0,10000)       

        self.g_box_layout.addWidget(self.date_label,0,0)
        self.g_box_layout.addWidget(self.date_edit,0,1)
        self.g_box_layout.addWidget(self.level_label,1,0)
        self.g_box_layout.addWidget(self.level_edit,1,1)

        conf_button = QPushButton('Add',self)
        conf_button.clicked.connect(self.conf)
        color_button = QPushButton('Color',self)
        color_button.clicked.connect(self.setColor)
        cancel_button = QPushButton('Cancel',self)
        cancel_button.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.g_box,0,0,1,0)
        self.layout.addWidget(conf_button,1,0)
        self.layout.addWidget(color_button,1,1)
        self.layout.addWidget(cancel_button,1,2)
        self.g_box.show()

        self.show()

    def conf(self):
        date = self.date_edit.date().toPyDate().toordinal()
        level = self.level_edit.value()
        old_level = self.model.model_data[self.model.db_index.index(self.rate_id)][2]
        self.model.sig.addRaiseSig(self.rate_id,date,old_level,level,list(self.color_data[:3]))

        self.close()

    def setColor(self,event):
        picker = QColorDialog(self)
        picker.colorSelected.connect(self.colorChange)
        picker.show() 

    def colorChange(self,QColor):
        self.color_data = QColor.getRgb()           

class DateEdit(QDialog):

    def __init__(self,posx,posy,parent=None):
        super().__init__(parent)
        self.config(posx,posy)

    def config(self,posx,posy):
        self.setGeometry(posx,posy,200,100)
        self.setFixedSize(200,100)
        self.setWindowTitle('Select Date')
        self.date = QDateEdit(QDate.currentDate())
        self.conf = QPushButton('Ok')
        self.conf.clicked.connect(self._conf)
        self.cancel = QPushButton('Cancel')
        self.cancel.clicked.connect(self._cancel)


        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.date,0,0,1,0)
        layout.addWidget(self.conf,1,0)
        layout.addWidget(self.cancel,1,1)

        self.show()

    def _conf(self):
        self.accept()

    def _cancel(self):
        self.close()   

