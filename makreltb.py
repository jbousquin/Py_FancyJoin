# ---------------------------------------------------------------------------
# Script name:  makreltb.py
# Created on:  August 26, 2016
#
# This script reads the Cape_Cod_Merged table and creates csv files to be
# used as intermediate relate tables.
#
# Done for a work request from Marisa Mazzotta.  Use the Table to Relationship
# Class tool to create relationships between the Cape_Cod_Merged layer and
# the other layers of the public access data.
#
# Edited on September 2, 2016 to use an updated version of the Cape_Cod_Merged
# layer (Cape_Cod_Merged2).
#
# Edited 11/7/2016
# Justin Bousquin
# Added loops and params to make easier to functionalize
# ---------------------------------------------------------------------------

# Import system modules
#import arcpy, sys, string, os, time
import arcpy, sys, string, os, time, re
import csv
from time import localtime, strftime
from arcpy import da

# Local variable definitions
#merged result table
capemrgd = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\Cape_Cod_Merged2"
#csv workspace
workdir = "D:\\Projects\\mazzotta\\capecod3\\"

#out gdb
capegdb = os.path.dirname(capemrgd) + os.sep

#capegdb = "D:\\Projects\\mazzotta\\capecod\\capetest1.gdb\\"
#capegdb = "D:\\Projects\\mazzotta\\capecod2\\capecod2.gdb\\"
#capegdb = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\"  # Geodatabase with updated Cape Cod Merged layer (9/2/16)
#workdir = "D:\\Projects\\mazzotta\\capecod\\" # Location of csv files
#workdir = "D:\\Projects\\mazzotta\\capecod3\\" # Location of csv files (9/2/16)
#arcpy.env.workspace = "D:\\Projects\\mazzotta\\capecod3\\"
#capemrgd = "D:\\Projects\\mazzotta\\capecod2\\capecod2.gdb\\Cape_Cod_Merged"
#capemrgd = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\Cape_Cod_Merged2"
#capemrgd = "D:\\Projects\\mazzotta\\capecod\\capetest1.gdb\\CC_Merge_Test"

#list of input FCs (Tables)
lst_tables = ["BarnstableWW", "FalmouthWW", "HealthDept_CC", "MashpeeWW", "MORIS_boatramps", "Sandwich_beaches", "Sandwich_boatramps",
              "EPA_beaches", "MORIS_beaches", "YarmouthWW_line", "YarmouthWW_poly"]

