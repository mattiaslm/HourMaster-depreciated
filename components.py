"""
HourMaster GUI Components

Written w/ PyQt5

Mattias Lange McPherson

November 16th, 2019
"""


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import tables as tbl
import managers as man
import json
import datetime as dt

class ReferencedFilter(QSortFilterProxyModel):
    def __init__(self,ref_table,ref_col,col_exclude=[],parent=None):
        super().__init__(parent)
        self.ref = ref_table
        self.col = ref_col
        self.ref.selectionModel().selectionChanged.connect(self.selChanged)
        self.sel = []
        self.col_exclude = col_exclude
        self.setFilterRole(Qt.EditRole)

    def selChanged(self):
        self.sel = self.ref.getSelIDs()
        self.invalidateFilter()

    def filterAcceptsRow(self,row,index,parent=None):
        sourceData = self.sourceModel().model_data[row][self.col]
        if self.sourceModel().model_data[row][self.col] in self.sel:
            return True
        else:
            return False    

    def filterAcceptsColumn(self,col,index):
        if col in self.col_exclude:
            return False
        else:
            return True    

class ReferenceView(QTabWidget):
    def __init__(self,main_table,models,type_num_exclude=[],parent=None):
        super().__init__(parent)
        self.ref = main_table
        self.ref_type = self.ref.typenum()
        self.col = self.getCol()
        self.exclude = type_num_exclude
        self.setUp(models)

    def setUp(self,models):
        tab_list = []
        if self.ref_type < 0 and 0 not in self.exclude:
            tab_list.append((tbl.CompanyTable(models['co']),'Companies'))
            proxy = ReferencedFilter(
                self.ref,getattr(tab_list[-1][0].model,self.col))
            tab_list[-1][0].setProxy(proxy)
        if self.ref_type < 1 and 1 not in self.exclude:
            tab_list.append((tbl.RateTable(models['ra']),'Rates'))
            proxy = ReferencedFilter(self.ref,getattr(tab_list[-1][0].model,self.col))
            tab_list[-1][0].setProxy(proxy)
        if self.ref_type < 2 and 2 not in self.exclude:
            tab_list.append((tbl.JobTable(models['jo']),'Jobs'))
            proxy = ReferencedFilter(
                self.ref,getattr(tab_list[-1][0].model,self.col),
                range(3,models['jo'].columnCount())
                )
            tab_list[-1][0].setProxy(proxy) 

        if self.ref_type < 3 and 3 not in self.exclude:
            tab_list.append((tbl.CallTable(models['ca']),'Calls'))        
            proxy = ReferencedFilter(
                self.ref,getattr(tab_list[-1][0].model,self.col),
                range(4,models['ca'].columnCount())
                )
            tab_list[-1][0].setProxy(proxy)
  
        if self.ref_type == 1 and 4 not in self.exclude:
            tab_list.append((tbl.PayLevelTable(models['pl']),'Pay Levels'))
            proxy = ReferencedFilter(
                self.ref,getattr(tab_list[-1][0].model,self.col)
                )
            tab_list[-1][0].setProxy(proxy)               

        for tab in tab_list:
            self.addTab(tab[0],tab[1])

    def getCol(self):
        if self.ref_type == 0:
            return 'co_col'
        elif self.ref_type == 1:
            return 'r_col'   
        elif self.ref_type == 2:
            return 'j_col'
        elif self.ref_type ==3:
            return 'ca_col'
        else:
            return False        

class GenericEntryTab(QWidget):
    def __init__(self,models,typenum,size=(600,600),parent=None):
        super().__init__(parent)
        self.typenum = typenum
        self.parent = parent
        self.models = models
        self.main_size = (size[0],size[1]*(2/3))
        self.sub_size = (size[0],size[1]*(1/3))
        if typenum == 0:
            self.coSetUp() 
        elif typenum == 1:
            self.rSetUp()
        elif typenum == 2:
            self.jSetUp()
        elif typenum == 3:
            self.caSetUp()               

    def coSetUp(self):
        co_table = tbl.CompanyTable(self.models['co'])
        co_table.setMinimumSize(self.main_size[0],self.main_size[1])
        ref_table_1 = ReferenceView(co_table,self.models)
        ref_table_1.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        analysis = QLabel('Analysis AAG')
        analysis.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        graph = QLabel('Graph AAG')
        graph.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])

        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        sub_layout.addWidget(ref_table_1)
        sub_layout.addWidget(analysis)
        sub_layout.addWidget(graph)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(co_table)
        layout.addWidget(sub_widget)
   
    def rSetUp(self):
        r_table = tbl.RateTable(self.models['ra'])
        r_table.setMinimumSize(self.main_size[0],self.main_size[1])
        ref_table_1 = ReferenceView(r_table,self.models)
        ref_table_1.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        analysis = QLabel('Analysis AAG')
        analysis.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        graph = QLabel('Graph AAG')
        graph.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])

        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        sub_layout.addWidget(ref_table_1)
        sub_layout.addWidget(analysis)
        sub_layout.addWidget(graph)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(r_table)
        layout.addWidget(sub_widget)   

    def jSetUp(self):
        j_table = tbl.JobTable(self.models['jo'])
        j_table.setMinimumSize(self.main_size[0],self.main_size[1])
        ref_table_1 = tbl.CallTable(self.models['ca'])
        proxy = ReferencedFilter(
            j_table,self.models['ca'].j_col,
            range(4,self.models['ca'].columnCount())
            )
        ref_table_1.setProxy(proxy)    
        ref_table_1.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        analysis = QLabel('Analysis AAG')
        analysis.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])
        graph = QLabel('Graph AAG')
        graph.setMinimumSize(self.sub_size[0]/3,self.sub_size[1])

        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        sub_layout.addWidget(ref_table_1)
        sub_layout.addWidget(analysis)
        sub_layout.addWidget(graph)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(j_table)
        layout.addWidget(sub_widget)            

    def caSetUp(self):
        ca_table = tbl.CallTable(self.models['ca'])
        ca_table.setMinimumSize(self.main_size[0],self.main_size[1])
        analysis = QLabel('Analysis AAG')
        analysis.setMinimumSize(self.sub_size[0]/2,self.sub_size[1])
        graph = QLabel('Graph AAG')
        graph.setMinimumSize(self.sub_size[0]/2,self.sub_size[1])

        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)
        sub_layout.addWidget(analysis)
        sub_layout.addWidget(graph)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(ca_table)
        layout.addWidget(sub_widget)            

