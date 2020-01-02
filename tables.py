"""
HourMaster Table and Model Classes 

Written with PyQt5 

Mattias Lange McPherson

December 21st, 2019

"""

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random as r
import managers as man
import dialogs as dlg
import datetime as dt
import copy


version = '0.01.01'


#Generic Classes

class GenericTableModel(QAbstractTableModel):

    #General Functions
    def __init__(
        self,header,db,table_name,schema,type_num,sig_manager,
        model_data=None,db_index=None,color_data=None,alpha=127,
        alt_display=None,no_edit=[],parent=None
        ):

        """
        ARGS:
            header: lst of strgs
            db: DBManager Class Instance
            table_name: str
            schema: lst of tuples
            type_num: int; subclass identifier
            sig_manager: signalManager Class Instance
            model_data: lst of lsts
            db_index: lst of unique ints
            color_data: lst of lsts
            c_alpha=int
            alt_display: list of col nums 
            parent: pyqt5 widget
        """

        super().__init__(parent)
        self.db = db
        self.header = header
        self._db_name = table_name
        self._schema = schema
        self.sig = sig_manager
        self.alpha=alpha
        if alt_display and type(alt_display) == dict:
            self.setAltDisplay(alt_display)
        else:
            self._alt_cols = None
            self._alt_display = None    
        self.no_edit = no_edit
        self.col_map = \
            {i-1:self.schema[i][0] for i in range(1,len(self.schema[
                :len(self.header)+1
                ]))}
        self._last_index = -1
        self._type_num = type_num

        self.co_col = None
        self.r_col = None
        self.j_col = None

        if self.sig:
            conns = {
                self.sig.itemDeleted:self.refDeleted,
                self.sig.itemChanged:self.refChanged,
                }
            self.sig.connect(conns)

        if model_data and db_index:
            if len(db_index) == len(data):
                self.model_data = model_data
                self.db_index = db_index
                if color_data:
                    self.color_data = color_data
                else:
                    self.color_data = [
                        [255,255,255] for i in range(len(
                            self.model_data
                        ))
                    ]
        elif model_data:
            print('No Data Provided! Reverting To Empty Model.')

        elif db_index:
            print('No Index Provided! Reverting To Empty Model.')    

        if not model_data or not db_index \
            or len(db_index) != len(model_data):
            self.model_data = []
            self.db_index = []
            self.color_data = []

        self.ref_models = {'co':None,'ra':None,'jo':None,'ca':None,'pl':None}

    @classmethod
    def getSchema(cls):
        temp_model = cls(None)
        return temp_model.db_name,temp_model.schema

    def newEntry(self,row_data,color_data):
        db_index = self.newIndex()
        data = [db_index] + self.dbOrder(row_data)
        self.db.insert(self.db_name,data+color_data)
        

        self.layoutAboutToBeChanged.emit()
        self.db_index.append(db_index)
        self.model_data.append(self.getModelData([[db_index]+row_data])[0])
        self.color_data.append(color_data)
        self.layoutChanged.emit()

    def delEntries(self,rows):
        del_dict = self.mapToDict()
        if type(rows) == int:
            rows = [rows]

        self.beginResetModel()
        
        for row in rows:
            self.beginRemoveRows(QModelIndex(),row,row)
            del del_dict[row]
            self.endRemoveRows()
            self.sig.itemDeletedSig(self.db_index[row],self.typeNum)
            self.db.delete(self.db_name,self.db_index[row])            
        self.mapFromDict(del_dict)
        self.endResetModel()

    def changeColor(self,rgb,rows):
        for row in rows:
            self.color_data[row] = rgb[:3]
            self.db.updateRow(
                self.db_name,self.db_index[row],r=rgb[0],g=rgb[1],b=rgb[2]
            )
            self.sig.itemColorChangedSig(row,self.typeNum)

    def mapToDict(self):
        """
        Maps data lists to row-indexed dictionary
        """

        data_dict = {}
        for row in range(self.rowCount()):
            data_dict[row] = [
                self.db_index[row],
                self.model_data[row],
                self.color_data[row]
                ]
        return data_dict

    def mapFromDict(self,data_dict):
        """
        Unpacks dictionary from mapToDict() into data lists
        """
        self.db_index = []
        self.model_data = []
        self.color_data = []
        raw_data = sorted(data_dict.values(),key=lambda x: x[0])
        for row in range(len(raw_data)):
            self.db_index.append(raw_data[row][0])
            self.model_data.append(raw_data[row][1])
            self.color_data.append(raw_data[row][2]) 

        return True               

    def newIndex(self):
        self._last_index += 1
        return self.lastIndex

    def getDbCol(self,col_num):
        #Expand to generate col_name with non-Db columns in model
        return self.schema[col_num-1][0]

    def dbOrder(self,data):
        db_col_list = [self.schema[i+1][0] for i in range(len(self.schema[1:])-3)]
        matrix = {col:db_col_list.index(self.col_map[col]) \
            for col in self.col_map.keys()}
        ordered_data = [None for i in range(len(matrix))]   
        for key, value in matrix.items():
            ordered_data[value] = data[key]
        return ordered_data    

    def modelOrder(self,data):
        return_data = []
        for row in data:
            no_id = row[1:]
            db_col_list = [self.schema[i+1][0] for i in range(len(self.schema[1:])-3)]
            matrix = {db_col_list.index(self.col_map[col]):col \
                for col in self.col_map.keys()}
            ordered_data = [None for i in range(len(matrix))]    
            for key, value in matrix.items():
                ordered_data[value] = no_id[key]
            return_data.append([row[0]]+ordered_data)
        return return_data            

    def loadData(self):
        db_data = self.db.selectTable(self.db_name)
        self.layoutAboutToBeChanged.emit()
        data = [db_data[row] \
            for row in range(len(db_data))]
        self.db_index = [data[row][0] for row in range(len(data))]
        self.model_data = self.getModelData(self.modelOrder(
            [list(data[row]) for row in range(len(data))]))
        self.color_data = [list(db_data[row][len(db_data[row])-3:]) \
            for row in range(len(db_data))]        
        self.layoutChanged.emit()
        if self.db_index:
            self._last_index=max(self.db_index)

    def padDoubleR(self,flt,_len):
        flt = round(flt,2)           
        flt_lst = str(flt).split('.')
        pad_num = _len - len(flt_lst[1])
        for i in range(pad_num):
            flt_lst[1] = flt_lst[1] + '0'
        return '.'.join(flt_lst)

    def dump(self):
        self.layoutAboutToBeChanged.emit()
        self.db_index = []
        self.model_data = []
        self.color_data = []
        self.layoutChanged.emit()

    def changeDB(self,new_db):
        self.db = new_db

    #Set/Get

    @property
    def db_name(self):
        return self._db_name

    @property
    def schema(self):
        return self._schema

    @property
    def lastIndex(self):
        return self._last_index    

    def setLastIndex(self,i_):
        self._last_index = i_

    @property
    def typeNum(self):
        return self._type_num

    def getAltDisplay(self,col):
        if callable(self._alt_display[col]):
            ids, vals = self._alt_display[col]()
        else:    
            ids, vals = self._alt_display[col]
            if callable(ids):
                ids = ids()[:]
            elif type(ids) == list:
                pass
            else:
                ids = [ids]

            if callable(vals):
                vals = vals()[:]
            elif type(vals) == list:
                pass
            else:
                vals = [vals]
        
        return ids, vals
    
    def setAltDisplay(self,alt_display):
        self._alt_display = alt_display
        self._alt_cols = alt_display.keys()

    def getCoList(self):
        return [
            self.db.getCol(self.cm.db_name,'i'),
            self.db.getCol(self.cm.db_name,self.cm.getDbCol(3))
        ]

    def getRateList(self):
        return [
            self.db.getCol(self.rm.db_name,'i'),
            self.db.getCol(self.rm.db_name,self.rm.getDbCol(2))
        ]  

    def getJobList(self):
        return [
            [0]+self.db.getCol(self.jm.db_name,'i'),
            ['None']+self.db.getCol(self.jm.db_name,self.jm.getDbCol(2))
        ]                    

    def attachRefModel(self,db_name,model):
        if db_name in self.ref_models.keys():
            self.ref_models[db_name] = model

    #Slots
    @pyqtSlot(int,int)
    def refDeleted(self,db_index,type_num):
        if type_num == 0 and self.co_col:
            col = self.co_col
        elif type_num == 1 and self.r_col:
            col = self.r_col
        elif type_num == 2 and self.j_col:
            col = self.j_col     
        else:
            return False       

        del_rows = [row for row in range(self.rowCount()) \
            if self.model_data[row][col] == db_index
            ]
        self.delEntries(del_rows)
   
     #Abstract Methods

    @pyqtSlot(int,int)
    def refChanged(self,db_index,type_num):
        if type_num == self.typeNum:
            #self.reCalc([db_index])
            return True
        elif type_num < self.typeNum:   
            if type_num == 0:
                col = 'co'
            elif type_num == 1:
                col = 'rate'
            elif type_num == 2:
                col = 'job'
            elif type_num == 3:
                return False
            else:
                return False

            if col:
                self.updateEntries(
                    self.db.selectByVal(self.db_name,col,db_index),
                    db_index,
                    type_num    
                )
                return True                

    #Abstract Methods
    def getModelData(self,data_in,load=True):
        if len(data_in) == 0:
            return []
        if len(data_in[0]) == len(self.col_map.keys())+1 or load:
            return [data[1:] for data in data_in]   
        else:
            return_data = [data[1:] for data in data_in]
            extra_vals = [data[self.columnCount():] for data in return_data]
            calc_col = []
            for i in range(self.columnCount()):
                if i not in self.col_map.keys():
                    calc_col.append(i)

            for data in return_data:
                i=0
                j=0
                for col in calc_col:
                    data[col] = extra_vals[j][i]
                    i += 1                    
                del data[self.columnCount():]
                j += 1    
            return return_data

    def reCalc(self,ids):
        new_data =  self.getModelData(
            self.modelOrder(
                self.db.getRows(self.db_name,ids)
            )
        )

        if new_data:
            i = 0
            for _id in ids:
                row = self.db_index.index(_id)
                self.model_data[row] = new_data[i]
                i += 1  
                self.dataChanged.emit(
                    self.index(row,0),
                    self.index(row,self.columnCount())
                    )

        return True

    def updateEntries(self,update_ids,rownum,typenum):
        pass

    #Implemented Abstract Methods
    def rowCount(self,parent=None):
        return len(self.model_data)

    def columnCount(self,parent=None):
        if self.rowCount() == 0:
            return 0
        else:    
            return len(self.model_data[0])  

    def data(self,index,role):
        if not index.isValid():
            return None

        elif role == Qt.BackgroundRole:
            rgb = self.color_data[index.row()]
            return QBrush(QColor(rgb[0],rgb[1],rgb[2],self.alpha))

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.DisplayRole:
            if self._alt_cols:
                if index.column() in self._alt_cols:
                    row = index.row()
                    col = index.column()
                    alt_ids, alt_vals = \
                        self.getAltDisplay(index.column())  
                    try:     
                        raw = alt_ids.index(
                            self.model_data[index.row()][index.column()]
                            )
                    except ValueError:
                        return 'DATA ERROR'        
                    return alt_vals[raw]
                else:
                    return self.model_data[index.row()][index.column()]     
            else:
                return self.model_data[index.row()][index.column()]               

        elif role == Qt.EditRole:
            return self.model_data[index.row()][index.column()] 

    def setData(self,index,value,role):
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            if value == '':
                pass
            else:  
                self.model_data[index.row()][index.column()] = value
                if index.column() in self.col_map.keys():
                    self.db.update(
                        self.db_name,self.db_index[index.row()],
                        value,self.col_map[index.column()],True
                        )
        self.dataChanged.emit(index,index)

        return True

    def flags(self,index):
        if not index.isValid():
            return Qt.NoItemFlags
        
        if index.column() not in self.no_edit:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable 
        else:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled    

    def headerData(self,col,orientation,role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return col+1  

class GenericTableView(QTableView):

    def __init__(self,model,parent=None):
        super().__init__(parent)
        self.model = model
        self.config()

    def config(self):
        self.setDelegates(self.delegates())

        self.proxy = GenericSortFilterProxy(self)
        self.proxy.setSourceModel(self.model)
        self.setModel(self.proxy)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
            )

        self.setSortingEnabled(True)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive) 

    def setDelegates(self,delegate_lst):    
        if delegate_lst:
            for col, type_ in delegate_lst:
                self.setItemDelegateForColumn(col,type_)
        else:
            return False    

    def new(self):
        self.new_dialog = self.dialogs()[0]           

    def delRows(self):
        rows = set(self.getSelRows())
        self.model.delEntries(rows)
        return rows

    def getSelRows(self):
        sel_list = set([])
        for index in self.selectedIndexes():
            sel_list.add(self.proxy.mapToSource(index).row())
        return tuple(sel_list)  

    def getSelIDs(self):
        ids = set([])
        for index in self.selectedIndexes():
            ids.add(self.proxy.sourceModel().db_index[self.proxy.mapToSource(index).row()])
        return tuple(ids)    
          
    def colorChange(self,QColor):
        self.model.changeColor(QColor.getRgb(),self.getSelRows()) 

    def setProxy(self,proxy):
        proxy.setSourceModel(self.proxy.sourceModel())
        self.setModel(proxy)
        self.proxy = proxy   

    def filterCols(self,col_list):
        if hasattr(self.proxy,'col_exclude'):
            self.proxy.col_exclude = col_list
            self.proxy.invalidateFilter()

    def typenum(self):
        return self.model.typeNum

    #Implemented Abstract Methods

    def contextMenuSetup(self,event):
        menu = QMenu(self)
        add_action = menu.addAction('New')
        del_action = menu.addAction('Delete')
        color_action = menu.addAction('Color')
        return menu
    
    def contextMenuEvent(self,event):
        menu = self.contextMenuSetup(event)
        self.contextMenuExec(event,menu)

    def contextMenuExec(self,event,menu):
        options = menu.actions()
        action = menu.exec_(self.mapToGlobal(event.pos()))

        #add_action
        if action == options[0]:
            self.new()

        #color_action
        elif action == options[2]:
            if not self.getSelRows():
                pass
            else:    
                picker = QColorDialog(self)
                picker.move(self.mapToGlobal(event.pos()))
                picker.colorSelected.connect(self.colorChange)
                picker.show() 

        #del_action
        elif action == options[1]:
            self.delRows() 

        return action, options 

    #Abstract Methods
    def dialogs(self):
        #0:New
        return [False]

    def delegates(self):
        return False

    def setAltVals(self):
        return False

    @classmethod
    def tableModel(cls):
        return False    

