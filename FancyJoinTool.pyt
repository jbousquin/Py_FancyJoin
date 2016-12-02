"""
#Name: Fancy Join
#Purpose: Save Sarina work and time
#Author: Justin Bousquin
#Date: 8/1/2016
#Version: 2.8
#Version Notes: fixed step 2 so that results would work better in step 3
"""

import os
import arcpy
from arcpy import da
from difflib import SequenceMatcher 

##########Functions##########
"""Distance Score
Purpose: calculate distance score and add field with this score"""
#Function notes: requires "NEAR_DIST" field
def distanceScore(joinFC):
    arcpy.AddField_management(joinFC, "DistScore", "DOUBLE")
    #maximum distance
    maxVal = arcpy.SearchCursor(joinFC, "", "", "", "NEAR_DIST" + " D").next().getValue("NEAR_DIST")
    #score = distance/max distance
    with arcpy.da.UpdateCursor(joinFC, ["NEAR_DIST", "DistScore"]) as cursor: 
        for row in cursor:
            if row[0] <0:
                row[1] = 0
            else:
                row[1] = 1-(row[0]/maxVal)
            cursor.updateRow(row)

"""Summary Score
Purpose: updates a FC to calculate the TotScore"""
def SummaryScore(joinFC, distW, nameW):
    arcpy.AddField_management(joinFC, "TotScore", "DOUBLE")
    with arcpy.da.UpdateCursor(joinFC, ["TotScore", "DistScore", "FldScore"]) as cursor:
        for row in cursor:
            row[0] = ((row[1]*distW) + (row[2]*nameW))/(1.0*(distW + nameW))
            cursor.updateRow(row)
    arcpy.AddMessage("Summary Scores Calculated")

"""Nested Cursor
Purpose: cursor for name based on NEAR_FID"""
#Function notes: its slow, should be a better method. Should only return 1 value
def slowFun(string, FC, Fld):
    whereClause = '"OBJECTID" = ' + string
    with arcpy.da.SearchCursor(FC, [Fld], whereClause) as cursorNested:
        for rowNested in cursorNested:
            return (rowNested[0])

"""Copy values field to field
Purpose: Copy values from one field to another in a table"""
def move_field_to_field(table, fromField, toField):
    with arcpy.da.UpdateCursor(table, [fromField, toField]) as cursor:
        for row in cursor:
            row[1] = row[0]
            cursor.updateRow(row)
            
"""Construct query for parent datasets
Purpose: Uses IDs in a child dataset to create selection qry from a parent dataset"""
def qry_from_parent(child_lyr, ID):
    whereClauseID = ''
    with arcpy.da.SearchCursor(child_lyr, [ID]) as cursor:
        for row in cursor:
            if row[0] >= 0:
                whereClauseID += "OBJECTID" + ' = ' + str(row[0]) + " OR "
    return (whereClauseID[:-4])
        
"""Unique Values
Purpose: returns a sorted list of unique values"""
#Function Notes: used to find unique field values in table column
def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor if row[0]})
    
"""Check if field exists in Feature
Purpose: Tests a Feature Class for a field (T/F)"""
#Function Notes: if the field appears more than once it will return False
def fieldExist(FC, field):
    fieldCnt = len(arcpy.ListFields(FC, field))
    if fieldCnt == 1:
        return True
    else:
        return False

"""List Duplicates
Purpose: make a list of values in a field of a table that appear more than once"""
#Function Notes: each value appears in the list for every instance after the first (e.g. 2x in list if 3x in the table)
def lst_dups(table, field):
    lst_unique = unique_values(table, field)
    lst_all = field_to_lst(table, field)
    for element in lst_unique:
        lst_all.remove(element)
    return lst_all

"""Check for Duplicates
Purpose: Find duplicate values within a field"""
#Function Notes: used to check field for duplicates
def check_dups(table, field):
    numFC = str(arcpy.GetCount_management(table))
    numNames = len(unique_values(table, field))
    if int(numFC) > numNames:
        dup_lst = lst_dups(table, field)
        if len(dup_lst) <10: #if there are less than 10 print their names
            arcpy.AddMessage("WARNING!!! The following are duplicate names in " + str(table)[:-4] + "." + str(field) + ": " + str(dup_lst))
            print("WARNING!!! The following are duplicate names in " + str(table)[:-4] + "." + str(field) + ": " + str(dup_lst))
        else:
            arcpy.AddMessage("WARNING!!! There are at least " + str(len(dup_lst)) + " duplicate names in " + str(table)[:-4] + "." + str(field))
            print("WARNING!!! There are at least " + str(len(dup_lst)) + " duplicate names in " + str(table)[:-4] + "." + str(field))

"""Field to List
Purpose: creates list from field in table"""
#Function Notes: only send stringm notmore complex list version of function
def field_to_lst(table, field):
    lst = [] #initiate list
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        for row in cursor:
            lst.append(row[0])
    return lst

