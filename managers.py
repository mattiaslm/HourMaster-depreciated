"""
HourMaster Manager Classes

Written w/ PyQt5

Mattias Lange McPherson

December 30th, 2019

"""

import sqlite3 as sq
import os
from PyQt5.QtCore import *
import inspect
import datetime as dt
import timeit


#dbManager
db_path = os.path.dirname(__file__)+'\db\\'

class DBManager():

    def __init__(self,db_path):
        if db_path:
            self.conn,self.cur = self.connect(db_path)
            self.path = db_path
        else:
            self.conn,self.cur = self.connect(':memory:')
            self.path = ':memory:'

    @classmethod
    def setUp(cls,db_name,t_names,schemas):
        db = cls(db_name)
        if len(t_names) == len(schemas):
            cur_lst_pos = 0
            for tbl in t_names:
                db.createTable(tbl,schemas[cur_lst_pos])
                cur_lst_pos += 1
        return db        

    @classmethod
    def fromConn(cls,conn,cur):
        db_manager = cls('')
        db_manager.conn = conn
        db_manager.cur = cur
        return db_manager
        
    def connect(self,db_path):
        try:
            conn = sq.connect(db_path)
            cur = conn.cursor()
            return conn,cur
        except sq.Error as e:
            print(e)

    def execute(self,sql_string):
        try:
            self.cur.execute(sql_string)
        except sq.Error as e:
            print(e)

    def stringify(self,val):
        if val == None:
            return 'null'
        if type(val) == str:
            return "'%s'" %val
        else:
            return str(val)

    def createTable(self,t_name,schema):
        col_list = []
        fk_list = []
        i_list = []

        for col in schema:
            if len(col) > 3:
                col_list.append(str(' '.join(col[:2])))
                if col[2][0] == 'F':
                    fk_list.append('FOREIGN KEY (%s) REFERENCES %s' %(col[0],col[3]))
            elif len(col) == 3 and col[2][0] == 'I':
                col_list.append(str(' '.join(col[:2])))
                i_list.append(
                    'CREATE INDEX "%s-%s" ON %s (%s)'
                    %(t_name,col[0],t_name,col[0])
                    )
            else:
                col_list.append(str(' '.join(col)))

        col_string = '(' + ','.join(col_list+fk_list) + ')'
        sql_string = 'CREATE TABLE %s %s' %(t_name,col_string)
        self.execute(sql_string)

        #Create Indexes
        for index in i_list:
            self.execute(index)   

    def expandTable(self,t_name,col_name,col_def,fk=None):
        sql_string = 'ALTER TABLE %s ADD %s %s' %(t_name,col_name,col_def)
        if fk:
            sql_string.append('FORIEGN KEY '+fk)
        self.execute(sql_string)
 
    def deleteTable(self,t_name):
        sql_string = 'DROP TABLE ' + t_name
        self.execute(sql_string)

    def insert(self,t_name,ins_data,cols='All'):
        if cols == 'All':
            col_string = ''
        else:    
            cols = [self.stringify(col) for col in cols]
            col_string = '(' + ','.join(cols) + ')'

        if len(ins_data) != len(cols) and cols != 'All':
            print('Mismatched # of cols and data')

        for i in range(len(ins_data)):
            if ins_data[i] == None:
                ins_data[i] = 'NULL'
            else:    
                ins_data[i] = self.stringify(ins_data[i])

        val_string = '(' + ','.join(ins_data) + ')' 

        if cols == 'All':
            sql_string = 'INSERT INTO %s VALUES %s' \
                %(t_name,val_string)
        else:
            sql_string = 'INSERT INTO %s %s VALUES %s' \
                %(t_name,col_string,val_string)

        self.execute(sql_string)
        self.conn.commit()    

    def delete(self,t_name,index):
        self.execute('DELETE FROM %s WHERE i=%d' %(t_name,index))
        self.conn.commit()

    def update(self,t_name,index,val,col,last=True):
        val = self.stringify(val)
        sql_string = 'UPDATE %s SET %s = %s WHERE i=%d' \
            %(t_name,col,val,index)
        self.execute(sql_string)
        if last:
            self.conn.commit()   

    def updateRow(self,t_name,index,**cols_vals):
        col_list = ''
        for col, val in cols_vals.items():
            col_list += ' %s = %s,' %(col,str(val))  

        sql_string = 'UPDATE %s SET%s WHERE i=%d' %(t_name,col_list[:-1],index) 
        self.execute(sql_string) 

    def dbTransfer(self,to=':memory:',_from=':memory:'):
        to_conn, to_cur = self.connect(to)
        if _from == ':memory:':
            from_conn, from_cur = self.conn,self.cur
        else:
            from_conn, from_cur = self.connect(_from)  

        from_conn.backup(to_conn)   

        return DBManager.fromConn(to_conn,to_cur)  

    def selectTable(self,t_name):
        sql_string = 'SELECT * FROM %s' %t_name
        self.cur.execute(sql_string)
        return self.cur.fetchall()

    def printTable(self,t_name):
        self.cur.execute('SELECT * FROM %s' %t_name)
        print(self.cur.fetchall())

    def getVal(self,t_name,index,col):
        sql_string = 'SELECT %s FROM %s WHERE i=%d' %(col,t_name,index)
        self.execute(sql_string)
        result = self.cur.fetchone()
        if result:
            return result[0]
        else:
            return []    

    def getVals(self,t_name,id_list,col):
        data_list = []
        for i in id_list:
            data_list.append(self.getVal(t_name,i,col))
        return data_list   

    def getRow(self,t_name,index):
        sql_string = 'SELECT * FROM %s WHERE i=%d' %(t_name,index)
        self.execute(sql_string)
        return self.cur.fetchone()

    def getRows(self,t_name,id_list):
        sql_string = 'SELECT * FROM %s WHERE i IN (%s)' \
            %(t_name,', '.join([str(_id) for _id in id_list]))
        self.execute(sql_string)
        return self.cur.fetchall()    

    def getCol(self,t_name,col_name,**filters):
        sql_string = 'SELECT %s FROM %s' %(col_name,t_name)
        
        filter_string = ''
        for key,value in filters.items():
            filter_string += ' AND %s = %s' %(t_name+'.'+key,value)
        if filters:
            sql_string += ' WHERE' + filter_string[4:] 

        self.execute(sql_string)
        return self.single(self.cur.fetchall())         
    
    def getTables(self):
        self.execute('SELECT name FROM sqlite_master WHERE type = "table"')
        return self.cur.fetchall()

    def selectByVal(self,t_name,col_name,val):
        sql_string = 'SELECT i from %s WHERE %s = %s'\
             %(t_name,col_name,str(val))
        self.execute(sql_string)
        return self.single(self.cur.fetchall())     

    def selectByVals(self,t_name,**cols_and_vals):
        sql_string = 'SELECT i from %s WHERE ' % t_name
        for key, val in cols_and_vals.items():
            sql_string += ('%s = %s AND ' %(key, val))
        sql_string = sql_string.strip(' AND ') 
        self.execute(sql_string)
        return self.single(self.cur.fetchall())  

    def selectByRange(self,t_name,s_col,r_col,start,end,**filters):
        sql_string = 'SELECT %s from %s WHERE %s BETWEEN %d AND %d' \
            %(s_col,t_name,r_col,start,end)
        for key, value in filters.items():
            sql_string += " AND %s = %s" %(key,value)
        self.execute(sql_string)
        return [self.single(self.cur.fetchall())][0]    

    def colRangeSelect(self,t_name,s_col,col,start,end,**filters):
        sql_string = 'SELECT %s from %s WHERE %s BETWEEN %d AND %d' \
            %(s_col,t_name,col,start,end)
        for key, value in filters.items():
            sql_string += " AND %s = %s" %(key,value)
        self.execute(sql_string)
        return [i[0] for i in self.clean(self.cur.fetchall())]  

    def innerJoin(self,t_name,t_sel_cols,j_name,j_sel_cols,t_cond_col,j_cond_col,operator='=',**filters):
        if t_sel_cols == '*':
            t_sel_cols = ['*']

        if j_sel_cols == '*':
            j_sel_cols = ['*']

        sel_cols = ', '.join([t_name + '.' + col for col in t_sel_cols] \
            + [j_name + '.' + col for col in j_sel_cols])
        sql_string = 'SELECT %s from %s INNER JOIN %s on %s.%s %s %s.%s' \
            %(sel_cols,t_name,j_name,t_name,t_cond_col,operator,j_name,j_cond_col)

        filter_string = ''
        for key,value in filters.items():
            filter_string += ' AND %s = %s' %(t_name+'.'+key,value)
        if filters:
            sql_string += ' WHERE' + filter_string[4:]

        self.execute(sql_string)
        return self.cur.fetchall()

    def innerJoins(self,t_name,t_sel_cols,t_cond_cols,j_tables,j_sel_cols,j_cond_cols,operators=None,f_op='=',**filters):
        if t_sel_cols == '*':
            t_sel_cols = ['*']

        if not operators:
            operators = {table:'=' for table in j_tables}    

        sel_cols = ', '.join([t_name + '.' + col for col in t_sel_cols]) + ', '
        for table in j_tables:
            sel_cols += ', '.join(
                [table + '.' + col for col in j_sel_cols[table]]
                ) + ', '

        sel_cols = sel_cols.strip(', ')

        sql_string = 'SELECT %s from %s' %(sel_cols,t_name)

        join_string = ''
        for table in j_tables:
            join_string += ' INNER JOIN %s on %s.%s %s %s.%s' \
                %(table,t_name,t_cond_cols[table],operators[table],table,j_cond_cols[table])
        sql_string += join_string

        filter_string = ''
        for key,value in filters.items():
            if type(value) in [list,set,tuple]:
                value = [str(_i) for _i in value]
                value = '(%s)' %', '.join(value)
            filter_string += ' AND %s %s %s' %(t_name+'.'+key,f_op,value)
        if filters:
            sql_string += ' WHERE' + filter_string[4:]    

        self.execute(sql_string)
        return self.cur.fetchall()            

    def rename(self,t_name,new_name):
        sql_string = 'ALTER TABLE ' + t_name + ' RENAME TO ' + new_name
        self.execute(sql_string)
    
    def repopulate(self,t_name,old_cols,old_name):
        col_str = ''
        for col in old_cols:
            col_str = col_str + col + ','
        col_str = col_str[:-1]    
        sql_string = 'INSERT INTO ' + t_name + ' ('+ col_str + ') SELECT ' + col_str + ' FROM ' + old_name
        self.execute(sql_string)

    def clean(self,data):
        if not data:
            return []   
        else:    
            return_data = [list(row) for row in data] 

        return return_data   

    def single(self,data):
        if not data:
            return []
        elif type(data[0]) in [int,str,float]:
            return data
        else:    
            return [i[0] for i in self.clean(data)]

    def deleteDB(self):
        self.close()
        if os._exists(self.path):
            os.remove(self.path)

    def close(self):
        self.conn.close()