class ComboDelegate(QItemDelegate):
    def __init__(self,ids_or_func,col,parent=None):
        super().__init__(parent)
        self.ids_or_func = ids_or_func
        self.col = col
        self.int_ids = None
        self.changed = False

    def selChanged(self,i):
        self.changed = True

    def createEditor(self,parent,option,index):
        self.model = index.model()
        self.original_value = self.model.data(index,Qt.EditRole)
        try:
            cb = QComboBox(parent)
            cb.addItems(index.model().sourceModel().\
                getAltDisplay(index.column())[1])
        except KeyError:
                print(KeyError)

        return cb        

    def setEditorData(self,combo,index):
        col_value = index.model().data(index,Qt.EditRole)
        combo_index = index.model().sourceModel().\
                getAltDisplay(index.column())[0].index(col_value)
        combo.setCurrentIndex(combo_index)

    def setModelData(self,combo,model,index,emit_flag=True):
        self.getIDs(combo)  
        model.setData(index,self.int_ids[combo.currentIndex()],Qt.EditRole)
        if emit_flag:
            source = model.sourceModel()
            source_index = model.mapToSource(index)
            source.sig.itemChangedSig(
                source.db_index[source_index.row()],
                source.typeNum,
                )

    def getIDs(self,combo):
        ci = combo.currentIndex()
        if self.int_ids:
            pass
        elif type(self.ids_or_func) == list:
            self.int_ids = self.ids_or_func
        else:    
            self.int_ids = self.ids_or_func(self.col)[0]         

    def updateEditorGeometry(self,combo,option,index):
        combo.setGeometry(option.rect)