try:

    print "Starting makreltb.py at " + strftime("%H:%M:%S", localtime()) + "\n"

    # Check to see if field RelateId exists in the public access data layers, if not, add the field and calc it equal to OBJECTID
    #for pubaclyr in ["Cape_Cod_Merged2","BarnstableWW","FalmouthWW","HealthDept_CC","MashpeeWW","MORIS_boatramps","Sandwich_beaches","Sandwich_boatramps","EPA_beaches","MORIS_beaches","YarmouthWW_line","YarmouthWW_poly"]:
    for pubaclyr in lst_tables:
        arcpy.MakeFeatureLayer_management(capegdb + pubaclyr, "publayer")
        desc = arcpy.Describe("publayer")
        fieldInfo = desc.fieldInfo
        fldIndex = fieldInfo.findFieldByName("RelateId")
        if not fldIndex > 0:
            #print "Shouldn't be processing this code\n"
            arcpy.AddField_management(capegdb + pubaclyr, "RelateId", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(capegdb + pubaclyr, "RelateId", "[OBJECTID]", "VB", "")  #Set field RelateId to OBJECTID
        arcpy.Delete_management("publayer", "")

#JJB: re-wrote these to name based on original table name, creating loop from lst_tables
    # Create .csv files with header line to be populated later in script
    #this required an ordered list of Orig_ID headers in the csv too (this will become automated later since it gets deleted anyway
    csv_ID_lst = ["BrnRelId", "FalmRelId", "HlthRelId", "MashRelId", "MBrRelId", "SnBchRelId", "SanBrRelId", "EpaRelId", "MBchRelId", "YarLnRelId", "YarPlRelId"]
    csv_lst = []
    i = 0
    for table in lst_tables:
        csv_name = table + ".csv"
        #if the csv already exists, delete it
        if arcpy.Exists(workdir + csv_name):
            arcpy.Delete_management(workdir + csv_name, "")
        csv_write = open(workdir + csv_name, "w")
        csv_write.write("RelateID," + csv_name + csv_ID_lst[i] + "\n")
        csv_lst.append(workdir + csv_name)
        i+=1
    # Create Department of Health table
    #if arcpy.Exists(workdir + "healthtb.csv"):
    #    arcpy.Delete_management(workdir + "healthtb.csv", "")
    #helthout = open(workdir + "healthtb.csv","w")
    #helthout.write("RelateId,HlthRelId\n")
    # Create EPA beaches table
    #if arcpy.Exists(workdir + "epatable.csv"):
    #    arcpy.Delete_management(workdir + "epatable.csv", "")
    #epaout = open(workdir + "epatable.csv","w")
    #epaout.write("RelateId,EpaRelId\n")
    # Create MORIS beaches table
    #if arcpy.Exists(workdir + "morbchtb.csv"):
    #    arcpy.Delete_management(workdir + "morbchtb.csv", "")
    #mrbchout = open(workdir + "morbchtb.csv","w")
    #mrbchout.write("RelateId,MBchRelId\n")
    # Create MORIS boat ramps table
    #if arcpy.Exists(workdir + "morbrtab.csv"):
    #    arcpy.Delete_management(workdir + "morbrtab.csv", "")
    #morbrout = open(workdir + "morbrtab.csv","w")
    #morbrout.write("RelateId,MBrRelId\n")
    # Create Barnstable WW table
    #if arcpy.Exists(workdir + "barnstab.csv"):
    #    arcpy.Delete_management(workdir + "barnstab.csv", "")
    #barnsout = open(workdir + "barnstab.csv","w")
    #barnsout.write("RelateId,BrnRelId\n")
    # Create Yarmouth WW line table
    #if arcpy.Exists(workdir + "yarlntab.csv"):
    #    arcpy.Delete_management(workdir + "yarlntab.csv", "")
    #yarlnout = open(workdir + "yarlntab.csv","w")
    #yarlnout.write("RelateId,YarLnRelId\n")
    # Create Yarmouth WW poly table
    #if arcpy.Exists(workdir + "yarpltab.csv"):
    #    arcpy.Delete_management(workdir + "yarpltab.csv", "")
    #yarplout = open(workdir + "yarpltab.csv","w")
    #yarplout.write("RelateId,YarPlRelId\n")
    # Create Mashpee WW table
    #if arcpy.Exists(workdir + "mashptab.csv"):
    #    arcpy.Delete_management(workdir + "mashptab.csv", "")
    #mashpout = open(workdir + "mashptab.csv","w")
    #mashpout.write("RelateId,MashRelId\n")
    # Create Sandwich beaches table
    #if arcpy.Exists(workdir + "snbchtab.csv"):
    #    arcpy.Delete_management(workdir + "snbchtab.csv", "")
    #snbchout = open(workdir + "snbchtab.csv","w")
    #snbchout.write("RelateId,SnBchRelId\n")
    # Create Sandwich boat ramp table
    #if arcpy.Exists(workdir + "sanbrtab.csv"):
    #    arcpy.Delete_management(workdir + "sanbrtab.csv", "")
    #sanbrout = open(workdir + "sanbrtab.csv","w")
    #sanbrout.write("RelateId,SanBrRelId\n")
    # Create Falmouth WW table
    #if arcpy.Exists(workdir + "falmtab.csv"):
    #    arcpy.Delete_management(workdir + "falmtab.csv", "")
    #falmout = open(workdir + "falmtab.csv","w")
    #falmout.write("RelateId,FalmRelId\n")

#JJB: update to use data access search cursor (faster)
#JJB: update to loop until last numeric (e.g. create list of fields, create list where field = "HD_*", for field in fields...)
#JJB: may change to lists instead of csv
    # Cursor reads each record of Cape Cod merged data layer and writes a line to respective .csv
    # file if there is a non-zero value for that data set
    fields_lst = arcpy.ListFields(capemrdgd) #listing fields so that number of duplicate fields is not static
    field_abr_lst = [ "Barnstable", "Falmouth", "HD_", "Mashpee", "BR_", "San_beach", "San_BOR", "EPA_", "MORIS_", "Yar_line", "Yar_poly"]
#abr order must line up with related csv order in csv_lst, which was generated based on lst_tables:
#["BarnstableWW", "FalmouthWW", "HealthDept_CC", "MashpeeWW", "MORIS_boatramps", "Sandwich_beaches", "Sandwich_boatramps",
#              "EPA_beaches", "MORIS_beaches", "YarmouthWW_line", "YarmouthWW_poly"]
    i = 0
    for abr in field_abr_lst: #for each abreviation in the list
        current_csv = csv_lst[i] #set which csv table to write to
        #make a new list of fields that use that abreviation, and "RelateID" at the start
        abr_ID_fields = ["RelateId"] + [field for field in fields_lst if field.startswith(abr)]
        with arcpy.da.SearchCursor(capemrgd, abr_ID_fields) as cursor: #create a cursor with "RelateID" and the list of fields
            for row in cursor:
                for index in range(1, len(abr_ID_fields)):                  
                    if row[index] <>0:
                        current_csv.write(str(row[0]) + "," + str(row[index]) + "\n")
        current_csv.close()
            
    #caperows = arcpy.SearchCursor(capemrgd)
    #caperow = caperows.next()
    #while caperow:
        # Process Department of Health data
    #    if caperow.HD_1 <> 0:
    #        helthout.write(str(caperow.RelateId) + "," + str(caperow.HD_1) + "\n")
    #    if caperow.HD_2 <> 0:
    #        helthout.write(str(caperow.RelateId) + "," + str(caperow.HD_2) + "\n")
    #    if caperow.HD_3 <> 0:
    #        helthout.write(str(caperow.RelateId) + "," + str(caperow.HD_3) + "\n")
        # Process EPA data
    #    if caperow.EPA_1 <> 0:
    #        epaout.write(str(caperow.RelateId) + "," + str(caperow.EPA_1) + "\n")
    #    if caperow.EPA_3 <> 0:
    #        epaout.write(str(caperow.RelateId) + "," + str(caperow.EPA_3) + "\n")
    #    if caperow.EPA_4 <> 0:
    #        epaout.write(str(caperow.RelateId) + "," + str(caperow.EPA_4) + "\n")
        # Process MORIS beaches data
    #    if caperow.MORIS_1 <> 0:
    #        mrbchout.write(str(caperow.RelateId) + "," + str(caperow.MORIS_1) + "\n")
    #    if caperow.MORIS_2 <> 0:
    #        mrbchout.write(str(caperow.RelateId) + "," + str(caperow.MORIS_2) + "\n")
    #    if caperow.MORIS_3 <> 0:
    #        mrbchout.write(str(caperow.RelateId) + "," + str(caperow.MORIS_3) + "\n")
        # Process MORIS boat ramp data
    #    if caperow.BR_1 <> 0:
    #        morbrout.write(str(caperow.RelateId) + "," + str(caperow.BR_1) + "\n")
        # Process Barnstable WW data
    #    if caperow.Barnstable1 <> 0:
    #        barnsout.write(str(caperow.RelateId) + "," + str(caperow.Barnstable1) + "\n")
        # Process Yarmouth WW line data
    #    if caperow.Yar_line1 <> 0:
    #        yarlnout.write(str(caperow.RelateId) + "," + str(caperow.Yar_line1) + "\n")
    #    if caperow.Yar_line2 <> 0:
    #        yarlnout.write(str(caperow.RelateId) + "," + str(caperow.Yar_line2) + "\n")
        # Process Yarmouth WW poly data
    #    if caperow.Yar_poly1 <> 0:
    #        yarplout.write(str(caperow.RelateId) + "," + str(caperow.Yar_poly1) + "\n")
        # Process Mashpee WW data
    #    if caperow.Mashpee1 <> 0:
    #        mashpout.write(str(caperow.RelateId) + "," + str(caperow.Mashpee1) + "\n")
        # Process Sandwich beaches data
    #    if caperow.San_beach1 <> 0:
    #        snbchout.write(str(caperow.RelateId) + "," + str(caperow.San_beach1) + "\n")
    #    if caperow.San_beach2 <> 0:
    #        snbchout.write(str(caperow.RelateId) + "," + str(caperow.San_beach2) + "\n")
        # Process Sandwich boat ramp data
    #    if caperow.San_BOR1 <> 0:
    #        sanbrout.write(str(caperow.RelateId) + "," + str(caperow.San_BOR1) + "\n")
        # Process Falmouth WW data
    #    if caperow.Falmouth1 <> 0:
    #        falmout.write(str(caperow.RelateId) + "," + str(caperow.Falmouth1) + "\n")

    #    caperow = caperows.next()

    #del caperow
    #del caperows

    #helthout.close()
    #epaout.close()
    #mrbchout.close()
    #morbrout.close()
    #barnsout.close()
    #yarlnout.close()
    #yarplout.close()
    #mashpout.close()
    #snbchout.close()
    #sanbrout.close()
    #falmout.close()

    # Convert csv files to geodatabase tables
#JJB: see if we can't tighten this up using init params above and loop
#may use dict to associate each field with its origin table
#create list of int tables, note they are ordered based on lst_table order
#["BarnstableWW", "FalmouthWW", "HealthDept_CC", "MashpeeWW", "MORIS_boatramps", "Sandwich_beaches", "Sandwich_boatramps",
#              "EPA_beaches", "MORIS_beaches", "YarmouthWW_line", "YarmouthWW_poly"]
#this could be fixed by automated naming based on field abreivations (first 6 letters of table or field_abr_lst)
    int_tables_lst = ["BarnIntTab", "FalmIntTab", "HlthIntTab", "MashIntTab", "MbrmIntTab", "SbchIntTab", "SbrIntTab", "EpaIntTab", "MbchIntTab", "YlinIntTab", "YpolIntTab"] 
    i = 0 #reset iterator
    #string for first part of field mapping string
    field_mapping_str_start = "RelateId \"RelateId\""
    #loop over int tables, delete if it exists and then do csv_Table to Table
    for int_table in in_tables_lst:
        if arcpy.Exists(capegdb + int_table):
            arcpy.Delete_management(capegdb + int_table)
        #create field mapping string
        field_mapping = str('{0} \"{0}\"{1}{2},{0},-1,-1;{3} \"{3}\"{1}{2},{3},-1,-1'.format("RelateId", " true true false 4 Double 0 0 ,First,#,", csv_lst[i], csv_ID_lst[i])) 
                            '
        arcpy.TableToTable_conversion(csv_lst[i], capegdb, int_table, "", field_mapping, "")
            
    #if arcpy.Exists(capegdb + "HlthIntTab"):
    #    arcpy.Delete_management(capegdb + "HlthIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "healthtb.csv", capegdb, "HlthIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\healthtb.csv,RelateId,-1,-1;HlthRelId \"HlthRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\healthtb.csv,HlthRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "EpaIntTab"):
    #    arcpy.Delete_management(capegdb + "EpaIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "epatable.csv", capegdb, "EpaIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\epatable.csv,RelateId,-1,-1;EpaRelId \"EpaRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\epatable.csv,EpaRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "MbchIntTab"):
    #    arcpy.Delete_management(capegdb + "MbchIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "morbchtb.csv", capegdb, "MbchIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\morbchtb.csv,RelateId,-1,-1;MBchRelId \"MBchRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\morbchtb.csv,MBchRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "MbrmIntTab"):
    #    arcpy.Delete_management(capegdb + "MbrmIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "morbrtab.csv", capegdb, "MbrmIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\morbrtab.csv,RelateId,-1,-1;MBrRelId \"MBrRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\morbrtab.csv,MBrRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "BarnIntTab"):
    #    arcpy.Delete_management(capegdb + "BarnIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "barnstab.csv", capegdb, "BarnIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\barnstab.csv,RelateId,-1,-1;BrnRelId \"BrnRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\barnstab.csv,BrnRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "YlinIntTab"):
    #    arcpy.Delete_management(capegdb + "YlinIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "yarlntab.csv", capegdb, "YlinIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\yarlntab.csv,RelateId,-1,-1;YarLnRelId \"YarLnRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\yarlntab.csv,YarLnRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "YpolIntTab"):
    #    arcpy.Delete_management(capegdb + "YpolIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "yarpltab.csv", capegdb, "YpolIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\yarpltab.csv,RelateId,-1,-1;YarPlRelId \"YarPlRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\yarpltab.csv,YarPlRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "MashIntTab"):
    #    arcpy.Delete_management(capegdb + "MashIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "mashptab.csv", capegdb, "MashIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\mashptab.csv,RelateId,-1,-1;MashRelId \"MashRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\mashptab.csv,MashRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "SbchIntTab"):
    #    arcpy.Delete_management(capegdb + "SbchIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "snbchtab.csv", capegdb, "SbchIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\snbchtab.csv,RelateId,-1,-1;SnBchRelId \"SnBchRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\snbchtab.csv,SnBchRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "SbrIntTab"):
    #    arcpy.Delete_management(capegdb + "SbrIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "sanbrtab.csv", capegdb, "SbrIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\sanbrtab.csv,RelateId,-1,-1;SanBrRelId \"SanBrRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\sanbrtab.csv,SanBrRelId,-1,-1", "")
    #if arcpy.Exists(capegdb + "FalmIntTab"):
    #    arcpy.Delete_management(capegdb + "FalmIntTab", "")
    #arcpy.TableToTable_conversion(workdir + "falmtab.csv", capegdb, "FalmIntTab", "", "RelateId \"RelateId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\falmtab.csv,RelateId,-1,-1;FalmRelId \"FalmRelId\" true true false 4 Double 0 0 ,First,#,D:\\Projects\\mazzotta\\capecod3\\falmtab.csv,FalmRelId,-1,-1", "")
#JJB: STOPPED MAKING EDITS HERE 11/15/2016
    # Local variables:
    #CC_Merge_Test = "D:\\Projects\\mazzotta\\capecod\\capetest1.gdb\\CC_Merge_Test"
    #Cape_Cod_Merged = "D:\\Projects\\mazzotta\\capecod2\\capecod2.gdb\\Cape_Cod_Merged"
    Cape_Cod_Merged = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\Cape_Cod_Merged2"
#JJB: may be a more elegant way of doing this... but 5 lines is moving in the right direction
    lst_tableNames =["BarnstableWW", "FalmouthWW", "HealthDept_CC", "MashpeeWW", "MORIS_boatramps", "Sandwich_beaches",
                     "Sandwich_boatramps", "EPA_beaches", "MORIS_beaches", "YarmouthWW_line", "YarmouthWW_poly"]
    lst_tableSource = []
    # Create variable names for data sources
    for table in lst_tableNames:
        lst_tableSource.Append(capegdb + table)
    # Create variable names for data sources
    #BarnstableWW = capegdb + "BarnstableWW"
    #FalmouthWW = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\FalmouthWW"
    #HealthDept_CC = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\HealthDept_CC"
    #MashpeeWW = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MashpeeWW"
    #MORIS_boatramps = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MORIS_boatramps"
    #Sandwich_beaches = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\Sandwich_beaches"
    #Sandwich_boatramps = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\Sandwich_boatramps"
    #EPA_beaches = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\EPA_beaches"
    #MORIS_beaches = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MORIS_beaches"
    #YarmouthWW_line = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\YarmouthWW_line"
    #YarmouthWW_poly = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\YarmouthWW_poly"
    # Create variable names for geodatabase tables created from csv files
    lst_csvTables = ["HlthIntTab", "EpaIntTab", "MbchIntTab", "MbrmIntTab", "BarnIntTab", "YlinIntTab", "YpolIntTab", "MashIntTab", "SbchIntTab", "SbrIntTab", "FalmIntTab"]  ]
    lst_csvSource = []
    for relTable in lst_relTables:
        lst_ralSource.Append(workdir + relTable)
    # Create variable names for geodatabase tables created from csv files
    #HlthIntTab = capegdb + "HlthIntTab"
    #EpaIntTab = capegdb + "EpaIntTab"
    #MbchIntTab = capegdb + "MbchIntTab"
    #MbrmIntTab = capegdb + "MbrmIntTab"
    #BarnIntTab = capegdb + "BarnIntTab"
    #YlinIntTab = capegdb + "YlinIntTab"
    #YpolIntTab = capegdb + "YpolIntTab"
    #MashIntTab = capegdb + "MashIntTab"
    #SbchIntTab = capegdb + "SbchIntTab"
    #SbrIntTab = capegdb + "SbrIntTab"
    #FalmIntTab = capegdb + "FalmIntTab"

    #HlthIntTab = "D:\\Projects\\mazzotta\\capecod\\capetest1.gdb\\HlthIntTab"
    #CC_Merge_Test_HealthDept_CC = "D:\\Projects\\mazzotta\\capecod\\capetest1.gdb\\CC_Merge_Test_HealthDept_CC"

    # Create variable names for the relationship class arguments
    lst_relClass = ["BarnRelCl", "FalmRelCl", "HealthRelCl", "MashRelCl", "MorbrRelCl", "SanBchRelCl", "SanBrRelCl", "EPARelCl",
                    "MorbchRelCl", "YarlinRelCl", "YarpolRelCl"]
    lst_relClass_source = []
    for relClass in lst_relClass:
        lst_relClass_source.Append(capegdb + relClass)
    #BarnRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\BarnRelCl"
    #FalmRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\FalmRelCl"
    #HealthRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\HealthRelCl"
    #MashRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MashRelCl"
    #MorbrRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MorbrRelCl"
    #SanBchRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\SanBchRelCl"
    #SanBrRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\SanBrRelCl"
    #EPARelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\EpaRelCl"
    #MorbchRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\MorbchRelCl"
    #YarlinRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\YarlinRelCl"
    #YarpolRelCl = "D:\\Projects\\mazzotta\\capecod3\\capecod3.gdb\\YarpolRelCl"

    # Create relationship classes for each data source
    # Process: Table To Relationship Class
    #arcpy.TableToRelationshipClass_management(CC_Merge_Test, HealthDept_CC, CC_Merge_Test_HealthDept_CC, "SIMPLE", "HealthDept_CC", "CC_Merge_Test", "NONE", "ONE_TO_MANY", HlthIntTab, "RelateId;HlthRelId", "RelateId", "RelateId", "RelateId", "HlthRelId")
    #arcpy.TableToRelationshipClass_management(CC_Merge_Test, HealthDept_CC, CC_Merge_Test_HealthDept_CC, "SIMPLE", "HealthDept_CC", "CC_Merge_Test", "NONE", "ONE_TO_MANY", HlthIntTab, "RelateId;HlthRelId", "RelateId", "RelateId", "RelateId", "HlthRelId")
    
    for item in lst_relClass:
        if arcpy.Exists(item):
            arcpy.Delete_management(item, "")
    #var1 = BarnstableWW
    #var2 = "BarnstableWW"
    #var3 = BarnIntTab
    #var4 = "RelateId;BrnRelId"
    #var5 = BrnRelId
        arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, var1, item, "SIMPLE", var2, "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", var3, var4, "RelateId", "RelateId", "RelateId", var5)


    if arcpy.Exists(BarnRelCl):
        arcpy.Delete_management(BarnRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, BarnstableWW, BarnRelCl, "SIMPLE", "BarnstableWW", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", BarnIntTab, "RelateId;BrnRelId", "RelateId", "RelateId", "RelateId", "BrnRelId")
    if arcpy.Exists(FalmRelCl):
        arcpy.Delete_management(FalmRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, FalmouthWW, FalmRelCl, "SIMPLE", "FalmouthWW", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", FalmIntTab, "RelateId;FalmRelId", "RelateId", "RelateId", "RelateId", "FalmRelId")
    if arcpy.Exists(HealthRelCl):
        arcpy.Delete_management(HealthRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, HealthDept_CC, HealthRelCl, "SIMPLE", "HealthDept_CC", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", HlthIntTab, "RelateId;HlthRelId", "RelateId", "RelateId", "RelateId", "HlthRelId")
    if arcpy.Exists(MashRelCl):
        arcpy.Delete_management(MashRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, MashpeeWW, MashRelCl, "SIMPLE", "MashpeeWW", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", MashIntTab, "RelateId;MashRelId", "RelateId", "RelateId", "RelateId", "MashRelId")
    if arcpy.Exists(MorbrRelCl):
        arcpy.Delete_management(MorbrRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, MORIS_boatramps, MorbrRelCl, "SIMPLE", "MORIS_boatramps", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", MbrmIntTab, "RelateId;MBrRelId", "RelateId", "RelateId", "RelateId", "MBrRelId")
    if arcpy.Exists(SanBchRelCl):
        arcpy.Delete_management(SanBchRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, Sandwich_beaches, SanBchRelCl, "SIMPLE", "Sandwich_beaches", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", SbchIntTab, "RelateId;SnBchRelId", "RelateId", "RelateId", "RelateId", "SnBchRelId")
    if arcpy.Exists(SanBrRelCl):
        arcpy.Delete_management(SanBrRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, Sandwich_boatramps, SanBrRelCl, "SIMPLE", "Sandwich_boatramps", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", SbrIntTab, "RelateId;SanBrRelId", "RelateId", "RelateId", "RelateId", "SanBrRelId")
    if arcpy.Exists(EPARelCl):
        arcpy.Delete_management(EPARelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, EPA_beaches, EPARelCl, "SIMPLE", "EPA_beaches", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", EpaIntTab, "RelateId;EpaRelId", "RelateId", "RelateId", "RelateId", "EpaRelId")
    if arcpy.Exists(MorbchRelCl):
        arcpy.Delete_management(MorbchRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, MORIS_beaches, MorbchRelCl, "SIMPLE", "MORIS_beaches", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", MbchIntTab, "RelateId;MBchRelId", "RelateId", "RelateId", "RelateId", "MBchRelId")
    if arcpy.Exists(YarlinRelCl):
        arcpy.Delete_management(YarlinRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, YarmouthWW_line, YarlinRelCl, "SIMPLE", "YarmouthWW_line", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", YlinIntTab, "RelateId;YarLnRelId", "RelateId", "RelateId", "RelateId", "YarLnRelId")
    if arcpy.Exists(YarpolRelCl):
        arcpy.Delete_management(YarpolRelCl, "")
    arcpy.TableToRelationshipClass_management(Cape_Cod_Merged, YarmouthWW_poly, YarpolRelCl, "SIMPLE", "YarmouthWW_poly", "Cape_Cod_Merged2", "NONE", "ONE_TO_MANY", YpolIntTab, "RelateId;YarPlRelId", "RelateId", "RelateId", "RelateId", "YarPlRelId")

    print "Completed makreltb.py at " + strftime("%H:%M:%S", localtime()) + "\n"

except:
    import traceback, sys

    helthout.close()
    epaout.close()
    mrbchout.close()
    morbrout.close()
    barnsout.close()
    yarlnout.close()
    yarplout.close()
    mashpout.close()
    snbchout.close()
    sanbrout.close()
    falmout.close()

    # get the traceback object
    tb = sys.exc_info()[2]

    # tbinfo contains the failure's line number and the line's code
    tbinfo = traceback.format_tb(tb)[0]

    print tbinfo          # provides where the error occurred
    print sys.exc_type    # provides the type of error
    #print sys.exc_Value   # provides the error message