"""Similarity Score
Purpose: """
#Function Notes: compares two strings based on sequence matcher 0 to 1, 1 being a perfect match
def simScore(a, b):
    return SequenceMatcher(None, a, b).ratio()

"""All Caps Field
Purpose: capitalizes all values in field"""
def All_Caps(table, field): #field as string
    #if field.Type == "String": #this only works on an object
    with arcpy.da.UpdateCursor(table, [str(field)]) as cursor: #str(field.name) if object
        for row in cursor:
            if row[0] != None: #Check for "<Null>"
                any(x.islower() for x in row[0]) == True
                row[0] = row[0].upper()
                cursor.updateRow(row)

############################
#########Front End##########
class Toolbox(object):
    def __init__(self):
        self.label = "Dataset Fancy Join"
        self.alias = "Fancy Join"
        # List of tool classes associated with this toolbox
        self.tools= [Step_1, Step_2, Step_3]

##########STEP 1###########
class Step_1 (object):
    def __init__(self):
        self.label = "Step 1: Prepare dataset by aggregating duplicates" 
        self.description = "This tool searches values in a dataset's target field to " +\
                           "find duplicates or near duplicates and assignes a score based on similarity."
    def getParameterInfo(self):
    #Define IN/OUT parameters
        joinFC_IN = arcpy.Parameter(
            displayName = "Join Feature Class",
            name = "join_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        Join_Field = arcpy.Parameter(
            displayName = "Join Field",
            name="joinFld",
            datatype="Field",
            parameterType="Required",
            direction = "Input")
        outputFC= arcpy.Parameter(
            displayName = "Output File for Unique",
            name="outFC",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction = "Output")
        outputFC_QC= arcpy.Parameter(
            displayName = "Output File for Duplicate (QC)",
            name="outFC_QC",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction = "Output")
        NameWeight = arcpy.Parameter(
            displayName = "Field Weight",
            name="nameWght",
            datatype="GPDouble",
            parameterType="Required", #
            direction = "Input")
        DistanceWeight = arcpy.Parameter(
            displayName = "Distance Weight",
            name="distWght",
            datatype="GPDouble",
            parameterType="Required",
            direction = "Input")
        tolerance = arcpy.Parameter(
            displayName = "Match Threshold",
            name="match",
            datatype="GPDouble",
            parameterType="Required", #
            direction = "Input")
        
	#Set the FieldsList to be filtered by the list from the feature dataset
        Join_Field.parameterDependencies = [joinFC_IN.name]
        #default values        
        NameWeight.value = "4.0"
        DistanceWeight.value = "1.0"

        params = [joinFC_IN, Join_Field, outputFC, outputFC_QC, NameWeight, DistanceWeight, tolerance]
        return params
    
    def isLicensed(self):
        return True
    def updateParameters(self, params):
        return
    def updateMessages(self, params):
        return
    def execute(self, params, messages):

        joinFC_IN = params[0].valueAsText
        joinFld = params[1].valueAsText
        outputFC = params[2].valueAsText
        outputFC_QC = params[3].valueAsText
        nameW = float(params[4].valueAsText)
        distW = float(params[5].valueAsText)
        tol = float(params[6].valueAsText)
        #derived
        joinName = os.path.basename(joinFC_IN)
        outPath = os.path.dirname(outputFC)
        joinFC = outPath + os.sep + joinName + "_int"

        #Make copy to maintain integrity
        arcpy.CopyFeatures_management(joinFC_IN, joinFC)

        #Normalize to All Caps
        All_Caps(joinFC, joinFld)
        arcpy.AddMessage("Capitalized text in Join Field")
        
        #check joinFC for duplicate names #REMOVE?
        check_dups(joinFC, joinFld)

        #Create Near Table
        arcpy.Near_analysis(joinFC, joinFC, "", "", "", "GEODESIC") #distance to nearest neighbor
        #FUNCTIONALITY TO DEAL WITH MORE THAN 2 nearest
        #arcpy.GenerateNearTable_analysis(joinFC, joinFC, TABLE, "", "", "", "ALL", maxMatches, "GEODESIC")
        #arcpy.AddJoin_Management() #join the new table back to the FC
        arcpy.AddMessage("Nearest Points Determined")

        #make sure needed IDs are available
        #If no IN_FID, make sure it is copied from OBJECTID
        if not(fieldExist(joinFC, "IN_FID")):
            arcpy.AddField_management(joinFC, "IN_FID", "LONG")
        move_field_to_field(joinFC, "OBJECTID", "IN_FID")
                    
        #If Orig_ID, make sure near ID is updated
        if(fieldExist(joinFC, "Orig_ID")):
            #add field to output
            arcpy.AddField_management(joinFC, "Near_O_ID", "DOUBLE") #doesn't have to be double
            #join field from joinFC_IN
            arcpy.JoinField_management(joinFC, "NEAR_FID", joinFC_IN, "OBJECTID", ["Orig_ID"])
            #copy over field
            #fieldName = str(os.path.basename(joinFC_IN))+".Orig_ID"
            move_field_to_field(joinFC, Orig_ID_1, Near_O_ID)
            #with arcpy.da.UpdateCursor(joinFC, ["Near_O_ID", "Orig_ID_1"]) as cursor:
                #for row in cursor:
                    #row[0] = row[1]
                    #cursor.updateRow(row)
                    
            arcpy.DeleteField_management(joinFC, "Orig_ID_1")
        arcpy.AddMessage('Checked for "IN_FID" and "Orig_ID", now "NEAR_O_ID"')

        #Distance Score
        distanceScore(joinFC)

        #Similarity Score
        arcpy.AddField_management(joinFC, "FldScore", "DOUBLE")
        arcpy.AddField_management(joinFC, "NearField", "TEXT") #name for near ID
        with arcpy.da.UpdateCursor(joinFC, ["FldScore", joinFld, "NEAR_FID", "NearField"]) as cursor:
            for row in cursor:
                if row[2] >= 0:
                    b = slowFun(str(row[2]), joinFC, joinFld)
                    row[0] = simScore(row[1], b) #add score
                    row[3] = b #add name
                else: #shouldn't happen
                    row[0] = 0
                cursor.updateRow(row)
        arcpy.AddMessage("Field Similarity Scores Calculated")

        #Summary Score
        SummaryScore(joinFC, distW, nameW)

        #Label Duplicate/Unique based on threshold
        arcpy.AddField_management(joinFC, "DUP_QC", "TEXT")
        with arcpy.da.UpdateCursor(joinFC, ["TotScore", "DUP_QC"]) as cursor:
            for row in cursor:
                if row[0] >= tol:
                    row[1] = "DUPLICATE"
                else:
                    row[1] = "UNIQUE"
                        #Calculate QC field
                cursor.updateRow(row)
        arcpy.AddMessage("Determined 'DUPLICATE' or 'UNIQUE' based on threshold")

        #Create output tables from selections
        arcpy.MakeFeatureLayer_management(joinFC, "lyr")
        #first remove double entries
        exp = ''
        pairs_lst =[]
        with arcpy.da.SearchCursor(joinFC, ["IN_FID", "NEAR_FID"]) as cursor:
            for row in cursor:
                pairs_lst.append([row[0],row[1]])
                if [row[1], row[0]] not in pairs_lst: #if it isn't a duplicate of a pair already in the list
                    exp += '"IN_FID" = '+ str(row[0]) + ' AND ' + '"NEAR_FID" = ' + str(row[1]) + ' OR '
        exp = exp[:-4] #removes last ' OR '
        #arcpy.AddMessage("exp: " + exp)
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp)
        arcpy.AddMessage("Removed redundant pairs in "+ str(os.path.basename(outputFC_QC)))

        #output table of unique
        exp1 = '"DUP_QC" = ' + "'UNIQUE'"
        arcpy.SelectLayerByAttribute_management("lyr", "SUBSET_SELECTION", exp1)
        arcpy.CopyFeatures_management("lyr", outputFC)
        arcpy.AddMessage("Created Feature Class for UNIQUE: " + str(os.path.basename(outputFC)))
        
        #output table of non-unique
        #arcpy.MakeFeatureLayer_management(joinFC, "lyr") #make new
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp)

        #move redundant pairs back down here if needed/wanted in Unique set
        #move will require reverting some of the selection types around

        exp2 = '"DUP_QC" = ' + "'DUPLICATE'"
        arcpy.SelectLayerByAttribute_management("lyr", "SUBSET_SELECTION", exp2)
        arcpy.CopyFeatures_management("lyr", outputFC_QC)
        arcpy.AddMessage("Created Feature Class for DUPLICATE: " + str(os.path.basename(outputFC_QC)))
        
        #Cleanup
        arcpy.Delete_management(joinFC)
                