class DoubleSpinBoxDelegate(QItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)

    def createEditor(self,parent,option,index):
        try:
            sb = QDoubleSpinBox(parent)
            sb.setRange(0,10000)
        except KeyError:
                print(KeyError)

        return sb 

    def setEditorData(self,spin,index):
        spin_val = index.model().data(index,Qt.EditRole)
        spin.setValue(spin_val)

    def setModelData(self,spin,model,index):
        model.setData(index,spin.value(),Qt.EditRole)
        source = model.sourceModel()
        source_index = model.mapToSource(index)
        source.sig.itemChangedSig(source.db_index[source_index.row()],source.typeNum) 

    def updateEditorGeometry(self,spin,option,index):
        spin.setGeometry(option.rect)

class DateEditDelegate(QItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)

    def createEditor(self,parent,option,index):
        de = QDateEdit(parent)
        return de    

    def setEditorData(self,date_edit,index):
        date_edit.setDisplayFormat('MM/dd/yy')
        try:
            self.date = [index.model().data(index,Qt.EditRole)].copy()[0]
            if not self.date:
                self.date = dt.date.today().toordinal()
        except TypeError as e:
            self.date = dt.date.today().toordinal()    
        date_edit.setDate(dt.date.fromordinal(self.date))

    def setModelData(self,date_edit,model,index):
        model.setData(index,date_edit.date().toPyDate().toordinal(),Qt.EditRole)
        source = model.sourceModel()
        source_index = model.mapToSource(index)
        source.sig.dateChangedSig(source.db_index[source_index.row()],source.typeNum,self.date,index.column()) 

    def updateEditorGeometry(self,date_edit,option,index):
        date_edit.setGeometry(option.rect)    

