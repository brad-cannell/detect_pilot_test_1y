# =============================================================================
# Creating incident complaint table
# Created: 2019-01-28
# Updated: 2019-01-31
# =============================================================================

# Here is where I created a path to the data..
path <- file.path("Documents", "Research Projects", "DETECT Research", "DETECT Data", "symptoms.feather")

library("feather", lib.loc="/Library/Frameworks/R.framework/Versions/3.5/Resources/library")

feather(path) # loading feather package

Incident <- read_feather(path)

View(Incident)

table(incident_complaint)