#sigManager
class tracked(object):
    def __init__(self,dummy=0):
        pass

    def __call__(self,f):
        def wrapper(*args,**kwargs):
            porthole = inspect.stack()[1]
            caller = inspect.stack()[1].function
            caller_class = str(type(inspect.stack()[1].frame.f_locals['self'])) \
                .split("'")[1]

            if args[0].trk._track:    
                self.trk = args[0].trk
                self.trk.open(args[2],args[1],f.__name__,caller_class + '.' + caller)
            f(*args,**kwargs)
            if args[0].trk._track:
                self.trk.close()
        return wrapper 

class sigTracker():
    def __init__(self):
        self._level = 0
        self._indent = 0
        self._cur_list = []
        self._stack = []
        self._print_run = 0
        self._open = False
        self._track = False

    def open(self,typenum,rownum,sig_name,caller):
        if self._track:
            if self._open:
                self._level += 1
            self.printStack([self._level,sig_name,typenum,rownum,caller])
            self._open = True

    def close(self):
        if self._track:
            self._level -= 1
            if self._level <= 0:
                self._level = 0
                self._open = False

    def printStack(self,_list):
        if _list[0] == 0:
            print('No. %i' %self._print_run)
        self._print_run += 1
        print('----'*_list[0] + '%s CALLED BY %s (ROWNUM %d, TYPENUM %d)' \
            %(_list[1],_list[4],_list[3],_list[2]))
    
    def track(self):
        self._track = True

