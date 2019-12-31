"""
HourMaster Main Window

Written w/ PyQt5 

Mattias Lange McPherson

December 21st, 2019
"""

version = '0.02.5.1a'

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import managers as man
import sys
import tables as tbl
import components as comp
import tools
import timeit
import random as rand

class MainWindow(QMainWindow):
    def __init__(self,db_path,size=(800,800),parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle('HourMaster V%s' %version)
        self.size = size
        self.config()
        self.menuConfig()
        self.show()

    def config(self,temp_db=False):
        #Arg Parsing
        arg_field = startUp()
        if not arg_field[1] and not temp_db:
            self.db = man.DBManager(self.db_path)
        else:
            m_format = tbl.getModelSchema()
            self.db = man.DBManager.setUp('',m_format[0],m_format[1]) 

        #Manager SetUp
        self.sig = man.sigManager()
        if arg_field[0]:
            self.sig.trk.track()
        self.pm = man.PayManager(self.db,self.sig,co='co',r='ra',ca='ca',j='jo',pl='pl') 

        #Model SetUp
        try:
            co_model = tbl.CompanyModel(self.db,self.sig)
            co_model.loadData()

            r_model = tbl.RateModel(self.db,co_model,self.sig)
            r_model.loadData()

            j_model = tbl.JobModel(self.db,co_model,r_model,self.sig,self.pm)
            j_model.loadData()

            ca_model = tbl.CallModel(self.db,co_model,r_model,j_model,self.sig,self.pm)
            ca_model.loadData()

            pl_model = tbl.PayLevelModel(self.db,r_model,self.sig,self.pm)
            pl_model.loadData()

            self.models = {'co':co_model,'ra':r_model,'jo':j_model,'ca':ca_model,'pl':pl_model}

        #Widget SetUp
            data_tab = QTabWidget()
            data_tab.addTab(comp.GenericEntryTab(self.models,0,size=(self.size[0],self.size[1]-200)),'Companies')
            data_tab.addTab(comp.GenericEntryTab(self.models,1,size=(self.size[0],self.size[1]-200)),'Rates')
            data_tab.addTab(comp.GenericEntryTab(self.models,2,size=(self.size[0],self.size[1]-200)),'Jobs')
            data_tab.addTab(comp.GenericEntryTab(self.models,3,size=(self.size[0],self.size[1]-200)),'Calls')

            nav_tab = QTabWidget()
            nav_tab.addTab(data_tab,'Data')

            self.setCentralWidget(nav_tab)
        except Exception as e:
            print(e)
            self.new()

    def menuConfig(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        option_menu = menu_bar.addMenu('Options')
        tool_menu = menu_bar.addMenu('Tools')
        export_menu = tool_menu.addMenu('Export')
        debug_menu = menu_bar.addMenu('Debug')

        load_action = QAction('Load',self)
        load_action.setShortcut('Shift+O')
        load_action.triggered.connect(self.load)
        file_menu.addAction(load_action)

        save_action = QAction('Save As',self)
        save_action.setShortcut('Shift+s')
        save_action.triggered.connect(self.saveAs)
        file_menu.addAction(save_action)

        new_action = QAction('New',self)
        new_action.setShortcut('Shift+N')
        new_action.triggered.connect(self.new)
        file_menu.addAction(new_action)

        update_action = QAction('Update',self)
        update_action.triggered.connect(self.updateDB)
        tool_menu.addAction(update_action)

        import_action = QAction('Import',self)
        import_action.triggered.connect(self._import)
        tool_menu.addAction(import_action)

        export_CSV_action = QAction('CSV',self)
        export_CSV_action.triggered.connect(self.exportCSV)
        export_menu.addAction(export_CSV_action)

        recalc_action = QAction('ReCalculate',self)
        recalc_action.triggered.connect(self.reCalc)
        debug_menu.addAction(recalc_action)

        perf_test_action = QAction('PerfTest',self)
        perf_test_action.triggered.connect(self.perfTest)
        debug_menu.addAction(perf_test_action)

    def load(self):
        self.db_path = str(QFileDialog.getOpenFileName(filter='*.db')[0])
        if self.db_path != '':
            print('LOAD:')
            print(timeit.timeit(lambda: self.config(),number=1))
     
    def new(self):
        self.config(temp_db=True)

    def saveAs(self,db_path=None):
        if db_path:
            self.db.dbTransfer(to=db_path)
            self.db_path = db_path
            self.config()
        else:    
            save_file = QFileDialog.getSaveFileName(filter='*.db')[0]
            self.db.dbTransfer(to=save_file)
            self.db_path = db_path
            self.config()

    def updateDB(self):
        self.db_path = str(QFileDialog.getOpenFileName(filter='*.db')[0])
        tools.Updater(self.db_path)
        self.config()       

    def _import(self):
        path = str(QFileDialog.getOpenFileName()[0])
        if path:
            self.db_path = comp.Importer(path).getSavePath()
            self.config()
            self.reCalc()    

    def exportCSV(self):
        save_path = QFileDialog.getSaveFileName(filter='*.csv')[0]
        tools.Exporter(self.db_path,save_path,'csv')
        print('Export Complete')

    def reCalc(self):
        self.pm.reCalcAll()
        
    def perfTest(self):
        print('RECALC:')
        print(timeit.timeit(lambda: self.reCalc(),number=1))
        print('UPDATE CALL (AVG OF 5):')
        call_ids = [rand.randint(0,self.models['ca'].rowCount()-1) for i in range(5)]
        for _id in call_ids:
            self.db.update('ca',_id,5,'sched')
        update_call_times = [timeit.timeit(lambda: self.pm.updatePay(_id,3),number=1) for _id in call_ids]
        print(sum(update_call_times)/len(update_call_times)) 
        get_alt_times = [timeit.timeit(lambda: self.models['ca'].getAltDisplay(2),number=1) for i in range(5)]
        print('GET_ALT_COLS (AVG OF 5):')
        print(sum(get_alt_times)/len(get_alt_times))       

def startUp():
        arg_field = [0,0]
        args = sys.argv[1:]
        if '--track' in args or '-t' in args:
            arg_field[0] = 1
        if '--new' in args or '-n' in args:
            arg_field[1] = 1
        return arg_field 

if __name__ == '__main__':
    db_path = 'E:\Projects\Python\HourMaster\HourMaster_Alpha\db\\time_test_10.db'
    app = QApplication(sys.argv)
    win = MainWindow(db_path)
    app.exec_()
