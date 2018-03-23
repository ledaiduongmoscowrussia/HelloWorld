import numpy as np
import pandas as pd
import warnings;warnings.filterwarnings('ignore')
from Dataset import *
from sqlalchemy import create_engine

# engine = create_engine('mysql+mysqldb://ledaiduongvnth:leduysao290893@ledaiduongvnth.mysql.pythonanywhere-services.com/ledaiduongvnth$CheckScoreTin', pool_recycle=280)

class SubFunctions:
    def __init__(self):pass

    def ReadDataFrameFromMySQL(self, path):
        df = pd.io.gbq.read_gbq('SELECT * FROM CheckScoreTin.' + path + ' ORDER BY id ', 'artful-journey-197609').drop(
            ['id'], axis=1)
        return df

    def WriteDataFrimeToSQLDatabase(self, df, table):
        df.insert(loc=0, column='id', value=range(df.shape[0]))
        pd.io.gbq.to_gbq(df, 'CheckScoreTin.' + table, 'artful-journey-197609', if_exists='replace')

    def AddSeriesOrListToRowOfDataFrameByIndexEqualLength(self,path,series_or_list):
        series = pd.Series(series_or_list)
        df_origin = self.ReadDataFrameFromMySQL(path)
        df_update = pd.DataFrame(index= ['0'], columns= df_origin.columns )
        len_series = len(series.index.tolist())
        len_columns_data_frame = len(df_update.columns)
        if len_series == len_columns_data_frame:
            for index in np.arange(0, len_series): df_update.set_value('0', df_update.columns[index], series[index])
            df_origin = df_origin.append(df_update, ignore_index=True)
            self.WriteDataFrimeToSQLDatabase(df_origin, path)
        else: raise ValueError('columns length of dataframe not equal length of series')

    def AddSeriesToRowOfDataFrameByName(self,path,series):
        df_origin = self.ReadDataFrameFromMySQL(path)
        df_update = pd.DataFrame(index= ['0'], columns= df_origin.columns )
        for index in series.index.tolist(): df_update.set_value('0', index, series[index])
        df_origin = df_origin.append(df_update, ignore_index=True)
        self.WriteDataFrimeToSQLDatabase(df_origin, path)

    def RemoveRows(self, path, list_of_rows):
        df = self.ReadDataFrameFromMySQL(path)
        df = df.drop(list_of_rows)
        self.WriteDataFrimeToSQLDatabase(df, path)

    def RemoveAllRows(self, path):
        df = self.ReadDataFrameFromMySQL(path)
        df = df.drop(df.index.tolist())
        self.WriteDataFrimeToSQLDatabase(df, path)

    def RemoveColumns(self, path, list_of_columns):
        df = self.ReadDataFrameFromMySQL(path)
        df = df.drop(list_of_columns, axis = 1)
        self.WriteDataFrimeToSQLDatabase(df, path)

    def WriteToExcel(self, df, path):
        writer = pd.ExcelWriter(path)
        df.to_excel(writer)
        writer.save()

    def WriteToCSV(self, path):
        df = self.ReadDataFrameFromMySQL(path)
        df.to_csv(path+'.csv')