##########STEP 2###########        
class Step_2 (object):
    def __init__(self):
        self.label = "Step 2: Join, Append or set aside for manual QC" 
        self.description = "This tool compares values in a target dataset's field with those" +\
                           " in a join dataset's field, assigns a score based on that compar" +\
                           "ison and the distance between the points, and then either joins " +\
                           "the attributes to the target dataset or appends a new point for " +\
                           "it. A new dataset it also generated for manually checking if the points match."

    def getParameterInfo(self):
    #Define IN/OUT parameters
        targetFC_IN = arcpy.Parameter(
            displayName = "Target Feature Class",
            name = "target_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        Target_Field = arcpy.Parameter(
            displayName = "Target Field",
            name="targetFld",
            datatype="Field",
            parameterType="Required",
            direction = "Input")
        joinFC_IN = arcpy.Parameter(
            displayName = "Join Feature Class",
            name = "join_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        Join_Field = arcpy.Parameter(
            displayName = "Join Field",
            name="joinFld",
            datatype="Field",
            parameterType="Required",
            direction = "Input")
        Radius = arcpy.Parameter( #max distance
            displayName = "Max Distance",
            name="radiusUnits",
            datatype="GPLinearUnit",
            parameterType="Required",
            direction = "Input")
        outputFC= arcpy.Parameter(
            displayName = "Output File",
            name="outFC",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction = "Output")
        QC_YES = arcpy.Parameter(
            displayName = "Match Threshold",
            name="match",
            datatype="GPDouble",
            parameterType="Optional", #
            direction = "Input")
        QC_NO = arcpy.Parameter(
            displayName = "Reject Threshold",
            name="reject",
            datatype="GPDouble",
            parameterType="Optional", #
            direction = "Input")
        NameWeight = arcpy.Parameter(
            displayName = "Field Weight",
            name="nameWght",
            datatype="GPDouble",
            parameterType="Optional", #
            direction = "Input")
        DistanceWeight = arcpy.Parameter(
            displayName = "Distance Weight",
            name="distWght",
            datatype="GPDouble",
            parameterType="Optional",
            direction = "Input")
        outUnique = arcpy.Parameter(
            displayName = "Unique Results",
            name = "out_Unique",
            datatype="DEFeatureDataset",
            parameterType = "Derived",
            direction = "Output")

	#Set the FieldsList to be filtered by the list from the feature dataset
        Target_Field.parameterDependencies = [targetFC_IN.name]
        Join_Field.parameterDependencies = [joinFC_IN.name]
        Radius.parameterDependencies = [targetFC_IN.name] #units default to match the spatial ref of target

        #default values
        QC_YES.value = 0.7
        QC_NO.value = 0.2
        NameWeight.value = 2
        DistanceWeight.value = 1

        #derived outputs
        #outUnique = outputFC + "_Unique"

        params = [targetFC_IN, Target_Field, joinFC_IN, Join_Field, Radius, outputFC, QC_YES, QC_NO, NameWeight, DistanceWeight, outUnique]

        return params
    def isLicensed(self):
        return True
    def updateParameters(self, params):
        return
    def updateMessages(self, params):
        return
    def execute(self, params, messages):        