class Importer(QWidget):
    def __init__(self,path):
        self.path = path
        self.type = path.split('.')[-1]
        self._ids = [0,0,1,0]
        self.id_matrix = {}
        self.orphans = {}
        self.db = self.configDB()
        if self.type == 'json':
            self.decodeJSON()
        else:
            print('FILETYPE NOT SUPPORTED') 
            return None 

    def configDB(self):
        m_format = tbl.getModelSchema()
        db = man.DBManager.setUp('',m_format[0],m_format[1])
        return db

    def decodeJSON(self):
        with open(self.path,'r') as imp_file:
            data = json.load(imp_file)
            for item in data:
                if item['Type'] == 'CO':
                    if item['Tax'] == '1099':
                        stat = 1
                    else:
                        stat = 0    
                    self.encode([
                        self._ids[0],
                        item['Name'],
                        item['Code'],
                        stat,
                        255,255,255
                        ], 'co')
                    self.id_matrix[item['ID']] = self._ids[0]-1    

                    for rate in item['Rates']:                      
                        if rate['Status'] == 'H':
                            stat = 0
                        else:
                            stat = 1
                        self.encode([
                            self._ids[1],
                            rate['Name'],
                            rate['Rate'],
                            rate['Min'],
                            stat,
                            self._ids[0]-1,
                            255,255,255
                        ], 'ra')
                        self.id_matrix[rate['ID']] = self._ids[1]-1

                elif item['Type'] == 'R':
                    self.orphans[item['ID']] = item
                
                elif item['Type'] == 'J':
                    if item['Rate'] in self.orphans.keys():
                        rate = self.orphans[item['Rate']]
                        if rate['Status'] == 'H':
                            stat = 0
                        else:
                            stat = 1
                        self.encode([
                            self._ids[1],
                            rate['Name'],
                            rate['Rate'],
                            rate['Min'],
                            stat,
                            self.id_matrix[item['Co']],
                            255,255,255
                        ],'ra')
                        self.id_matrix[rate['ID']] = self._ids[1]-1
                        del self.orphans[item['Rate']]  
                    self.encode([
                        self._ids[2],
                        item['Name'],
                        self.id_matrix[item['Co']],
                        self.id_matrix[item['Rate']],
                        255,255,255
                    ], 'jo')

                    for call in item['Calls']:
                        date = dt.date(call['Year'],call['Month'],call['Day']).toordinal()
                        if call['PTime']:
                            p_date = date + call['PTime']
                        else:
                            p_date = None

                        self.encode([
                            self._ids[3],
                            date,
                            call['Name'],
                            self.id_matrix[item['Co']],
                            self.id_matrix[item['Rate']],
                            self._ids[2]-1,
                            call['Hrs'][0],
                            0,
                            call['Hrs'][1],
                            0,
                            p_date,
                            255,255,255
                        ],'ca') 
                elif item['Type'] == 'CA':
                    date = dt.date(item['Year'],item['Month'],item['Day']).toordinal()
                    if item['PTime']:
                        p_date = date + item['PTime']
                    else:
                        p_date = None

                    self.encode([
                        self._ids[3],
                        date,
                        item['Name'],
                        self.id_matrix[item['Co']],
                        self.id_matrix[item['Rate']],
                        0,
                        item['Hrs'][0],
                        item['Pay'][0],
                        item['Hrs'][1],
                        item['Pay'][1],
                        p_date,
                        255,255,255
                        ],'ca')       

    def encode(self,data,_type):
        self.db.insert(_type,data)
        if _type == 'co':
            self._ids[0] += 1
        elif _type == 'ra':
            self._ids[1] += 1
        elif _type == 'jo':
            self._ids[2] += 1   
        elif _type == 'ca':
            self._ids[3] += 1                              

    def getSavePath(self):
        save_path = QFileDialog.getSaveFileName(filter='*.db')[0]
        self.db.dbTransfer(to=save_path)        
        return save_path  

if __name__ == '__main__':
    pass             