class AdaptiveCoCombo(ComboDelegate):
    def __init__(self,db,ids_or_func,col,parent=None):
        super().__init__(ids_or_func,col,parent)
        self.db = db
    
    def createEditor(self, parent, option, index):
        cb = super().createEditor(parent, option, index)
        cb.currentIndexChanged.connect(self.selChanged)
        return cb

    def setModelData(self, combo, model, index):

        self.getIDs(combo)

        if self.changed:
            rates = self.db.selectByVal(
                model.sourceModel().rm.db_name,
                'co',
                self.int_ids[combo.currentIndex()]
            )
            if not rates:
                co_message = QMessageBox()
                co_message.setIcon(QMessageBox.Warning)
                co_message.setText('Company Has No Rates')
                co_message.setWindowTitle('No Rates')
                co_message.setStandardButtons(QMessageBox.Ok)
                val = co_message.exec_()
                model.setData(index,self.original_value)
            else:
                r_index = model.index(index.row(),model.sourceModel().r_col)
                j_index = model.index(index.row(),model.sourceModel().j_col)
                j_id = model.sourceModel().data(j_index,Qt.EditRole)
                model.setData(r_index,rates[0]) 
                model.setData(j_index,0)
                model.sourceModel().jm.reSum(j_id,2)

            super().setModelData(combo, model, index)                 

class AdaptiveRCombo(ComboDelegate):
    def __init__(self,db,col,parent=None):
        super().__init__(None,col,parent)
        self.db = db

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.currentIndexChanged.connect(self.selChanged)
        self.populate(cb,index)
        return cb  

    def populate(self,cb,index):
        co_m_index = index.model().index(index.row(),index.model().sourceModel().co_col)
        co_id = index.model().data(co_m_index,Qt.EditRole)
        self.int_ids = self.db.selectByVal('ra','co',co_id)
        self.rate_names = self.db.getVals('ra',self.int_ids,'name')
        cb.addItems(self.rate_names)

    def setModelData(self, combo, model, index):
        if self.changed:
            j_index = model.index(index.row(),model.sourceModel().j_col)
            j_id = model.sourceModel().data(j_index,Qt.EditRole)
            model.setData(j_index,0)
            model.sourceModel().jm.reSum(j_id,2)
        super().setModelData(combo,model,index)            

class AdaptiveJCombo(ComboDelegate):
    def __init__(self,db,col,parent=None):
        super().__init__(None,col,parent)
        self.db = db

    def setEditorData(self, combo, index):
        if index.model().data(index,Qt.EditRole) != 0:
            self.prev_val = index.model().data(index,Qt.EditRole)
            super().setEditorData(combo,index)
        else:
            combo.setCurrentIndex(0)
            self.prev_val = 0 

    def createEditor(self, parent, option, index):
        cb = QComboBox(parent)
        cb.currentIndexChanged.connect(self.selChanged)
        self.populate(cb,index)
        return cb  

    def populate(self,cb,index):
        co_m_index = index.model().index(index.row(),index.model().sourceModel().co_col)
        co_id = index.model().data(co_m_index,Qt.EditRole)  

        r_m_index = index.model().index(index.row(),index.model().sourceModel().r_col)
        r_id = index.model().data(r_m_index,Qt.EditRole)

        self.int_ids = \
            [0] + self.db.selectByVals('jo',co=co_id,rate=r_id)    
        self.job_names = ['None'] + self.db.getVals('jo',self.int_ids,'name')
        del self.job_names[1]
        cb.addItems(self.job_names)    
                              
    def setModelData(self,combo,model,index):
        prev = self.prev_val

        super().setModelData(combo,model,index,emit_flag=False)
    
        if self.changed and prev != self.int_ids[combo.currentIndex()]:
            model.sourceModel().jm.reSum(prev,2)
            model.sourceModel().jm.reSum(self.int_ids[combo.currentIndex()],2)