############################
#######Test Variables#######
#targetFC_IN = 'Health_public_target'
#joinFC_IN = 'Boat_ramps'
#outputFC = r'L:\Public\Lyon\GIS\Test_JJB.gdb\Health_public_result'
#targetFld = "Name"
#joinFld = "FACNAME"
#radius = "1000 Meters"
#QCThresholdYes = 0.7
#QCThresholdNo = 0.2
#nameW = 2
#distW = 1
###########PARAMS###########
        targetFC_IN = params[0].valueAsText
        targetFld= params[1].valueAsText
        joinFC_IN = params[2].valueAsText
        joinFld = params[3].valueAsText
        outputFC = params[5].valueAsText
        radius = params[4].valueAsText
        QCThresholdYes = float(params[6].valueAsText)
        QCThresholdNo = float(params[7].valueAsText)
        nameW = float(params[8].valueAsText)
        distW = float(params[9].valueAsText)
        #derived
        #arcpy.AddMessage("derived Param: " + params[10].valueAsText) #trying this instead of arcpy.mapping
        #outUnique = arcpy.setParameterAsText(params[10], outputFC + "Unique")
        
        targetName = os.path.basename(targetFC_IN)
        joinName = os.path.basename(joinFC_IN)
        outPath = os.path.dirname(outputFC) + os.sep
        targetFC = outPath + targetName + "_int"
        joinFC = outPath + joinName + "_int"

        #unique out FC
        outUnique = outputFC + "Unique"
        #duplicate out FC
        outDup = outputFC + "Duplicate"
        #manual out FC
        outMan = outputFC + "Manual"
        
