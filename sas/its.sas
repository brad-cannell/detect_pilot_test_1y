{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf200
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 libname detect "H:\\DETECT\\pilot data";\
/* FROM IMPORT of CSV FILE\
data detect.aps_pilot_data;\
set aps_its;\
run;\
*/\
/*aggregate by week*/\
proc sql;\
create table aps_pilot_data as\
select count(study_week) as report_count,\
ems as ems,\
study_week as study_week\
from detect.aps_pilot_data\
group by study_week, ems ;\
run;\
quit;\
data aps_ems;\
set aps_pilot_data;\
if ems=1;\
ems_count=report_count;\
drop report_count;\
run;\
data aps_other;\
set aps_pilot_data;\
if ems=0;\
other_count=report_count;\
drop report_count;\
run;\
proc sort data=aps_ems;\
by study_week;\
run;\
proc sort data=aps_other;\
by study_week;\
run;\
/*prep intervention dummies*/\
data analyze_its;\
merge aps_ems aps_other;\
by study_week;\
if ems_count=. then ems_count=0;\
if study_week >= 38 and study_week <= 43 then detect = 1;\
else if study_week >= 109 then detect = 1;\
else detect = 0;\
if study_week >= 38 and study_week <= 43 then detect_pilot = 1;\
else detect_pilot=0;\
if study_week >= 109 then detect_r2 = 1;\
else detect_r2=0;\
run;\
/*find the appropriate ARIMA noise structures to achieve white noise in the baseline period. Needed to control for the short \
pilot period. Also conditioned on the control group to help clean up the noise model\
Based on the ACF and PACF, tried q=2 (thats a MA(2) noise model). All my diagnostics are now pretty, \
moving on to intervention analysis with MA(2) noise model*/\
proc arima data=analyze_its;\
where study_week<109;\
identify var=ems_count crosscorr=(other_count detect) STATIONARITY=(adf=(1,4));\
estimate q=(2) input=( other_count detect) method=ml ;\
run;\
/*treat as level change, combine effect across phases (one dummy for both the short pilot and the long intervention period)*/\
proc arima data=analyze_its;\
identify var=ems_count crosscorr=(other_count detect) ;\
estimate q=(2) input=( other_count detect) method=ml \
outmodel=with_control;\
run;\
quit;\
/*treat as level change, combine across phases, no control group. \
This mostly is just making sure there is not some craziness in the control driving the effects*/\
proc arima data=analyze_its;\
identify var=ems_count crosscorr=( detect) ;\
estimate q=(2) input=(  detect) method=ml \
outmodel=without_control;\
run;\
quit;\
/*treat as level change, seperate variables per phase*/\
/*this is 5% for my own intellectual curiosity, mostly this is so I can test for different intervention shapes in the long period */\
/*might be worth circling back to if Brad wants to do some fancy graphs*/\
proc arima data=analyze_its;\
identify var=ems_count crosscorr=(other_count detect_pilot detect_r2) ;\
estimate q=(2) input=( other_count detect_pilot detect_r2 ) method=ml ;\
run;\
quit;\
/*treat r2 as gradually increasing to some limit, seperate variables per phase*/\
/*running it as an intervention that ramps up didnt fit as well, the basic mean change is what to stick with (first analyses)*/\
proc arima data=analyze_its;\
identify var=ems_count crosscorr=(other_count detect_pilot detect_r2) ;\
estimate q=(2) input=( other_count detect_pilot / (1) detect_r2 ) method=ml ;\
run;\
quit;\
/*The SAS gods did not see fit to calcualte CIs for ARIMA parameter estimates... so this is me doing it by hand*/\
data ci1;\
set with_control;\
if _NAME_="detect";\
lcl=_VALUE_-1.96*_STD_;\
ucl=_VALUE_+1.96*_STD_;\
run;\
data ci2;\
set without_control;\
if _NAME_="detect";\
lcl=_VALUE_-1.96*_STD_;\
ucl=_VALUE_+1.96*_STD_;\
run;\
/*Sensitivity analyses*/\
/*the mean count is a little low to assume normally distriubted outcomes. I'm not worried about it, but a reviewer might be*/\
/*so heres the equivalent models as a Poisson with robust standard errors. Results are virtually the same */\
proc genmod data=analyze_its;\
class study_week;\
model ems_count=detect other_count/link=log dist=p;\
repeated subject=study_week;\
estimate "detect" detect 1/exp;\
run;\
proc genmod data=analyze_its;\
class study_week;\
model ems_count=detect /link=log dist=p;\
repeated subject=study_week;\
estimate "detect" detect 1/exp;\
run;}