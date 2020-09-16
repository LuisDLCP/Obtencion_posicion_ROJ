import pandas as pd
import glob

current_path = "/home/luis/Desktop/Proyects_Files/LISN/GPSs/Tareas/Obtencion_posicion/"
input_files_path = current_path + "data_input/"
output_files_path = current_path + "data_output/"

# Input file: nmea type GGA & ZDA file. 
def read_nmea(input_file_name):
    # read csv: without header, and the index is the first column
    n_cols = list(range(15)) # a trick to insert a different number of columns
    data = pd.read_csv(input_files_path+input_file_name, names=n_cols, header=None, index_col=[0])
    return data

# Input file: pandas dataframe
def nmea2lisn(data):
    # Select gga data
    data_gga = data.loc["$GPGGA"] 
    data_gga2 = data_gga[[1,2,3,4,5,9]] # Choose only the valid information
    data_gga2.columns = ["UTC_time", "LAT", "LAT(unit)", "LON", "LON(unit)", "HEIGHT"]
    # Select zda data
    data_zda = data.loc["$GPZDA"] 
    data_zda2 = data_zda[[1,2,3,4]]
    data_zda2.columns = ["UTC_time","day","month","year"]

    # First, we obtain time info

    # Then, we obtain location info 
    data_gga2.reset_index(drop=True, inplace = True) # Drop label index

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
    
    data_gga2["LAT"] = data_gga2["LAT"].apply(convert2_decimalDegree).round(6) * data_gga2["LAT(unit)"].apply(coordinate_sign)
    del data_gga2["LAT(unit)"] # drop this column

    data_gga2["LON"] = data_gga2["LON"].apply(convert2_decimalDegree).round(5) * data_gga2["LON(unit)"].apply(coordinate_sign)
    del data_gga2["LON(unit)"] 

    return data_gga2

def save_csv(input_file_name, variable):
    output_file_name = input_file_name[:-4]+".pos"
    variable.to_csv(output_files_path + output_file_name, index=False, encoding="utf-8")
    
    return "Ok!"

def main():
    list_input_files = glob.glob(input_files_path+'*.201') # List all the files of the input directory
    if len(list_input_files)>0:
        for i in range(len(list_input_files)):
            file_name = list_input_files[i][len(input_files_path):] # Get the file's name

            dframe_nmea = read_nmea(file_name)
            dframe_lisn = nmea2lisn(dframe_nmea)
            save_csv(file_name, dframe_lisn)

if __name__ == '__main__':
    main()