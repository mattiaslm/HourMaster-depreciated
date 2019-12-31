import managers as man
import tables as tbl
import random as rand
import os
import main
import sys
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qt
import timeit
import csv


class Updater():
    def __init__(self,db):
        try:
            self.old_db = man.DBManager(db)
            self.temp_db = self.old_db.dbTransfer()
            try:
                self.old_db.deleteDB()
            except PermissionError:
                print('File In Use.')    
            self.new_db = man.DBManager.setUp(
                db,tbl.getModelSchema()[0],tbl.getModelSchema()[1]
                ) 

        except Exception as e:
            print(e)
            print('Update Failed. Reverting Changes')
            self.old_db = self.temp_db.dbTransfer(to=db)

class Exporter():
    def __init__(self,_from,to,_type):
        self._from = _from
        self.to = to
        self.db = man.DBManager(_from)
        if _type == 'csv':
            self.encodeCSV()

    def encodeCSV(self):
        co_data = self.db.selectTable('co')
        r_data = self.db.selectTable('ra')
        j_data = self.db.selectTable('jo')
        pl_data = self.db.selectTable('pl')
        ca_data = self.db.selectTable('ca')

        with open(self.to,'a') as csv_file:
            writer = csv.writer(csv_file)
            
            schema = tbl.getModelSchema()[1]
            writer.writerow([col[0] for col in schema[0]])
            writer.writerows(co_data)
            writer.writerow([col[0] for col in schema[1]])
            writer.writerows(r_data)
            writer.writerow([col[0] for col in schema[2]])
            writer.writerows(j_data)
            writer.writerow([col[0] for col in schema[4]])
            writer.writerows(pl_data) 
            writer.writerow([col[0] for col in schema[3]])
            writer.writerows(ca_data)                                    

def createEntries(co_num,r_num,j_num,ca_num,db_path):
    if not os.path.isfile(db_path):
        app = qt.QApplication(sys.argv)
        win = main.MainWindow('',(0,133))
        win.saveAs(db_path)
        win.close()
    else:
        os.remove(db_path)
        app = qt.QApplication(sys.argv)
        win = main.MainWindow('',(0,133))
        win.saveAs(db_path)
        win.close()


    #data_manipulation
    r_num = max(r_num,co_num)

    #connect to db
    db = man.DBManager(db_path)

    print('Creating %d Companies' %co_num)

    #create companies
    for i in range(co_num):
        db.insert('co',[
            i,
            'Co ' + str(i),
            'C' + str(i),
            rand.randint(0,1),
            rand.randint(0,255),
            rand.randint(0,255),
            rand.randint(0,255)
        ])

        stat = rand.randint(0,1)
        if not stat:
            rate_amt = rand.randint(0,50)
        else:
            rate_amt = rand.randint(50,500)  
        db.insert('ra',[
            i,
            'R' + str(i),
            rate_amt,
            rand.randint(0,6),
            stat,
            i,
            rand.randint(0,255),
            rand.randint(0,255),
            rand.randint(0,255)
        ])

    print('Creating %d Rates' %r_num)

    #create rates
    for i in range(r_num-co_num):
        stat = rand.randint(0,1)
        if not stat:
            rate_amt = rand.randint(0,50)
        else:
            rate_amt = rand.randint(50,500)    
        db.insert('ra',[
            i+co_num,
            'R' + str(i+co_num),
            rate_amt,
            rand.randint(0,6),
            stat,
            rand.randint(0,co_num-1),
            rand.randint(0,255),
            rand.randint(0,255),
            rand.randint(0,255)            
        ])

    print('Creating %d Jobs' %j_num)
    #create jobs
    for i in range(j_num):
        co = rand.randint(0,co_num-1)
        rates = db.single(db.getCol('ra','i',co=co))
        if len(rates) == 1:
            rate = rates[0]
        else:    
            _i = rand.randint(0,len(rates)-1)
            rate = rates[_i]
        db.insert('jo',[
            i+1,
            'J' + str(i+1),
            co,
            rate,
            rand.randint(0,255),
            rand.randint(0,255),
            rand.randint(0,255)              
        ])

    print('Creating %d Calls' %ca_num)

    #create calls
    for i in range(ca_num):
        co = rand.randint(0,co_num-1)
        rates = db.single(db.getCol('ra','i',co=co))
        if len(rates) == 1:
            rate = rates[0]
        else:    
            _i = rand.randint(0,len(rates)-1)
            rate = rates[_i]    
        jobs = db.single(db.getCol('jo','i',co=co,rate=rate))
        if jobs:
           job = jobs[rand.randint(0,len(jobs)-1)]
           if rand.randint(0,100) < 75:
               job = 0
        else:
            job = 0
        sched = rand.randint(0,12)
        act = max(1,sched + rand.randint(-5,5))    
        db.insert('ca',[
            i,
            rand.randint(745000,751000),
            'CA' + str(i),
            co,
            rate,
            job,
            sched,
            0,
            act,
            0,
            None,
            rand.randint(0,255),
            rand.randint(0,255),
            rand.randint(0,255)             
        ]) 
   
    print('Complete')



if __name__ == '__main__':
    exp = Exporter('E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_100.db','E:\Projects\Python\HourMaster\HM_A2-5\db\\exp_test.csv','csv')
#    createEntries(1,1,0,1,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_1.db')
#    createEntries(10,10,5,100,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_100.db')
#    createEntries(10,10,5,200,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_200.db')
#    createEntries(10,10,5,300,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_300.db')  
#    createEntries(10,10,5,400,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_400.db')
#    createEntries(10,10,5,500,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_500.db')         
#    createEntries(10,10,5,1000,'E:\Projects\Python\HourMaster\HM_A2-5\db\\time_test_1000.db')
