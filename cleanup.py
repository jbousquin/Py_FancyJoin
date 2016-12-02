# -*- coding: utf-8 -*-
"""
Cleanup of columns and IDS for Sarina
"""

import sys, os
workspace=r"C:\Users\nmerri02\Desktop\Cleanup crew"
sys.path.append(workspace)

import arcpy
from arcpy import env
import numpy as np

arcpy.env.overwriteOutput = True

arcpy.env.workspace = r"L:\Public\Lyon\GIS\AccessJoin.gdb"
messy="Aggregated_2_final"

clean="Aggregated_2_final_clean"
arcpy.CopyFeatures_management(messy, clean)

#Check column names
HDfields=arcpy.ListFields(messy,"HD_*")
EPAfields=arcpy.ListFields(messy,"EPA_*")
MORISfields=arcpy.ListFields(messy,"MORIS_*")
BRfields=arcpy.ListFields(messy,"BR_*")
Barnstablefields=arcpy.ListFields(messy,"Barnstabl*")
Yarlinefields=arcpy.ListFields(messy,"Yar_lin*")
Yarpolyfields=arcpy.ListFields(messy,"Yar_pol*")
Mashpeefields=arcpy.ListFields(messy,"Mashpe*")
Sanbeachfields=arcpy.ListFields(messy,"San_beac*")
SanBRfields=arcpy.ListFields(messy,"San_BO*")
Falmouthfields=arcpy.ListFields(messy,"Falmout*")
ftfields=arcpy.ListFields(messy,"FT_*")
Codefields=arcpy.ListFields(messy,"Code_*")   

combines=[HDfields,EPAfields,MORISfields,BRfields,Barnstablefields,Yarlinefields,Yarpolyfields,Mashpeefields,Sanbeachfields,SanBRfields,Falmouthfields,ftfields,Codefields]
names=["HD_","EPA_","MORIS_","BR_","Barnstable","Yar_line","Yar_poly","Mashpee","San_beach","San_BOR","Falmouth","FT_","Code_"]

n=0
for x in combines:

    HD_names = []
    for field in x:
        HD_names.append(field.name)
        
    HDs = arcpy.da.TableToNumPyArray(messy,HD_names,null_value=-9999)
    
    HDs = np.array(HDs.tolist())
    
    HD2=np.zeros((np.ma.size(HDs,0),np.ma.size(HDs,1)),dtype=np.dtype('U8'))
    
    for i in range(0,np.ma.size(HDs,0)): 
        a =  np.unique(HDs[i])
        if n<12: #changes this to max of combines size
            a=a[a>0]
        else:
            a=a[1:] #drop only -9999's
            
        
        HD2[i,0:np.ma.size(a,0)]=a
    
    HDc= HD2[:, np.apply_along_axis(np.count_nonzero,0,HD2) > 0]
    HDc[HDc=='']=0
    
    arcpy.DeleteField_management (clean, HD_names)
    
    HD_newnames=list()
    
    for i in range(0,np.ma.size(HDc,1)):
        HD_newnames.append(names[n]+str(i+1))
        if n<12: #changes this to max of combines size
            arcpy.AddField_management(clean, HD_newnames[i] , "DOUBLE")
        else:
            arcpy.AddField_management(clean, HD_newnames[i] , "TEXT")
          
    i=0
    for x in HD_newnames:
        ii=0
        with arcpy.da.UpdateCursor(clean,x) as cursor:
            for row in cursor:
                row[0]=HDc[ii,i]
                ii=ii+1
                cursor.updateRow(row)
        i=i+1
    
    del HD_names
    print names[n]
    n=n+1
    