############################
##########Execute###########
        #create copy datasets
        arcpy.CopyFeatures_management(targetFC_IN, targetFC)
        arcpy.CopyFeatures_management(joinFC_IN, joinFC)

        #Normalize to All Caps
        All_Caps(targetFC, targetFld)
        All_Caps(joinFC, joinFld)

        #check targetFC for duplicate names
        check_dups(targetFC, targetFld)

        #check joinFC for duplicate names
        check_dups(joinFC, joinFld)

        #Near distances
        #arcpy.Near_analysis(joinFC, targetFC, radius, "NO_LOCATION", "NO_ANGLE", "GEODESIC")
        arcpy.Near_analysis(targetFC, joinFC, radius, "NO_LOCATION", "NO_ANGLE", "GEODESIC")

        #join joinFC
        arcpy.JoinField_management(targetFC, "NEAR_FID", joinFC, "OBJECTID", [joinFld])

        #check for IN_FID in targetFC
        #If no IN_FID, make sure it is copied from OBJECTID
        if not(fieldExist(targetFC, "IN_FID")):
            arcpy.AddField_management(targetFC, "IN_FID", "LONG")
        move_field_to_field(targetFC, "OBJECTID", "IN_FID")
        
        #Distance Score
        distanceScore(targetFC)
        
        #Similarity Score
        arcpy.AddField_management(targetFC, "FldScore", "DOUBLE") #Doesn't get "NearField" because we'll do a join instead
        NEAR_ID_lst = [] #create list of NEAR_ID distance for later use
        with arcpy.da.UpdateCursor(targetFC, ["FldScore", targetFld, "NEAR_FID"]) as cursor:
            for row in cursor:
                NEAR_ID_lst.append(row[2])
                if row[2] >= 0:
                    b = slowFun(str(row[2]), joinFC, joinFld)
                    row[0] = simScore(row[1], b)
                else: #shouldn't happen
                    row[0] = 0
                cursor.updateRow(row)

        #Summary Score
        SummaryScore(targetFC, distW, nameW)

        #add field for QC
        arcpy.AddField_management(targetFC, "DUP_QC", "TEXT")
        #Calculate QC field
        with arcpy.da.UpdateCursor(targetFC, ["TotScore", "DUP_QC"]) as cursor:
            for row in cursor:
                if row[0] >= QCThresholdYes:
                    row[1] = "DUPLICATE"
                elif row[0] <= QCThresholdNo:
                    row[1] = "UNIQUE"
                else:
                    row[1] = "MANUAL"
                cursor.updateRow(row)
        
###ADD HANDLE FOR NO THRESHOLD?

#####append any points in the joinFC that were out of range#####

        #First create a selection exp
        ob_ID_lst = field_to_lst(joinFC, "OBJECTID") #make a list of the IDs from original
        #compare to IDs joined by distance threshold
        far_out_lst = (set(ob_ID_lst) - set(NEAR_ID_lst))
        
        #selection exp
        exp = ''
        for pnt_ID in far_out_lst:
            exp += '"OBJECTID" = ' + str(pnt_ID) + " OR "
        exp = exp[:-4]

        arcpy.AddField_management(joinFC, "NEAR_FID", "LONG")
        move_field_to_field(joinFC, "OBJECTID", "NEAR_FID")                                 
    
        #use the expression from above to make a selection
        arcpy.MakeFeatureLayer_management(joinFC, "lyr")
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp)

        #Add function to make a list of fields in target to remove from join?
        #append any that were skipped to new FC
        arcpy.Append_management(["lyr"], targetFC, "NO_TEST", "", "")

        arcpy.DeleteField_management(joinFC, "NEAR_FID") #don't need if joinField isn't run after this

        #export to outputFC
        arcpy.MakeFeatureLayer_management(targetFC, "lyr")
        arcpy.CopyFeatures_management("lyr", outputFC) 
        
        #update their QC code
        with arcpy.da.UpdateCursor(outputFC, ["DUP_QC"]) as cursor:
            for row in cursor:
                if row[0] == None:
                    row[0] = "UNIQUE" #should be unique
                cursor.updateRow(row)

        #set mxd to add new layers to
        mxd = arcpy.mapping.MapDocument("CURRENT")
        #set dataframe
        df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
        
        #create output datasets
        arcpy.MakeFeatureLayer_management(outputFC, "lyr")
        #create dataset for duplicates
        exp1 = '"DUP_QC" = ' + "'DUPLICATE'"
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp1) #select
        arcpy.CopyFeatures_management("lyr", outDup) #copy to outDup
        #add to map
        layer = arcpy.mapping.Layer(outDup)
        arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
        arcpy.AddMessage("Created Feature Class for DUPLICATE: " + str(os.path.basename(outDup)))
        #create dataset for manual QC
        exp2 = '"DUP_QC" = ' + "'MANUAL'"
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp2) #select
        arcpy.CopyFeatures_management("lyr", outMan) #copy to outMan
        #add to map
        layer = arcpy.mapping.Layer(outMan)
        arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
        arcpy.AddMessage("Created Feature Class for Manual Check: " + str(os.path.basename(outMan)))
        #create dataset for unique
        exp3 = '"DUP_QC" = ' + "'UNIQUE'"
        arcpy.SelectLayerByAttribute_management("lyr", "NEW_SELECTION", exp3) #select
        arcpy.CopyFeatures_management("lyr", outUnique) #copy to outUnique
        #add to map
        layer = arcpy.mapping.Layer(outUnique)
        arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
        arcpy.AddMessage("Created Feature Class for UNIQUE: " + str(os.path.basename(outUnique)))

############################
#########CLEAN UP###########
        arcpy.Delete_management(targetFC)
        arcpy.Delete_management(joinFC)
        #arcpy.Delete_management(outputFC)

        #refresh
        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()
        
        arcpy.AddMessage("Process Complete")

