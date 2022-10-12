#!/usr/bin/python3.6
import pandas as pd
import datetime
import warnings
import glob
import os 

warnings.filterwarnings("ignore")

current_path = "/home/cesar/Desktop/luisd/scripts/Obtencion_posicion/"
input_files_path = current_path + "Input_files/Data_set/"
input_files_path_op = current_path + "Input_files/Data_procesada/"
output_files_path = current_path + "Output_files/"
output_files_path2 = output_files_path + "ToUpload/"

# Input file: nmea type GGA & ZDA file. 
def read_nmea(input_file_name):
    # read csv: without header, and the index is the first column
    n_cols = list(range(15)) # a trick to insert a different number of columns
    data = pd.read_csv(input_files_path+input_file_name, names=n_cols, header=None, index_col=[0])
    return data

# Input file: pandas dataframe
def nmea2lisn(data):
    # Select and clean GGA data: Time + Coordinates 
    data_gga = data.loc[["$GPGGA"],:] 
    data_gga2 = data_gga[[1,2,3,4,5,9]] # Choose only the valid information
    data_gga2.columns = ["UTC_time", "LAT", "LAT(unit)", "LON", "LON(unit)", "HEIGHT"]
    data_gga2.reset_index(drop=True, inplace=True)
    #
    N = 10
    if len(data_gga2) < N:
       N = len(data_gga2)
    # -- Remove first columns, which have wrong data
    vals = data_gga2.iloc[:N,0].values # extract first 10 rows 
    indice = [v<=min(vals) for v in vals].index(True)
    rm_rows = list(range(indice))
    data_gga2.drop(index=rm_rows, inplace=True)
    data_gga2.reset_index(drop=True, inplace=True)
    #
    # -- Remove last columns, wich have wrong data
    vals = data_gga2.iloc[-N:,0].values # extract 10 last rows 
    indice = [vv>=max(vals) for vv in vals].index(True)
    a = list(range(len(vals)-indice-1))
    rm_rows = [len(data_gga2)-(val+1) for val in a]
    data_gga2.drop(index=rm_rows, inplace=True)
    #
    data_gga2.drop_duplicates(subset="UTC_time", keep='last', inplace=True)

    # Select and clean ZDA data: Date
    data_zda = data.loc[["$GPZDA"],:] 
    data_zda2 = data_zda[[1,2,3,4]]
    data_zda2.columns = ["UTC_time","day","month","year"]
    data_zda2.reset_index(drop=True, inplace=True)
    #
    # --Remove the first columns, with wrong data
    vals = data_zda2.iloc[:N,0].values # 10
    indice = [vv<=min(vals) for vv in vals].index(True)
    rm_rows = list(range(indice))
    data_zda2.drop(index=rm_rows, inplace=True)
    data_zda2.reset_index(drop=True, inplace=True)
    #
    # --Remove the last columns, which have wrong data
    vals = data_zda2.iloc[-N:,0].values
    indice = [vv>=max(vals) for vv in vals].index(True)
    a = list(range(len(vals)-indice-1))
    rm_rows = [len(data_zda2)-(val+1) for val in a]
    data_zda2.drop(index=rm_rows, inplace=True)
    #
    data_zda2.drop_duplicates(subset="UTC_time", keep="last", inplace=True)

    # DATA PROCESSING 
    # --Obtain location info 
    def convert2_decimalDegree(value): # convert degree + decimal minute value to decimal degree
        integer = int(value/100)
        decimal = (value-integer*100)/60
        return integer + decimal

    def coordinate_sign(coord): # Change N,S,W,E to numbers
        if coord == "S" or coord == "W":
            return -1
        elif coord == "N" or coord == "E":
            return +1
        else:
            return "Error!"

    data_gga2.loc[:,"LAT"] = data_gga2.loc[:,"LAT"].apply(convert2_decimalDegree).round(6) * data_gga2.loc[:,"LAT(unit)"].apply(coordinate_sign)
    del data_gga2["LAT(unit)"] # drop this column

    data_gga2.loc[:,"LON"] = data_gga2.loc[:,"LON"].apply(convert2_decimalDegree).round(5) * data_gga2.loc[:,"LON(unit)"].apply(coordinate_sign)
    del data_gga2["LON(unit)"] 

    # --Get YY/DOY from YYYY/MM/DD
    def change_date(row): 
        day = row[1]
        month = row[2]
        year = row[3]
        date = year + "/" + month + "/" + day

        date1 = datetime.datetime.strptime(date,"%Y/%m/%d") # Convert string to datetime variable 
        date2 = datetime.datetime.strftime(date1,"%y/%j") # Convert datetime to string variable

        YEAR = date2[:2] # i.e. "20/253"
        DOY = date2[3:] 

        return YEAR, DOY

    data_zda2["Year"] = data_zda2.astype('int').astype('str').apply(change_date, axis=1).str.get(0).astype("int") # Get the year YY
    data_zda2["DoY"] = data_zda2.astype('int').astype('str').apply(change_date, axis=1).str.get(1).astype("int") # Get the day of year DOY

    del data_zda2["day"]
    del data_zda2["month"]
    del data_zda2["year"]

    # --Join dfs 
    df = data_gga2.merge(data_zda2, how='left', on='UTC_time')

    # --Get seconds of day(SOD) from hour:minute:seconds, tiempo:"str"
    def get_secondsDay(tiempo): 
        hour = int(tiempo[:2])
        minute = int(tiempo[2:4])
        seconds = int(tiempo[4:])
        #
        total_seconds = seconds + minute*60 + hour*60*60
        #
        return total_seconds

    df["SoD"] = df.loc[:,"UTC_time"].astype('int').astype('str').str.zfill(6).apply(get_secondsDay)
    del df["UTC_time"] 

    # --Next, we arrange the columns
    df["Var"] = 0
    df = df[["Var","Year","DoY","SoD","LAT","LON","HEIGHT"]]
    df.drop_duplicates(subset="SoD", keep="last", inplace=True)

    # --Decimate every hour 
    #df = df.iloc[8::60, :]
    #df.reset_index(drop=True, inplace=True)

    # --Finally, convert to 7 digits float number 
    df["LAT"] = df["LAT"].apply('{:,.7f}'.format)
    df["LON"] = df["LON"].apply('{:,.7f}'.format)
    df["HEIGHT"] = df["HEIGHT"].apply('{:,.7f}'.format)

    return df