class HourSpinDelegate(DoubleSpinBoxDelegate):
    def __init__(self,mode,parent=None):
        super().__init__(parent)
        self.mode = mode

    def setEditorData(self,spin,index):
        self.call_num = index.model().sourceModel().db_index[index.row()]
        self.spin_val = index.model().data(index,Qt.EditRole) 
        spin.setValue(self.spin_val) 

    def setModelData(self,spin,model,index):
        if self.mode == 0:
            s_off = spin.value()-self.spin_val
            a_off = 0
        elif self.mode == 1: 
            s_off = 0
            a_off = spin.value()-self.spin_val             
        model.setData(index,spin.value(),Qt.EditRole)   
        source = model.sourceModel()
        source_index = model.mapToSource(index)
        source.sig.hrsChangedSig(
            source.db_index[source_index.row()],source.typeNum,s_off,a_off
            )

class GenericSortFilterProxy(QSortFilterProxyModel):
    def __init__(self,parent=None):
        super().__init__(parent)

    def lessThan(self,left,right):
        left_val = self.sourceModel().data(left,Qt.EditRole)
        right_val = self.sourceModel().data(right,Qt.EditRole)

        if left_val == None and right_val == None:
            return False
        else:    
            return left_val > right_val  
        
#Subclassed Widgets
class CompanyModel(GenericTableModel):
    def __init__(self,db,sig_man=None,parent=None):
        header = ['Name','Short','Class.']
        db_name = 'co'
        schema = [
            ('i','INTEGER','PRIMARY KEY'),('name','TEXT'),('short','TEXT'),
            ('stat','INTEGER'),('r','INTEGER'),('g','INTEGER'),('b','INTEGER')
            ]
        alpha=127
        type_num = 0

        super().__init__(
            header,db,db_name,schema,type_num,sig_man,
            alpha=alpha,alt_display=None,parent=parent
           ) 

        self.setAltDisplay({2:[[0,1],['W2','1099']]})
             
class CompanyTable(GenericTableView):
    def __init__(self,model,parent=None):
        super().__init__(model,parent)

    #Implemented Abstract Methods

    def dialogs(self):
        return [dlg.NewCompanyDialog(self.model)]
    
    def delegates(self):
        return [[2,ComboDelegate(self.model.getAltDisplay,2,self)]]

class RateModel(GenericTableModel):
    def __init__(self,db,co_model=None,sig_man=None,parent=None):
        header = ['Name','Co','Rate','Min','Status']
        db_name = 'ra'
        schema = [
            ('i','INTEGER','PRIMARY KEY'),('name','TEXT'),
            ('rate','FLOAT'),('min','FLOAT'),('stat','INTEGER'),
            ('co','INTEGER','FOREIGN KEY', 'co(i)'),('r','INTEGER'),
            ('g','INTEGER'),('b','INTEGER')
            ]
        alpha = 127
        type_num = 1

        super().__init__(
            header,db,db_name,schema,type_num,sig_man,
            alpha=alpha,alt_display=None,parent=parent
        ) 

        self.cm = co_model
        self.co_col = 1 

        self.setAltDisplay({
            self.co_col:self.getCoList,
            4:[[0,1],['Hourly','Flat']]
        })

        self.col_map = {
            0:self.schema[1][0],
            1:self.schema[5][0],
            2:self.schema[2][0],
            3:self.schema[3][0],
            4:self.schema[4][0]
        }

        if self.sig:
            connect = {
                self.sig.addRaise:self.addRaise
            }

            self.sig.connect(connect)

    def getCoData(self,index):
        return self.db.getRow(cm.db_name,index)

    #Extended Parent Class Methods
    def data(self,index,role):
        if role == Qt.DisplayRole and index.column() in [2,3]:
            
            if index.column() == 2:
                val = self.padDoubleR(
                self.model_data[index.row()][index.column()],2
                )
                return '$' + val
            elif index.column() == 3:
                val = str(self.model_data[index.row()][index.column()]) \
                    .strip('0').strip('.')
                if val == '':
                    return '0 hrs'
                else:    
                    return val + ' hrs'
        else:
            return super().data(index,role)   

    def addRaise(self,rate,date,old_level,level,colors):
        index = self.index(self.db_index.index(rate),2)
        self.setData(index,level,Qt.EditRole)

class RateTable(GenericTableView):
    def __init__(self,model,parent=None):
        super().__init__(model,parent)
        
    #Abstract Methods
    def dialogs(self):
        return [dlg.NewRateDialog(self.model)]

    def delegates(self):
        return [
            [
                self.model.co_col,
                ComboDelegate(self.model.getAltDisplay,self.model.co_col,self)
            ],
            [2,DoubleSpinBoxDelegate(self)],
            [3,DoubleSpinBoxDelegate(self)],
            [4,ComboDelegate(self.model.getAltDisplay(4)[0],self)]
            ]               
      
    def contextMenuEvent(self, event):
        menu = self.contextMenuSetup(event)
        menu.addAction('Add Raise')
        action, options = self.contextMenuExec(event,menu)

        #add_raise
        if action == options[3]:
            if not self.getSelIDs():
                pass
            else:
                self.addRaise(self.getSelIDs()[0])

    def addRaise(self,rate_id):
        self.raise_dlg = dlg.AddRaiseDialog(rate_id,self.model)