##########STEP 3###########        
class Step_3 (object):
    def __init__(self):
        self.label = "Step 3: Use QC code to finalize dataset" 
        self.description = "This tool determines if a new point is created from two that are" +\
                           " the same or if the two points are unique, based on assigned values"

    def getParameterInfo(self):
        #parent dataset(s)
        targetFC_IN = arcpy.Parameter(
            displayName = "Original Target Feature Class",
            name = "target_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        joinFC_IN = arcpy.Parameter(
            displayName = "Original Join Feature Class",
            name = "join_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        #QC'd datasets
        ManualQC = arcpy.Parameter(
            displayName = "Points Manually Checked",
            name = "QC_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        autoSame = arcpy.Parameter(
            displayName = "Points Matching",
            name = "same_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Optional",
            direction = "Input")
        autoUnique = arcpy.Parameter(
            displayName = "Points Unique",
            name = "unique_pnts",
            datatype = "GpFeatureLayer",
            parameterType = "Required",
            direction = "Input")
        #field with QC codes
        QC_field = arcpy.Parameter(
            displayName = "QC Field",
            name="QCFld",
            datatype="Field",
            parameterType="Required",
            direction = "Input")
        QC_Same = arcpy.Parameter( #rows marked same
            displayName = "Value for Same",
            name="match",
            datatype="GPString",
            parameterType="Required",
            direction = "Input")
        QC_unique = arcpy.Parameter( #rows marked unique
            displayName = "Value for Unique",
            name="unique",
            datatype="GPString",
            parameterType="Required",
            direction = "Input")
        method = arcpy.Parameter( #method (centroid or target)
            displayName = "Duplicate Point Placement Method",
            name="method",
            datatype="GPString",
            parameterType="Required",
            direction = "Input")
        outputFC= arcpy.Parameter(
            displayName = "Output File",
            name="outFC",
            datatype="DEFeatureDataset",
            parameterType="Required",
            direction = "Output")

        #Set the FieldsList to be filtered by the list from the feature datasets
        QC_field.parameterDependencies = [autoUnique.name] + [ManualQC.name] + [autoSame.name] 
        #QC_field.parameterDependencies = set([ManualQC.name]) & set([autoSame.name]) & set([autoUnique.name]) #v2.2
        method.filter.type = "ValueList"
        method.filter.list = ["TARGET", "CENTER"]
        
        #default values
        QC_field.value = "DUP_QC"
        QC_Same.value = "DUPLICATE"
        QC_unique.value = "UNIQUE"
        #method.value = "TARGET"

        params = [targetFC_IN, joinFC_IN, ManualQC, autoSame, autoUnique, QC_field, QC_Same, QC_unique, method, outputFC]

        return params
    def isLicensed(self):
        return True
    def updateParameters(self, params): #does this need to be used?
        return
    def updateMessages(self, params):
        return
    def execute(self, params, messages):
        targetFC_IN = params[0].valueAsText
        joinFC_IN = params[1].valueAsText
        manualQC = params[2].valueAsText
        autoSame = params[3].valueAsText
        autoUnique = params[4].valueAsText
        QC_field = params[5].valueAsText
        field_same = params[6].valueAsText
        field_unique = params[7].valueAsText
        method = params[8].valueAsText
        outputFC = params[9].valueAsText

###FOR TESTING###
#targetFC_IN = r'L:\Public\Lyon\GIS\RawData.gdb\HealthDept_points'
#autoUnique = r'L:\Public\Lyon\GIS\Test_JJB.gdb\HealthDept_Unique8'
#autoSame = r'L:\Public\Lyon\GIS\Test_JJB.gdb\HealthDept_Duplicate8'
#outputFC = r'L:\Public\Lyon\GIS\Test_JJB.gdb\Heath_Step1_Step3'

#targetFC_IN =r'L:\Public\Lyon\GIS\Test_JJB.gdb\test9pnts'
#autoUnique = r'L:\Public\Lyon\GIS\Test_JJB.gdb\test9pnts_Unq'
#autoSame = r'L:\Public\Lyon\GIS\Test_JJB.gdb\test9pnts_Dup'
#outputFC = r'L:\Public\Lyon\GIS\Test_JJB.gdb\test3pnts_Step3_cnt_4'

#joinFC_IN = None
#manualQC = None
#QC_field = "DUP_QC"
#field_unique = "UNIQUE"
#field_same = "DUPLICATE"
#################

        path = os.path.dirname(outputFC) + os.sep
        targetFC = path + os.path.basename(targetFC_IN) + "_int"

        ID1 = "IN_FID" #in Target
        ID2 = "NEAR_FID" #in Join
            
        #make list for optional layers
        lyr_lst = []
        if autoUnique!= None: #input is not optional
            arcpy.MakeFeatureLayer_management(autoUnique, "unique_lyr")
            lyr_lst.append("unique_lyr")
        if manualQC!= None: #input is optional
            arcpy.MakeFeatureLayer_management(manualQC, "man_lyr")
            lyr_lst.append("man_lyr")
        if autoSame!= None: #input is optional
            arcpy.MakeFeatureLayer_management(autoSame, "same_lyr")
            lyr_lst.append("same_lyr")

        #Make copy to maintain integrity
        arcpy.CopyFeatures_management(targetFC_IN, targetFC)

        #check IN_FID and make layers for target dataset
        if (fieldExist(targetFC, ID1)):
            arcpy.DeleteField_management(targetFC, [ID1])
            arcpy.AddMessage(str(ID1) + " replaced in Original Target Features")
        arcpy.AddField_management(targetFC, ID1)
        move_field_to_field(targetFC, "OBJECTID", ID1)
        arcpy.MakeFeatureLayer_management(targetFC, "target_lyr")

        if joinFC_IN == None: #optional input, if null near was performed on one dataset 
            arcpy.MakeFeatureLayer_management(targetFC, "join_lyr") #use ID1
        else:
            #make copy to maintain integrity
            joinFC = path + os.path.basename(joinFC_IN) + "_int"
            arcpy.CopyFeatures_management(joinFC_IN, joinFC)
            if (fieldExist(joinFC, ID2)): #check for Near_ID
                arcpy.DeleteField_management(joinFC, [ID2])
                arcpy.AddMessage(str(ID2) + " replaced in Original Join Features")
            arcpy.AddField_management(joinFC, ID2) #use ID2
            move_field_to_field(joinFC, "OBJECTID", ID2)
            arcpy.MakeFeatureLayer_management(joinFC, "join_lyr")

        #test for ID1 and ID2 in all layers (shouldn't fail)
        for lyr in lyr_lst:
            if not(fieldExist(lyr, ID1)):
                arcpy.AddMessage("CAUTION: " + ID1 + " missing from " + lyr)
            if not(fieldExist(lyr, ID2)):
                arcpy.AddMessage("CAUTION: " + ID2 + " missing from " + lyr)

        #Create query strings
        whereUnique = QC_field + ' = ' + "'" + field_unique + "'"
        whereSame = QC_field + ' = ' + "'" + field_same + "'"
                                 
        #create empty feature class with full schema
        arcpy.CreateFeatureclass_management(path, os.path.basename(outputFC), "POINT", "unique_lyr", "", "", "", "", "", "", "")
                                 
        for lyr in lyr_lst:
            #from lyr where unique
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereUnique)

            whereTargetID = qry_from_parent(lyr, ID1)
            whereJoinID = qry_from_parent(lyr, ID2)
            
            clauseLst = []
            #test whereClause isn't empty or else all are selected
            if whereTargetID !='':
                arcpy.SelectLayerByAttribute_management("target_lyr", "NEW_SELECTION", whereTargetID)
                clauseLst.append("target_lyr")
            if whereJoinID !='':
                arcpy.SelectLayerByAttribute_management("join_lyr", "NEW_SELECTION", whereJoinID)
                clauseLst.append("join_lyr")
            #test the list isn't empty or append would fail
            if len(clauseLst)>0:
                arcpy.Append_management(clauseLst, outputFC, "NO_TEST", "", "") #use subtype to assign metadata on source

        ###DELETE DUPLCIATES FROM APPENDED####
        if joinFC_IN == None:
        #this occurs when A is nearest B, C is nearest B and all are unique
        #if there are two datasets, this will be delt with after duplicates are appended
            field_names = [f.name for f in arcpy.ListFields(outputFC)]
            field_names.remove("OBJECTID")
            arcpy.DeleteIdentical_management(outputFC, field_names) #find a way to do this with lower LICENSE
        ######################################
    
        #Update QC_field (since this was cleared) ???this field may not be needed???
        with arcpy.da.UpdateCursor(outputFC, [QC_field]) as cursor:
            for row in cursor:
                row[0] = field_unique
                cursor.updateRow(row)
                
        #from all tables where duplicate
        for lyr in lyr_lst:
            arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", whereSame)

            #append from created dataset
            arcpy.Append_management([lyr], outputFC, "NO_TEST", "", "") #use subtype to assign metadata on source

    ######DELETE DUPLCIATES FROM APPENDED#######
        if joinFC_IN == None:
        #have to check NEAR_FID against IN_FID
            if method == "TARGET":
                arcpy.AddMessage("CAUTION: Since the Target dataset contains both IN_FID and NEAR_FID, the location " +
                                 "of duplicates is set to the smaller IN_FID if both are nearest eachother.")
        #if A is nearest B (pair) and C is nearest B (pair or unique, see nested if statement)

            ID_lst=[]
            
            with arcpy.da.SearchCursor(outputFC, [ID1, ID2, "OBJECTID"]) as cursor:
                for row in cursor:
                    ID_lst.append([row[0], row[1], row[2]])
            ID1_lst, ID2_lst, OID_lst = map(list, zip(*ID_lst)) #unpack nested list to 3 lists
            ID2_lst_NoNull = [element for element in ID2_lst if element != None]

            deleteExp=''
            for item in ID2_lst_NoNull:
                #first check for duplicate IN_FID
                NEAR_FID_index = ID2_lst.index(item) #ID2, IN_FID = ID1_lst[NEAR_FID_index]
                if ID1_lst.count(ID1_lst[NEAR_FID_index])>1: #if the IN_FID from a pair appears more than 1x
                        #index for all occurances of the IN_FID from the pair
                        indices = [i for i, ID_1 in enumerate(ID1_lst) if ID_1 == ID1_lst[NEAR_FID_index]]
                        for index in indices:
                            if ID2_lst[index] == None: #if it apears as unique
                                OID = OID_lst[index]
                                deleteExp += "OBJECTID" + " = " + str(OID) + " OR "
                                arcpy.AddMessage(str(ID1) + ": " + str(ID1_lst[index]) + " was identified as both unique (Results OBJECTID: " +
                                                 str(OID) + ") and as a duplicate of " + str(ID2) +
                                                 str(item) + ". The unique point will be deleted.")

                #second check for duplicate NEAR_FID
                if item in ID1_lst:
                    IN_FID_index = ID1_lst.index(item) #ID1 
                    #NEAR_FID_index = ID2_lst.index(item) #ID2
                    if ID2_lst[IN_FID_index] != None: #if C-B is pair
                        arcpy.AddMessage(str(ID2) + ": " + str(item) + " was identified as a duplicate of both " + str(ID1) +
                                         ": " + str(ID1_lst[NEAR_FID_index]) + "(Results OBJECTID: " + str(OID_lst[NEAR_FID_index]) +
                                         ") and " + str(ID2) + ": " + str(ID2_lst[IN_FID_index]) +
                                         " (Results OBJECTID: " + str(OID_lst[IN_FID_index]) + ").")
                        #print(str(ID1) + ": " + str(item) + " was identified as a duplicate of both " + str(ID1) + ": " +
                        #str(ID1_lst[NEAR_FID_index]) + "(OBJECTID: " + str(OID_lst[NEAR_FID_index]) + ") and " + str(ID2) +
                        #": " + str(ID2_lst[IN_FID_index]) + " (OBJECTID: " + str(OID_lst[IN_FID_index]) + ").")
                        arcpy.AddMessage("These points were left separate but should be inspected and combined in the future.")
                    #if C-B is unique
                    else: #if C-B is unique
                        arcpy.AddMessage(str(ID2) + ": " + str(item) + " was identified as unique (Results OBJECTID = " +
                                         str(OID_lst[IN_FID_index]) + ") and as part of a duplicate pair with " + str(ID1) +
                                         ": " + str(ID1_lst[NEAR_FID_index]) + " (Results OBJECTID = " + str(OID_lst[NEAR_FID_index]) + ").")
                        #print(str(ID1) + ": " + str(item) + " was identified as unique (OBJECTID = " + str(OID_lst[IN_FID_index]) +
                        #") and as part of a duplicate pair with " + str(ID2) + ": " + str(ID1_lst[NEAR_FID_index]) + " (OBJECTID = " +
                        #str(OID_lst[NEAR_FID_index]) + ").")
                        arcpy.AddMessage("The unique point will be deleted.")
                        deleteExp += str(ID1) + " = " + str(item) + " OR " #better to do by OBJECTID?                        
                            
            if deleteExp != '':
                deleteExp=deleteExp[:-4]
                arcpy.MakeFeatureLayer_management(outputFC, "out_lyr")
                arcpy.SelectLayerByAttribute_management("out_lyr", "NEW_SELECTION", deleteExp)
                arcpy.DeleteFeatures_management("out_lyr")
                arcpy.AddMessage("The unique entries were deleted.") #add list of them even though they are identified above?
    ############################################
                
        if method == "CENTER":
            #create point between points
            arcpy.MakeFeatureLayer_management(outputFC, "final_lyr")
            arcpy.SelectLayerByAttribute_management("final_lyr", "NEW_SELECTION", whereSame)
            #alter geometry
            with arcpy.da.UpdateCursor("final_lyr", ["SHAPE@XY", ID2, "OBJECTID"]) as cursor: #SHAPE@XY = tuple
                for row in cursor:
                    if row[1] == None:
                        arcpy.AddMessage("OBJECTID " + str(row[2]) + " is missing a NEAR_ID, location of point could not be re-assigned.")
                    else:
                        x1, y1 = row[0][0], row[0][1] #X coordinate, Y coordinate
                        whereJoinID = "OBJECTID" + " = " + str(row[1])
                        arcpy.SelectLayerByAttribute_management("join_lyr", "NEW_SELECTION", whereJoinID)
                        with arcpy.da.SearchCursor("join_lyr", ["SHAPE@XY"])as cursor2:
                            for row2 in cursor2:
                                x2, y2 = row2[0][0], row2[0][1]
                        newXY = (((x1-x2)/2.0)+ x2), (((y1-y2)/2.0)+ y2) #as tuple
                        row[0] = newXY
                        cursor.updateRow(row)

