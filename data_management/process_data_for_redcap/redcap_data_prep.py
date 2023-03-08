import csv
import pandas as pd

def redcap_get_variables(source_file_path,out_path,mode=False,form_id="form_1"):
    """
    
    This function takes in an exisitng CSV Data Set and assists in generating
    a REDCap compatible Data Dictionary
    
    Parameters
    ----------

    source_file_path : Path to CSV file
        Path of the csv file we want to alter
    out_path: Path to CSV file
        Path of the exported file we want to create
    mode: STRING
        "txt" or "csv"
            -default of false triggers a check on any extension provided in the 
            out_file_path
    form_id: STRING
        Form ID in Data Dictionary (to ensure matching correct data set)
            - default is "form_1"

    Returns
    -------
        MODE: "txt": TXT file with each header from the source file
                    separated by a new line
              "csv": CSV template of a REDCap Data Dictionary, with all
                     fields from the source data entered as "Field Label"
    """
    #Open and read our CSV and isolate our headers
    with open(source_file_path,encoding="utf-8-sig") as file:
        df = pd.read_csv(file)
        headers = ["record_id"] + df.columns.to_list()
    
    #Checking for mode from outfile if not otherwise specified
    if not mode:
        extension = out_path[-3:]
        if extension == "csv":
            mode = "csv"
        elif extension == "txt":
            mode = "txt"
        else:
            print("Failed to specify a mode")
            return ""
    
    #TXT Mode: Printing headers to txt
    if mode == "txt":
        with open(out_path,"w") as outfile:
            for item in headers:
                outfile.write(item+"\n")
        return headers
    
    #CSV MODE: Generating DataFrame to build framework CSV
    if mode == "csv":
        fields = ['Variable / Field Name','Form Name','Section Header',
                  'Field Type','Field Label', 
                  'Choices, Calculations, OR Slider Labels','Field Note',
                  'Text Validation Type OR Show Slider Number',
                  'Text Validation Min','Text Validation Max','Identifier?',
                  'Branching Logic (Show field only if...)','Required Field?',
                  'Custom Alignment','Question Number (surveys only)',
                  'Matrix Group Name','Matrix Ranking?','Field Annotation']
       
        df = pd.DataFrame(index=range(len(headers)),columns=fields)
        
        df["Field Label"]=headers
        df["Form Name"] = form_id*len(df)
        df["Field Type"] = "text" *len(df)
        
        with open(out_path,"w") as outfile:
            df.to_csv(outfile,encoding="utf-8")
        return df
    
    


def redcap_filemod_variables(source_acro,source_file_path,data_dict_path,form_id="form_1",out_path=False):
    """
    
    This function modifies source data CSV variables to match a REDCap Data 
    Dictionary CSV; Should help automate processing for upload
    
    Parameters
    ----------
    source_acro: STRING
        Acronym for the source in the combined data set
            - using "ms" for MedStar
            - using "aps" for APS
    source_file_path : Path to CSV file
        Path of the csv file we want to alter
    data_dict_path: Path to CSV file
        Path to REDCap Data Dictionary File
    form_id: STRING
        Form ID in Data Dictionary (to ensure matching correct data set)
        - Default is "form_1"
    out_path: Path to CSV file
        Path of the exported CSV file we want to create
        -default of FALSE does not export

    Returns
    -------
    Dataframe of the contents of file(filepath) with column headers modified by 
        file(variablepath)
        
    If outpath specified, saved in a new file(outpath)
    """
    
    #get source data as pandas data frame
    #this allows renaming and reorganizing variables without using up memory
    
    with open(source_file_path,encoding="utf-8-sig") as file:
        df = pd.read_csv(file)
        #Just uses the data frame index to assign a "record id" for now
        index = df.index.to_list()
        index_var = source_acro+"_index"
        df[index_var]=index
        #record_id here will just be a placeholder
        df["record_id"]=index
    
    #Data Dictionary should be small enough to allow O(N) processing without issue
    #Iterate to get dictionary to map renaming of variables
    #Iteration also allows us to get the desired column order in the produced data frame
    with open(data_dict_path,"r") as variables:
        variable_map = {}
        columns = ["record_id"]
        reader = csv.reader(variables)
        #this just skips over the first 2 rows:
        #data dictionary header, record_id
        i=0
        while i < 2:
            next(reader)
            i+=1
        for row in reader:
            #print(f"reading 0:{row[0]}, 4: {row[4]}")
            if row[1]==form_id:
                if row[0][-6:] !="_index":
                    #don't need to add any "index" variables to our map
                    variable_map[row[4]]=row[0]
                columns.append(row[0])
    #Rename and reorder variables (all rows should stay in same order)
    df = df.rename(columns=variable_map)
    df = df[columns]
    #save to file if desired
    if out_path:
        with open(out_path,"w",encoding="utf-8-sig") as outfile:
            df.to_csv(outfile,index=False,lineterminator="\n")
    return df