class JobModel(GenericTableModel):
    def __init__(
        self,db,co_model=None,r_model=None,
        sig_man=None,pay_man=None,parent=None
    ):
        header = ['Name','Co','Rate','Sched.','Pay','Act.','Pay']
        db_name = 'jo'
        schema = [
            ('i','INTEGER','PRIMARY KEY'),('name','TEXT'),
            ('co','INTEGER','FORIEGN KEY', 'co(i)'),
            ('rate','INTEGER','FORIEGN KEY','ra(i)'),
            ('r','INTEGER'),('g','INTEGER'),('b','INTEGER')
        ]
        alpha = 127
        type_num = 2
        no_edit = [1,2,3,4,5,6]

        super().__init__(
            header,db,db_name,schema,type_num,sig_man,
            alpha=alpha,alt_display=None,no_edit=no_edit,parent=parent
        )

        self.setLastIndex(0)

        self.pm = pay_man

        if co_model and r_model:
            self.cm = co_model
            self.rm = r_model

        self.co_col = 1
        self.r_col = 2

        self.setAltDisplay({
            self.co_col:self.getCoList,
            self.r_col:self.getRateList
        })   

        self.col_map = {
            0:self.schema[1][0],
            1:self.schema[2][0],
            2:self.schema[3][0],
        }

        if self.sig:
            connect = {
                self.sig.payChanged:self.updatePay,
                self.sig.hrsChanged:self.updateHrs,
                self.sig.resum:self.reSum
            } 

            self.sig.connect(connect)

    def data(self,index,role):
        if role == Qt.DisplayRole: 

            if index.column() in [4,6]:
                val = self.model_data[index.row()][index.column()]
                if val == 0:
                    return '$ 0.00'
                else:    
                    return '$' + self.padDoubleR(val,2)
            elif index.column() in [3,5]:
                val = self.model_data[index.row()][index.column()]
                return str(val) + ' hrs'
            else:
                return super().data(index,role)    
        else:
            return super().data(index,role)      

    def getModelData(self,data_in):
        return_data = []
        for row in data_in:
            hrs = self.pm.sumHrs(row[0],self.typeNum)
            pay = self.pm.sumPay(row[0],self.typeNum)
            return_data.append(list(row) + [hrs[0],pay[0],hrs[1],pay[1]])
        return super().getModelData(return_data)    
    
    def reCalc(self,rows):
        return False

    @pyqtSlot(int,int,float,float)
    def updatePay(self,rownum,typenum,s_offset,a_offset):
        if typenum == 3:
            job_id = self.db.getVal('ca',rownum,'job')
        elif typenum == 2:
            job_id = rownum
        else:
            return None      

        if job_id == 0:
            return None

        row_num = self.db_index.index(job_id)
        s_index = self.index(row_num,4)
        a_index = self.index(row_num,6)   

        self.setData(s_index,round(self.data(s_index,Qt.EditRole)+s_offset,2),Qt.EditRole)
        self.setData(a_index,round(self.data(a_index,Qt.EditRole)+a_offset,2),Qt.EditRole)

    @pyqtSlot(int,int,float,float)
    def updateHrs(self,rownum,typenum,s_offset,a_offset):
        if typenum == 3:
            job_id = self.pm.getCallData(rownum)['job']
            if job_id == 0:
                return None
            row_num = self.db_index.index(job_id)
            s_index = self.index(row_num,3)
            a_index = self.index(row_num,5)
            self.setData(s_index,self.data(s_index,Qt.EditRole)+s_offset,Qt.EditRole)
            self.setData(a_index,self.data(a_index,Qt.EditRole)+a_offset,Qt.EditRole)
            self.sig.hrsChangedSig(job_id,2,s_offset,a_offset)

    def updateEntries(self,update_ids,rownum,typenum):
        if typenum == 1:
            for _id in update_ids:
                if self.db.getVal(self.db_name,_id,'co') != \
                    self.db.getVal(self.rm.db_name,rownum,'co'):
                    self.setData(
                        self.index(self.db_index.index(_id),self.co_col),
                        self.db.getVal(self.rm.db_name,rownum,'co'),
                        Qt.EditRole
                        )
        else:
            super().updateEntries(update_ids,rownum,typenum)            

    def reSum(self,job_id,typenum):
        if job_id != 0 and typenum == 2:
            hrs = self.pm.sumHrs(job_id,self.typeNum)
            pay = self.pm.sumPay(job_id,self.typeNum)
            row_num = self.db_index.index(job_id)

            s_hrs_index = self.index(row_num,3)
            s_pay_index = self.index(row_num,4)
            a_hrs_index = self.index(row_num,5)
            a_pay_index = self.index(row_num,6)

            self.setData(s_hrs_index,hrs[0],Qt.EditRole)
            self.setData(s_pay_index,pay[0],Qt.EditRole)
            self.setData(a_hrs_index,hrs[1],Qt.EditRole)
            self.setData(a_pay_index,pay[1],Qt.EditRole)

class JobTable(GenericTableView):
    def __init__(self,model,parent=None):
        super().__init__(model,parent)

    def dialogs(self):
        return [dlg.NewJobDialog(self.model)] 

    def delegates(self):
        return []