# Generate file name in the LISN format 
def get_file_name(file_name):
    station_name = file_name[:4]
    doy = file_name[4:7]
    yy = file_name[9:11]
    today = yy + "-" + doy + ";00:00:00" # e.g. '20-219;00:00:00'
    fecha = datetime.datetime.strptime(today,"%y-%j;%H:%M:%S")
    fecha = datetime.datetime.strftime(fecha,"%y-%m-%d") #e.g. '20-08-06'
    year = fecha[:2]
    month = fecha[3:5]
    day = fecha[6:8]

    file_name = station_name + "_" + year + month + day + ".pos"

    return file_name

def save_csv(input_file_name, variable):
    output_file_name = get_file_name(input_file_name)
    csv_path = output_files_path + output_file_name
    csv_path2 = output_files_path2 + output_file_name
    # Save to a permanent output folder 
    variable.to_csv(csv_path, sep='\t', index=False, header=False, encoding="utf-8")
    # Save to a temporal output folder 
    variable.to_csv(csv_path2, sep='\t', index=False, header=False, encoding="utf-8")
    
    return "Ok!"

def main():
    list_input_files = glob.glob(input_files_path+'*1') # List all NMEA files 
    if len(list_input_files)>0:
        for file_i in list_input_files:
            file_name = file_i[len(input_files_path):] # Get the file's name
            try: 
               dframe_nmea = read_nmea(file_name)
               dframe_lisn = nmea2lisn(dframe_nmea)
               save_csv(file_name, dframe_lisn)
    
               # Move input files to a permanent directory
               os.rename(file_i, input_files_path_op+file_name)
               print("File " + get_file_name(file_name) + " was obtained succesfully!")
            except:
               print("File " + get_file_name(file_name) + " is corrupted!") 

if __name__ == '__main__':
    print("Starting ...")
    main()
    print("Finished!")
