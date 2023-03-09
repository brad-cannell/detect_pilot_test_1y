## IMPORTS ##
import csv
import pandas as pd
import os

"""
Versioning:
    
Python: 3.9.12
CSV: 1.0
Pandas: 1.5.2
OS: Python Standard Library
"""

## MAIN ##

def main():
    #VARIABLES FOR TYPING IN THE CODE ITSELF, IF DESIRED
    mypath = ""
    data_tuple = ("","","")
    output_tuple = ("","")
    processing = False
    templates = False
    
    #USER PROMPT TREE FOR DESIRED ACTION
    while not processing:
        processing = input("Do you have completed Data Dictionaries? [y/n]: ")
        if processing.upper().strip() == "Y":
            processing = True
            
            templates = False
            while not templates:
                templates = input("Do you want to regenerate templates while processing? [y/n]: ")
                if templates.upper().strip() == "Y":
                    templates = True
                elif templates.upper().strip() == "N":
                    templates = False
                    break
                else:
                    print ("Not a valid entry, please try again")
                    templates = False
                    
        elif processing.upper().strip() == "N":
            templates = True
            processing = False
            break
        else:
            print("Not a valid entry, please try again")
            processing = False
            
    source_path, output_path, dict_path = package_paths(mypath,data_tuple,output_tuple)   
    if templates:
        get_templates(source_path,output_path)
    if processing:
        process_files(source_path,dict_path,output_path)


                    