class CallModel(GenericTableModel):
    def __init__(
        self,db,co_model=None,r_model=None,j_model=None,
        sig_man=None,pay_man=None,parent=None
    ):

        header = ['Date','Name','Co','Rate','Job','Sched','Pay','Act.','Pay','Pay Date','Pay Time']
        db_name = 'ca'
        schema = [
            ('i','INTEGER','PRIMARY KEY'),('date','INTEGER','INDEX'),
            ('name','TEXT'),('co','INTEGER','FORIEGN KEY', 'co(i)'),
            ('rate','INTEGER','FORIEGN KEY','ra(i)'),
            ('job','INTEGER','FORIEGN KEY','jo(i)'),
            ('sched','FLOAT'),('s_pay','FLOAT'),('act','FLOAT'),('a_pay','FLOAT'),
            ('pdate','INTEGER','INDEX'),
            ('r','INTEGER'),('g','INTEGER'),('b','INTEGER')
        ]
        alpha = 127
        type_num = 3
        no_edit = [6,8,10]        
        
        super().__init__(
            header,db,db_name,schema,type_num,sig_man,
            alpha=alpha,alt_display=None,no_edit=no_edit,parent=parent
        )

        self.pm = pay_man
        if co_model and r_model and j_model:
            self.cm = co_model
            self.rm = r_model
            self.jm = j_model

        self.co_col = 2
        self.r_col = 3
        self.j_col = 4
        self.date_col = 0
        self.pdate_col = 9

        self.setAltDisplay({
            self.co_col:self.getCoList,
            self.r_col:self.getRateList,
            self.j_col:self.getJobList
        }) 

        self.col_map = {
            0:self.schema[1][0],
            1:self.schema[2][0],
            2:self.schema[3][0],
            3:self.schema[4][0],
            4:self.schema[5][0],
            5:self.schema[6][0],
            6:self.schema[7][0],
            7:self.schema[8][0],
            8:self.schema[9][0],
            9:self.schema[10][0]
        }  

        if self.sig:
            connect = {
                self.sig.payChanged:self.updatePay,
                self.sig.dateChanged:self.pdateChanged,
            }    

            self.sig.connect(connect)

    def newEntry(self,row_data,color_data):
        super().newEntry(row_data+[None], color_data)
        self.pm.updateCall(self.db_index[-1])
        self.sig.hrsChangedSig(
            self.db_index[-1],self.typeNum,row_data[5],row_data[7]
            )

    def delEntries(self,rows):
        for row in rows:            
            self.sig.hrsChangedSig(
               self.db_index[row],self.typeNum,-self.model_data[row][5],
                -self.model_data[row][7]
            )
        super().delEntries(rows)

    def data(self,index,role):
        if role == Qt.DisplayRole: 
            if index.column() == self.date_col or index.column() == self.pdate_col:
                if self.model_data[index.row()][index.column()] == None:
                    return 'None'
                return dt.date.fromordinal(self.model_data[index.row()][index.column()]).strftime('%m/%d/%y')
            elif index.column() == self.j_col and self.model_data[index.row()][self.j_col] == 0:
                return 'None'
            elif index.column() in [6,8]:
                val = self.model_data[index.row()][index.column()]
                if val == 0:
                    return '$ 0.00'
                else:
                    self.padDoubleR(val,2)    
                    return '$' + self.padDoubleR(val,2)
            elif index.column() in [5,7]:
                val = self.model_data[index.row()][index.column()]
                return str(val) + ' hrs'
            else:
                return super().data(index,role)    
        else:
            return super().data(index,role)    

    def updateEntries(self,update_ids,rownum,typenum):
        if typenum == 1:
            for _id in update_ids:
                if self.db.getVal(self.db_name,_id,'co') != \
                    self.db.getVal(self.rm.db_name,rownum,'co'):
                    self.setData(
                        self.index(self.db_index.index(_id),self.co_col),
                        self.db.getVal(self.rm.db_name,rownum,'co'),
                        Qt.EditRole
                        )
        elif typenum == 2:
            for _id in update_ids:
                if self.db.getVal(self.db_name,_id,'co') != \
                    self.db.getVal(self.jm.db_name,rownum,'co'):
                    self.setData(
                        self.index(self.db_index.index(_id),self.co_col),
                        self.db.getVal(self.jm.db_name,rownum,'co'),
                        Qt.EditRole
                    )

                if self.db.getVal(self.db_name,_id,'rate') != \
                    self.db.getVal(self.jm.db_name,rownum,'rate'):
                    self.setData(
                        self.index(self.db_index.index(_id),self.rate_col),
                        self.db.getVal(self.jm.db_name,rownum,'rate'),
                        Qt.EditRole
                    )                    

            super().updateEntries(update_ids,rownum,typenum)                                       

    def getModelData(self,data_in,load=True):
        return_data = []
        for row in data_in:
            if row[self.pdate_col+1] == None:
                p_time = None
            else:    
                p_time = max(
                    row[self.pdate_col+1]-row[self.date_col+1],
                    0
                )   
            return_data.append(list(row)+[p_time])    
        return super().getModelData(return_data,load)    

    def setData(self,index,value,role):
        original_val = self.data(index,Qt.EditRole)

        return_val = super().setData(index,value,role)

        if index.column() == self.j_col:
            self.sig.jobChangedSig(
                self.db_index[index.row()],
                self.typeNum,
                original_val
                )

        return True       

    def setPDate(self,row,date):
        self.setData(self.index(row,self.pdate_col),date,Qt.EditRole)
        self.pdateChanged(self.db_index[row],3,None,self.pdate_col)

    @pyqtSlot(int,int,float,float)
    def updatePay(self,rownum,typenum,s_off,a_off):
        if typenum == 3:
            row = self.db_index.index(rownum)
            self.layoutAboutToBeChanged.emit()
            self.model_data[row][6] += s_off
            self.model_data[row][8] += a_off 
            self.layoutChanged.emit()

    @pyqtSlot(int,int,int,int)    
    def pdateChanged(self,rownum,typenum,o_date,model_col):
        if typenum == 3:
            row = self.db_index.index(rownum)
            if not self.model_data[row][self.pdate_col]:
                return False
            index = self.index(self.db_index.index(rownum),self.pdate_col+1)
            date = max(self.model_data[row][self.pdate_col] - self.model_data[row][self.date_col],0)
            self.setData(index,date,Qt.EditRole)