class sigManager(QObject):
    itemDeleted = pyqtSignal(int,int,bool)
    itemChanged = pyqtSignal(int,int)
    itemColorChanged = pyqtSignal(int,int)
    payChanged = pyqtSignal(int,int,float,float)
    hrsChanged = pyqtSignal(int,int,float,float)
    paylevelChanged = pyqtSignal(int,int,float,int)
    dateChanged = pyqtSignal(int,int,int,int)
    jobChanged = pyqtSignal(int,int,int)
    pdateChanged = pyqtSignal(int,int)
    addRaise = pyqtSignal(int,int,float,float,list)
    resum = pyqtSignal(int,int)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.trk = sigTracker()
        self._signals = [
            self.itemDeleted,
            self.itemChanged,
            self.itemColorChanged,
            self.payChanged
            ]

    @tracked()
    def itemDeletedSig(self,rownum,typenum,last=True):
        self.itemDeleted.emit(rownum,typenum,last)

    @tracked()
    def itemChangedSig(self,rownum,typenum):
        self.itemChanged.emit(rownum,typenum)

    @tracked()
    def itemColorChangedSig(self,rownum,typenum):
        self.itemColorChanged.emit(rownum,typenum)

    @tracked()
    def payChangedSig(self,rownum,typenum,s_offset,a_offset):
        self.payChanged.emit(rownum,typenum,s_offset,a_offset)
    
    @tracked()
    def hrsChangedSig(self,rownum,typenum,s_offset,a_offset):
        self.hrsChanged.emit(rownum,typenum,s_offset,a_offset)

    @tracked()
    def paylevelChangedSig(self,rate_num,level,date,_id):
        self.paylevelChanged.emit(rate_num,level,date,_id)

    @tracked()
    def dateChangedSig(self,rownum,typenum,original_date,model_col):
        self.dateChanged.emit(rownum,typenum,original_date,model_col)

    @tracked()
    def jobChangedSig(self,rownum,typenum,original_job):
        self.jobChanged.emit(rownum,typenum,original_job)

    @tracked()
    def addRaiseSig(self,rate,date,old_level,level,colors):
        self.addRaise.emit(rate,date,old_level,level,colors)

    @tracked()
    def resumSig(self,rownum,typenum):
        self.resum.emit(rownum,typenum)

    def connect(self,conn_dict):
        for key, value in conn_dict.items():
            key.connect(value) 