## FUNCTIONS ##
def redcap_get_variables(source_file_path,out_path,mode=False,form_id="form_1"):
    """
    
    This function takes in an exisitng CSV Data Set and assists in generating
    a REDCap compatible Data Dictionary by extracting all variable names
    
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
        df["Form Name"] = form_id
        #Sets value of "record_id" to form_1 for consistency
        df["Form Name"].iloc[0] = "form_1"
        df["Field Type"] = "text"
        
        with open(out_path,"w") as outfile:
            df.to_csv(outfile,encoding="utf-8",mode="w",index=False,lineterminator="\n")
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
    #this allows renaming and reorganizing variables without using up too much memory
    
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

def get_paths_console():
    """
    
    Creates a console-based entry for package_paths
    
    Parameters
    ----------

    None: All string entries from console prompts

    Returns
    -------
    Results of package_paths on entered paths:
    
    source_path: PATH
        Path for source data files
        
    output_path: PATH
        Path for output data files
    
    dict_dir: PATH
        Path for completed data dictionary templates
    
    """
    #Get info from console
    project_directory = input("Enter Main Project Path: ")
    data_dir = input("Enter Path to Main Data Directory in Project: ")
    data_subdir = input("Enter Specific Subdirectory of Data to Process (if needed): ")
    dict_dir = input("Enter Data Subdirectory For Completed Templates: ")
    output_dir = input("Enter Path to Desired Output File Directory in Project: ")
    output_subdir = input("Enter Any Specific Subdirectory for Output Files (optional): ")

    #Package up data
    data_tuple = (data_dir,data_subdir,dict_dir)
    output_tuple = (output_dir,output_subdir)
    return package_paths(project_directory,data_tuple,output_tuple)


def package_paths(project_directory=False,data_tuple=False,output_tuple=False):
    """
    
    Uses OS to cleanly process path information for data processing.
    
    If any fields are missing, initiates get_paths_console instead
    
    Parameters
    ----------

    project_directory: PATH
        Main project directory where data is found
        
    data_tuple: TUPLE of (data_dir, data_subdir)
        data_dir: PATH
            Path to primary data directory in project
        data_subdir: PATH
            Path to specific subdirectory within data directory of project
        dict_dir: PATH
            Path to specific subdirectory within data directory which will
            hold completed Data Dictionary Templates

    output_tuple: TUPLE of (output_dir, output_subdir)
        output_dir: PATH
            Path to primary output directory in project
        output_subdir: PATH
            Path to specific subdirectory within output directory of project

    Returns
    -------
    Results of package_paths on entered paths:
    
    source_path: PATH
        Path for source data files
        
    output_path: PATH
        Path for output data files
    
    dict_path: PATH
        Path for completed Data Dictionary Templates
    
    """    
    if not (project_directory and data_tuple and output_tuple):
        return get_paths_console()
    
    
    #unpack and clean arguments
    project_path = os.path.realpath(project_directory)
    data_dir, data_subdir, dict_dir = data_tuple
    output_dir, output_subdir = output_tuple
    
    #Build desired paths
    if data_subdir:
        source_path = os.path.join(project_path,data_dir,data_subdir)
        dict_path = os.path.join(source_path,dict_dir)
    else:
        source_path = os.path.join(project_path,data_dir)
        dict_path = os.path.join(source_path,dict_dir)
    
    if output_subdir:
        output_path = os.path.join(project_path,output_dir,output_subdir)
    else:
        output_path = os.path.join(project_path,output_dir)
    
    if not os.path.isdir(source_path):
        #if source directory does not exist, raise error
        raise FileNotFoundError("Source Path Not Found")
    if not os.path.isdir(output_path):
        #if output directory does not exist, try to make it
        #will raise errors if unable
            os.makedirs(output_path)
    
    paths = source_path, output_path, dict_path
    return paths

def get_templates(source_path,output_path):
    """
    
    Performs REDCap template processing on all CSV files in a path
    
    Parameters
    ----------

    source_path: PATH
        Path of source data CSV files
        
    output_path: PATH
        Desired path for output files to be stored

    Returns
    -------
    
    Generates both .txt and .csv file products of redcap_get_variables for 
    all files in source_path, and stores them in output_path
    
    """
    source_files = os.listdir(source_path)
    i = 2
    for file in source_files:
        file_path = os.path.join(source_path,file)
        if not os.path.isdir(file_path):
            file_name = file.split(".")[0]

            form_id = "form_"+str(i)
            i+=1
            txt_path = os.path.join(output_path,(file_name+"_headers.txt"))
            csv_path = os.path.join(output_path,(file_name+"_redcap_datadictionary_template.csv"))
            
            redcap_get_variables(file_path, txt_path, form_id = form_id)
            redcap_get_variables(file_path, csv_path, form_id = form_id)
            
    print(f"Done with initial processing for {i-2} files")

def process_files(source_path,dict_path,output_path):
    """
    
    Performs REDCap processing of source CSV files with REDCap DataDictionary
    as a template
    
    Parameters
    ----------

    source_path: PATH
        Path of source data CSV files
    
    dict_path: PATH
        Path of any complete REDCap DataDictionaries, in CSV Format
        
    output_path: PATH
        Desired path for output files to be stored

    Returns
    -------
    
    Generates a copy of the source file from source_path, 
    transformed by REDCap processing using a matching DataDictionary in dict_path,
    and stores it as a CSV file in the output_path
    
    """
    source_path = os.path.join(source_path)
    source_files = os.listdir(source_path)
    
    if os.path.isdir(dict_path):
        i=0
        #STOP IF DICT_PATH DOESN'T EXIST
        template_files = os.listdir(dict_path)
        for source_file in source_files:
            if source_file[:3].upper() == "APS":
                source_acro = "aps"
                form_id = "form_3"
            elif source_file[:7].upper() == "MEDSTAR":
                source_acro = "ms"
                form_id = "form_2"
            else:
                source_acro = ""
                form_id = "form_1"
            source_file_path = os.path.join(source_path,source_file)
            if not os.path.isdir(source_file_path):
                source_name = source_file.split(".")[0]
                source_len = len(source_name)
                for template in template_files:
                    if template[:source_len] == source_name:
                        #MATCHES BASED ON PREFIXES
                        template_path = os.path.join(dict_path,template)
                        if source_acro:
                            processed_name = source_name+"_redcap_processed.csv"
                            processed_path = os.path.join(output_path,processed_name)
                            redcap_filemod_variables(source_acro,source_file_path,template_path,form_id,processed_path)
                            i+=1
    print(f"REDCap formatting from DataDictionary processed for {i} source files")

if __name__ == "__main__":
    main()