class CallTable(GenericTableView):
    def __init__(self,model,parent=None):
        super().__init__(model,parent)

    def dialogs(self):
        return [dlg.NewCallDialog(self.model)]

    def delegates(self):
        return [
            [self.model.date_col,DateEditDelegate(self)],
            [
                self.model.co_col,
                AdaptiveCoCombo(
                    self.model.db,self.model.getAltDisplay,self.model.co_col,self
                ),                
            ],
            [
                self.model.r_col,
                AdaptiveRCombo(
                    self.model.db,self.model.r_col,self
                )
            ],
            [
                self.model.j_col,
                AdaptiveJCombo(
                    self.model.db,self.model.j_col,self
                )
            ], 
            [7,HourSpinDelegate(1,self)],
            [5,HourSpinDelegate(0,self)],
            [self.model.pdate_col,DateEditDelegate(self)],           
        ]                            

    def contextMenuEvent(self,event):
        menu = self.contextMenuSetup(event)
        menu.addAction('Set Pay Date')
        menu.addAction('Clear Date')
        action, options = self.contextMenuExec(event,menu)

        if action == options[3]:
            self.setPDates(event)
        elif action == options[4]:
            self.clearPDates()           

    @pyqtSlot()
    def clearPDates(self):
        if self.getSelRows():
            rows = set(self.getSelRows())
            for row in rows:
                index = self.model.createIndex(row,self.model.pdate_col)
                self.model.setData(index,None,Qt.EditRole)
                self.model.reCalc([row])    

    @pyqtSlot()
    def setPDates(self,event):
        if self.getSelRows():
            pos = self.mapToGlobal(event.pos())
            date_edit = dlg.DateEdit(pos.x(),pos.y(),self)
            if date_edit.exec_():
                date = date_edit.date.date().toPyDate().toordinal()
                for row in self.getSelRows():
                    self.model.setPDate(row,date)
       
class PayLevelModel(GenericTableModel):
    def __init__(
        self,db,r_model=None,sig_man=None,pay_man=None,parent=None        
    ):

        header = ['Rate','Level','Date']
        db_name = 'pl'
        schema = [
            ('i','INTEGER','PRIMARY KEY'),('rate','INTEGER','INDEX'),
            ('level','FLOAT'),('date','INTEGER'),
            ('r','INTEGER'),('g','INTEGER'),('b','INTEGER')
        ]

        alpha = 127
        type_num = 4 
        no_edit = [0]     
        
        super().__init__(
            header,db,db_name,schema,type_num,sig_man,
            alpha=alpha,alt_display=None,no_edit=no_edit,parent=parent
        )    

        if pay_man:
            self.pm = pay_man
        if r_model:
            self.rm = r_model    

        self.r_col = 0
        self.date_col = 2

        self.setAltDisplay({
            self.r_col:self.getRateList
        })

        if self.sig:
            connect = {
                self.sig.addRaise:self.addRaise
            }
            self.sig.connect(connect)

    def data(self,index,role):
        if role == Qt.DisplayRole:
            if index.column() == self.date_col:
                if self.model_data[index.row()][index.column()] == None:
                    return ''
                return dt.date.fromordinal(int(self.model_data[index.row()][index.column()])).strftime('%m/%d/%y')
            elif index.column() == 1:
                return '$' + self.padDoubleR(self.model_data[index.row()][index.column()],2)   
            else:
                return super().data(index,role)    
        else:
            return super().data(index,role)        

    def setData(self,index,value,role):
        return_val = super().setData(index,value,role)
        self.sig.paylevelChangedSig(
            self.model_data[index.row()][self.r_col],
            self.model_data[index.row()][self.date_col],
            self.model_data[index.row()][1],
            self.db_index[index.row()]
            )
        return return_val    

    def getModelData(self,data_in,load=True):
        for row in data_in:
            self.pm.updateTimeline(
                row[self.r_col+1],
                row[self.date_col+1],
                row[2],
                row[0]
                )
        return super().getModelData(data_in,load=load)

    def addRaise(self,rate,date,old_level,level,colors):
        if rate not in self.pm.timelines.keys():
            self.newEntry([rate,old_level,dt.date(1901,1,1).toordinal()],colors) 
        self.newEntry([rate,level,date],colors)

class PayLevelTable(GenericTableView):
    def __init__(self,model,parent=None):
        super().__init__(model,parent)

    def dialogs(self):
        return [dlg.NewPayLevelDialog(self.model)]

    def delegates(self):
        return [
            [0,ComboDelegate(self.model.getAltDisplay,0,self)],
            [1,DoubleSpinBoxDelegate(self)],
            [self.model.date_col,DateEditDelegate(self)],
            ]        

def getModelSchema():
    t_names = [
        CompanyModel.getSchema()[0],
        RateModel.getSchema()[0],
        JobModel.getSchema()[0],
        CallModel.getSchema()[0],
        PayLevelModel.getSchema()[0],
    ]
    schema = [
        CompanyModel.getSchema()[1],
        RateModel.getSchema()[1],
        JobModel.getSchema()[1],
        CallModel.getSchema()[1],
        PayLevelModel.getSchema()[1],
    ]
    return t_names,schema

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    db_names,schema = getModelSchema()
    db = man.DBManager('test')
    sig_man = man.sigManager()
    co_model = CompanyModel(db,sig_man)
    co_model.loadData()
    r_model = RateModel(db,co_model,sig_man)
    r_model.loadData()
    win = RateTable(r_model)
    app.exec_()