#payManager
class PayManager():
    def __init__(self,db_,sig_man,**db_names):
        self.db = db_
        self.sig = sig_man
        self.co_name = db_names['co']
        self.ca_name = db_names['ca']
        self.r_name = db_names['r']
        self.j_name = db_names['j']
        self.pl_name = db_names['pl']

        self.pr_W2 = payRule(self,self.db,0,0)
        self.pr_1099 = payRule(self,self.db,1,0,ot_mod=1,dt_mod=1)
        self.pr_flat = payRule(self,self.db,2,0,rt_mod=0)

        self._last_offset = [0,0]

        self.timelines = {}

        self.to_delete = []

        connect = {
            self.sig.hrsChanged:self.updatePay,
            self.sig.itemChanged:self.updatePay,
            self.sig.jobChanged:self.jobChanged,
            self.sig.dateChanged:self.dateChanged,
            self.sig.itemDeleted:self.itemDeleted,
            self.sig.paylevelChanged:self.paylevelChanged,
        }
        self.sig.connect(connect)

    def updatePay(self,rownum,typenum,s_off=None,a_off=None):
        #call
        if typenum == 3:
            self.updateCall(rownum)
        elif typenum == 2:
            self.multUpdate(rownum,typenum)    
        else:
            if self.getCalls(rownum,typenum):
                for call_id in self.getCalls(rownum,typenum):
                    self.updateCall(call_id)          

    def itemDeleted(self,rownum,typenum,last=True):
        if typenum == 3:     
            if not last:
                self.to_delete.append(rownum)
            elif last:
                self.to_delete.append(rownum)
                calls = self.getMultCallData(self.to_delete)
                for call in calls:
                    self.updateCall(call,del_call=call['id'])
                    self.sig.payChangedSig(
                        rownum,typenum,-call['s_pay'],-call['a_pay']
                    )
                    

        elif typenum == 1:
            if rownum in self.timelines.keys():
                del self.timelines[rownum]

        elif typenum == 4:
            for rate in self.timelines.keys():
                if rownum in [entry[3] for entry in self.timelines[rate]]:
                    self.delTimelineEntry(rownum,rate)
                    break

    def dateChanged(self,rownum,typenum,o_date,model_col):
        if typenum == 3 and o_date:
            self.updateCall(rownum,o_date=o_date)                

    def jobChanged(self,rownum,typenum,original_val):
        if typenum == 3:     
            job_id = self.getCallData(rownum)['job']
            if original_val:
                self.multUpdate(original_val,2)
            if job_id:
                self.multUpdate(job_id,2)
            self.updatePay(rownum,typenum) 

    def itemChanged(self,rownum,typenum):
        self.updatePay(rownum,typenum)

    def multUpdate(self,rownum,typenum):
        tot_off = [0,0]
        job_calls = self.getCalls(rownum,typenum)
        s_off, a_off = self.updateCalls(job_calls)

        if typenum != 2:
            self.sig.payChangedSig(rownum,typenum,s_off,a_off)

    def sumPay(self,rownum,typenum):
        if typenum == 0:
            col_name = 'co'
        elif typenum == 1:
            col_name = 'rate'
        elif typenum == 2:
            col_name = 'job'
        elif typenum == 3:
            return False

        return [
            round(sum(
                self.db.getVals(self.ca_name,
                self.db.selectByVal(self.ca_name,col_name,rownum),
                's_pay'
            )),2),
            round(sum(
                self.db.getVals(self.ca_name,
                self.db.selectByVal(self.ca_name,col_name,rownum),
                'a_pay'
            )),2),
            ]

    def sumHrs(self,rownum,typenum):    
        if typenum == 0:
            col_name = 'co'
        elif typenum == 1:
            col_name = 'rate'
        elif typenum == 2:
            col_name = 'job'
        elif typenum == 3:
            return False

        return [
            round(sum(
                self.db.getVals(self.ca_name,
                self.db.selectByVal(self.ca_name,col_name,rownum),
                'sched'
            )),2),
            round(sum(
                self.db.getVals(self.ca_name,
                self.db.selectByVal(self.ca_name,col_name,rownum),
                'act'
            )),2),
            ]

    def updateCall(self,call,del_call=None,carry=True,o_date=None):
        if type(call) == int:
            if call == del_call:
                return None   
            call_id = call    
            call = self.getCallData(call)
        elif type(call) == dict:
            call_id = call['id']
        else:
            raise TypeError

        if not call:
            return False

        #Hourly
        if call['rate']['stat'] == 0:
            if call['tax'] == 0:
                s_pay, a_pay, recalc = self.pr_W2.calculate(call,del_call,o_date)
            elif call['tax'] == 1:             
                s_pay, a_pay, recalc = self.pr_1099.calculate(call,del_call,o_date)  
            flat = False
            
        #Flat
        elif call['rate']['stat'] == 1:           
            s_pay, a_pay, recalc = self.pr_flat.calculate(call,del_call,o_date) 
            flat = True        
        
        self.db.updateRow(self.ca_name,call_id,s_pay=s_pay,a_pay=a_pay)

        s_off, a_off = self.getOffset(call,[s_pay,a_pay])

        self._last_offset = [s_off,a_off]

        if s_off != 0 or a_off != 0:
            self.sig.payChangedSig(call['id'],3,s_off,a_off)
        elif call['job'] != 0 and flat and 0 not in self._last_offset:
            self.sig.payChangedSig(
                call['job'],2,-self._last_offset[0],-self._last_offset[1],
                )

        if carry:
            self.updateCalls(recalc,del_call=call['id'],carry=False)        

        return s_off, a_off

    def updateCalls(self,call_ids,del_call=None,carry=True):
        if not call_ids:
            return 0, 0
        calls = self.getMultCallData(call_ids)
        s_off_tot = 0
        a_off_tot = 0
        for call in calls:
            s_off, a_off = self.updateCall(call,del_call=del_call,carry=carry)
            s_off_tot += s_off
            a_off_tot += a_off

        return s_off_tot, a_off_tot    

    def getCalls(self,rownum,typenum):
        try:
            if typenum == 0:
                return self.db.selectByVal(self.ca_name,'co',rownum)
            elif typenum == 1:
                return self.db.selectByVal(self.ca_name,'rate',rownum)
            elif typenum == 2:
                return self.db.selectByVal(self.ca_name,'job',rownum)    
        except:
            pass

    def getCallData(self,call_id):
        t_cond_cols = {self.r_name:'rate',self.co_name:'co'}
        j_sel_cols = {
            self.r_name:['rate','min','stat'],
            self.co_name:['stat']
            }
        j_cond_cols = {self.r_name:'i',self.co_name:'i'}

        id_,date,name,co,rate,job,sched,s_pay,act,a_pay,r_rate,r_min,r_stat,co_tax = \
            self.db.innerJoins(
                self.ca_name,
                ['i','date','name','co','rate','job','sched','s_pay','act','a_pay'],
                t_cond_cols,
                [self.r_name,self.co_name],
                j_sel_cols,
                j_cond_cols,
                i=call_id
                )[0]
        
        #Pay Level Calculation
        if rate in self.timelines.keys():
            for level in self.timelines[rate]:
                if (level[0] == None or date >= level[0]) and (level[1] == None or date <= level[1]):
                    r_rate = level[2]
                    break

        return {
            'id':id_,
            'date':date,
            'co':co,
            'rate':{'id':rate,'rate':r_rate,'min':r_min,'stat':r_stat},
            'job':job,
            'sched':sched,
            's_pay':s_pay,
            'act':act,
            'a_pay':a_pay,
            'tax':co_tax,
            }

    def getMultCallData(self,call_ids):
        t_cond_cols = {self.r_name:'rate',self.co_name:'co'}
        j_sel_cols = {
            self.r_name:['rate','min','stat'],
            self.co_name:['stat']
            }
        j_cond_cols = {self.r_name:'i',self.co_name:'i'}

        db_result = \
            self.db.innerJoins(
                self.ca_name,
                ['i','date','name','co','rate','job','sched','s_pay','act','a_pay'],
                t_cond_cols,
                [self.r_name,self.co_name],
                j_sel_cols,
                j_cond_cols,
                f_op='IN',
                i=call_ids
                )      

        call_list = []
        for call in db_result:
            id_,date,name,co,rate,job,sched,s_pay,act,a_pay,r_rate,r_min,r_stat,co_tax = call
            #Pay Level Calculation
            if rate in self.timelines.keys():
                for level in self.timelines[rate]:
                    if (level[0] == None or date >= level[0]) and (level[1] == None or date <= level[1]):
                        r_rate = level[2]
                        break
            call_list.append({
                'id':id_,
                'date':date,
                'co':co,
                'rate':{'id':rate,'rate':r_rate,'min':r_min,'stat':r_stat},
                'job':job,
                'sched':sched,
                's_pay':s_pay,
                'act':act,
                'a_pay':a_pay,
                'tax':co_tax,                
            })

        return call_list                

    def getOffset(self,call,pay):
        s_off = pay[0] - call['s_pay']
        a_off = pay[1] - call['a_pay']
        return s_off, a_off
    
    def updateTimeline(self,rate,date,level,_id,end_date=None):
        if rate in self.timelines.keys():
            cur_timeline = self.timelines[rate]
            found = False
            ids = [entry[3] for entry in cur_timeline]
            if _id in ids:
                pos = ids.index(_id)
                del cur_timeline[pos]   

            i = len(cur_timeline)-1
            if date >= cur_timeline[i][0]:
                cur_timeline[i][1] = date-1
                if end_date:
                    cur_timeline.append([date,end_date,level,_id])
                else:    
                    cur_timeline.append([date,None,level,_id])
                found = True
            elif i == 0:
                if date <= cur_timeline[i][0]:
                    cur_timeline.append([date,cur_timeline[i][0]-1,level,_id])
                    found = True    
            i -= 1       
            while not found:
                if i == 0 and cur_timeline[i][0] == None or date < cur_timeline[i][0]:
                    cur_timeline.append([date,cur_timeline[i][0]-1,level,_id])
                    found = True
                elif date > cur_timeline[i][0] and date < cur_timeline[i][1]:
                    cur_timeline[i][1] = date-1
                    cur_timeline.append([date,cur_timeline[i+1][0]-1,level,_id])        
                    found = True
                i -= 1 
            self.timelines[rate] = sorted(cur_timeline,key=lambda x: x[0])    
        else:
            self.timelines[rate] = [[date,None,level,_id]]

        self.updatePay(rate,1)    

    def paylevelChanged(self,rate,date,level,_id):
        self.updateTimeline(rate,date,level,_id)
        self.updatePay(rate,1)

    def delTimelineEntry(self,rownum,rate):
        i = [entry[3] for entry in self.timelines[rate]].index(rownum)
        del self.timelines[rate][i]
        if len(self.timelines[rate]) == 0:
            del self.timelines[rate]    
        elif i >= len(self.timelines[rate])-1:
            self.timelines[rate][i-1][1] == None
        else:    
            self.timelines[rate][i-1][1] = self.timelines[rate][i][0]

        self.updatePay(rate,2)    

    def reCalcAll(self):
        print('ReCalculating Calls')
        for call_id in self.db.single(self.db.getCol(self.ca_name,'i')):
            print('Calculating %d' %call_id)
            self.updateCall(call_id)
        print('ReCalculating Jobs')
        for job_id in self.db.single(self.db.getCol(self.j_name,'i')):
            print('Calculating %d' %job_id)
            self.sig.resumSig(job_id,2)
        print('Complete')

