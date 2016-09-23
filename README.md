# Py_FancyJoin
This tool is used to find similar points based on distance between the points and how similar a string field is. 

##Process
The tool is set up to automatically mark and separte outputs based on if it thinks they are a match or not. This allows the user to then
review clear matches, those that are questionable or those that are clear non-matches.
The user can update the auto generated duplciates field to reflect if the points are an actual match or not or create a new field.
These fields are specified and used in the "Compile" step to create a new dataset where similar points are combined. The location for the
combined point can be either based on one of the datasets or a mid-point between the two.

##Input Datasets
Points can either be compared within a dataset (Step1) or between two datasets (Step2).

##Input Parameters
The user is able to set weights for distance vs field similarity.
The user is able to specify a score (0 to 1) to mark points as matching.
The user is able to specify which field(s) in the dataset(s) should be compared.

##Download Options
The tool is available as three (3) standalone pytohn scripts which require the arcpy library, or a single .pyt python toolbox which can
be run from arcGIS desktop.
