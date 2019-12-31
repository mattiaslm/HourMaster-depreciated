"""
Widget Class w/ All Tables Side by Side

Written with PyQt5 

Mattias Lange McPherson

July 5th, 2019

"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import tables as tbl
import managers as man
import components as comp

class TestWindow(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        arg_field = self.startUp()
        if not arg_field[1]:
            self.db = man.DBManager('E:\Projects\Python\HourMaster\HM_A2-5\db\\l_test.db')
        else:
            m_format = tbl.getModelSchema()
            self.db = man.DBManager.setUp('',m_format[0],m_format[1])    
        sig = man.sigManager()
        if arg_field[0]:
            sig.trk.track()
        self.pm = man.PayManager(self.db,sig,co='co',r='ra',ca='ca',j='jo') 
        co_model = tbl.CompanyModel(self.db,sig)
        co_model.loadData()
        self.co_table = tbl.CompanyTable(co_model)

        r_model = tbl.RateModel(self.db,co_model,sig)
        r_model.loadData()
        self.r_table = tbl.RateTable(r_model)
        self.r_table.setProxy(comp.ReferencedFilter(self.co_table,1))

        j_model = tbl.JobModel(self.db,co_model,r_model,sig,self.pm)
        j_model.loadData()
        self.j_table = tbl.JobTable(j_model)  
        self.j_table.setProxy(comp.ReferencedFilter(self.r_table,2))

        ca_model = tbl.CallModel(self.db,co_model,r_model,j_model,sig,self.pm)
        ca_model.loadData()
        self.ca_table = tbl.CallTable(ca_model)
        self.ca_table.setProxy(comp.ReferencedFilter(self.co_table,2))


        self.grid = QHBoxLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.co_table)
        self.grid.addWidget(self.r_table)
        self.grid.addWidget(self.j_table)
        self.grid.addWidget(self.ca_table)
        self.show()

    @classmethod
    def setUp(cls):
        m_format = tbl.getModelSchema()
        setUpDB = man.DBManager.setUp('m_test',m_format[0],m_format[1])
        return cls()

    def startUp(self):
        arg_field = [0,0]
        args = sys.argv[1:]
        if '--track' in args or '-t' in args:
            arg_field[0] = 1
        if '--new' in args or '-n' in args:
            arg_field[1] = 1
        return arg_field        

class RefTestWindow(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        #Arg Parsing
        arg_field = startUp()
        if not arg_field[1]:
            self.db = man.DBManager('m_test')
        else:
            m_format = tbl.getModelSchema()
            self.db = man.DBManager.setUp('',m_format[0],m_format[1]) 

        #Manager SetUp
        sig = man.sigManager()
        if arg_field[0]:
            sig.trk.track()
        self.pm = man.PayManager(self.db,sig,co='co',r='ra',ca='ca',j='jo') 

        #Model SetUp
        co_model = tbl.CompanyModel(self.db,sig)
        co_model.loadData()

        r_model = tbl.RateModel(self.db,co_model,sig)
        r_model.loadData()

        j_model = tbl.JobModel(self.db,co_model,r_model,sig,self.pm)
        j_model.loadData()

        ca_model = tbl.CallModel(self.db,co_model,r_model,j_model,sig,self.pm)
        ca_model.loadData()

        #Table SetUp
        models = {'co':co_model,'ra':r_model,'jo':j_model,'ca':ca_model}
        self.co_tab = comp.GenericEntryTab(models,3)

        #Layout
        self.grid = QHBoxLayout()
        self.setLayout(self.grid)
        self.grid.addWidget(self.co_tab)
        self.show()

                                
    def setUp(cls):
        m_format = tbl.getModelSchema()
        setUpDB = man.DBManager.setUp('m_test',m_format[0],m_format[1])
        return cls()

def startUp():
        arg_field = [0,0]
        args = sys.argv[1:]
        if '--track' in args or '-t' in args:
            arg_field[0] = 1
        if '--new' in args or '-n' in args:
            arg_field[1] = 1
        return arg_field 

if __name__ == '__main__':
    man.DBManager.setUp('E:\Projects\Python\HourMaster\HM_A2-5\db\\l_test.db',tbl.getModelSchema()[0][:-1],tbl.getModelSchema()[1][:-1])
    app = QApplication(sys.argv)
    win = RefTestWindow()
    app.exec_()
    