class payRule():
    def __init__(self,parent,db,id_,week,rt_mod=1,ot=8,ot_mod=1.5,dt=12,dt_mod=2):
        self.parent = parent
        self.db = db
        self.id = id_
        self.work_week = week
        self.rt_mod = rt_mod
        self.ot_mod = ot_mod
        self.dt_mod = dt_mod
        self.ot = ot
        self.dt = dt

    def calculate(self,call,del_call=None,o_date=None):
        if call['id'] == del_call:
            recalc_calls = self.reCalc(call['date'],o_date=o_date)
            if recalc_calls:
                recalc_calls.remove(call['id'])
            return 0, 0, recalc_calls

        min_pay = call['rate']['rate']*call['rate']['min']

        #Flat Rate
        if self.rt_mod == 0:
            if call['job'] == 0:
                s_pay, a_pay = call['rate']['rate'], call['rate']['rate']
            else:
                return self.jobCalc(call,del_call,o_date)    
        else:
            s_ot_hrs, s_dt_hrs, a_ot_hrs, a_dt_hrs = self.getOTHrs(call,del_call)

            s_pay = round(max(min_pay,
                (call['sched']-s_ot_hrs-s_dt_hrs)*(call['rate']['rate']) +
                s_ot_hrs*self.ot_mod*(call['rate']['rate'])+
                s_dt_hrs*self.dt_mod*(call['rate']['rate'])),
                2
            )

            a_pay = round(max(min_pay,
                (call['act']-a_ot_hrs-a_dt_hrs)*(call['rate']['rate']) +
                a_ot_hrs*self.ot_mod*(call['rate']['rate'])+
                a_dt_hrs*self.dt_mod*(call['rate']['rate'])),
                2
            ) 

        recalc_calls = self.reCalc(call['date'],o_date=o_date)
        if recalc_calls:
            recalc_calls.remove(call['id'])

        return s_pay, a_pay, recalc_calls 

    def jobCalc(self,call,del_call=None,o_date=None):
        s_hrs_tot, a_hrs_tot = self.parent.sumHrs(call['job'],2)

        if del_call:
            del_call = self.parent.getCallData(del_call)
            s_hrs_tot -= del_call['sched']
            a_hrs_tot -= del_call['act']
        pay_tot = self.db.getVal('ra',self.db.getVal('jo',call['job'],'rate'),'rate')

        if s_hrs_tot == 0:
            s_pay = 0
        else:    
            s_pay = round((call['sched']/s_hrs_tot)*pay_tot,2)

        if a_hrs_tot == 0:
            a_pay = 0
        else:    
            a_pay = round((call['act']/a_hrs_tot)*pay_tot,2)

        recalc_calls = self.reCalc(call['date'],o_date=o_date)
        if recalc_calls:
            recalc_calls.remove(call['id'])

        return s_pay, a_pay, recalc_calls 

    def getOTHrs(self,call,del_call=None):
        same_day_co = self.sameDateCo(call,del_call)
        wk_hrs, is_consecutive = self.sumWorkWeek(call,del_call)

        if is_consecutive:
            s_dt = call['sched']
            s_ot = 0

            a_dt = call['act']
            a_ot = 0

            return s_ot, s_dt, a_ot, a_dt


        if not same_day_co:
            s_dt = max(0,call['sched']-self.dt)
            s_ot = max(0,wk_hrs[0]-40,call['sched']-self.ot-s_dt)

            a_dt = max(0,call['act']-self.dt)
            a_ot = max(0,wk_hrs[1]-40,call['act']-self.ot-a_dt)

            return s_ot, s_dt, a_ot, a_dt

        i = 0
        cur_hrs = 0            
        cur_call = same_day_co[i]
        while cur_call[0] != call['id']:
            cur_hrs += cur_call[1]
            wk_hrs[0] += cur_call[1]
            i += 1
            cur_call = same_day_co[i]
        s_dt = min(max(0,(cur_hrs+cur_call[1])-self.dt),cur_call[1])    
        s_ot = max(
            0,
            min((cur_call[1]+wk_hrs[0])-40,cur_call[1]-s_dt),
            min((cur_hrs+cur_call[1])-self.ot-s_dt,cur_call[1]-s_dt)
        )

        i = 0
        cur_hrs = 0
        cur_call = same_day_co[i]
        while cur_call[0] != call['id']:
            cur_hrs += cur_call[2]
            wk_hrs[1] += cur_call[2]
            i += 1
            cur_call = same_day_co[i]
        a_dt = min(max(0,cur_hrs+cur_call[2]-self.dt),cur_call[2])    
        a_ot = max(
            0,
            min((cur_call[2]+wk_hrs[1])-40,cur_call[2]-a_dt),
            min((cur_hrs+cur_call[2])-self.ot-a_dt,cur_call[2]-a_dt)
        )

        return s_ot, s_dt, a_ot, a_dt

    def sameDateCo(self,call,del_call=None):
        same_date_co = self.db.selectByVals('ca',date=call['date'],co=call['co'])
        return_data = []
        for call_id in same_date_co:
            if call_id != del_call:    
                return_data.append([
                    call_id,
                    self.db.getVal('ca',call_id,'sched'),
                    self.db.getVal('ca',call_id,'act')
                ])
        return return_data            

    def getWkCalls(self,call):
        date = dt.date.fromordinal(call['date'])
        return self.db.selectByRange(
            'ca',
            'i',
            'date',
            call['date']-date.weekday(),
            call['date']-1,
            co=call['co']
        )

    def sumWorkWeek(self,call,del_call=None):
        week_calls = self.getWkCalls(call)
        wk_hrs = [0,0]
        for cur_call in week_calls:
            if cur_call != del_call:
                wk_hrs[0] += self.db.getVal('ca',cur_call,'sched')
                wk_hrs[1] += self.db.getVal('ca',cur_call,'act')

        is_consecutive = False
        if week_calls:
            dates = set(
                    [self.db.getVal('ca',call,'date') for call in week_calls]
                    )

            if len(dates) == 7: is_consecutive = True            
               
        return wk_hrs, is_consecutive

    def reCalc(self,call_date,o_date=None):
        wkday = dt.date.fromordinal(call_date).weekday()
        day_hrs = [
            sum(self.db.single(self.db.getCol('ca','sched',date=call_date))),
            sum(self.db.single(self.db.getCol('ca','act',date=call_date)))
        ]

        wk_hrs = [
            sum(self.db.selectByRange('ca','sched','date',call_date-wkday,call_date+(7-wkday))),
            sum(self.db.selectByRange('ca','act','date',call_date-wkday,call_date+(7-wkday)))
        ]

        recalc_list = set()
        if max(day_hrs) > self.ot or max(wk_hrs) > 40:

            for call in self.db.single(self.db.getCol('ca','i',date=call_date)):
                recalc_list.add(call)
            for call in self.db.selectByRange('ca','i','date',call_date-wkday,call_date+(7-wkday)):
                recalc_list.add(call)    

            if o_date and o_date != call_date:
                for call in self.reCalc(o_date):
                    recalc_list.add(call)

        return recalc_list                       