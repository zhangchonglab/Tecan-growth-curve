# this script is used for processing the data extracted from Tecan cell growth curve profiling.
# 3 input files needed
# 1st: the raw data of growth curve with only necessary lines
# 2nd: the configuration file definin the relationship of replicates
# 3rd: Prefix used to rename the output file
# strain\tA1,A2,A3

import os
import sys
raw_data=sys.argv[1]
configureFile=sys.argv[2]
prefix=sys.argv[3]
import numpy as np

row=['A','B','C','D','E','F','G','H']
column=['1','2','3','4','5','6','7','8','9','10','11','12']
AllWell=[]

for item in row:
    for element in column:
        AllWell.append(item+element)

# construct the dic that link the strain name to its relevant replicates
BioReplicate={}
TimeCourse={}
f=open(configureFile,'r')
wellRecord=[]
Well_strain_dic={}
strainRecord=[]
for line in f:
    strain=line.rstrip().split('\t')[0]
    Replicates=line.rstrip().split('\t')[1].split(',')
    BioReplicate[strain]=[]
    TimeCourse[strain]={}
    strainRecord.append(strain)
    for repli in Replicates:
        BioReplicate[strain].append(repli)
        Well_strain_dic[repli]=strain
        if repli in wellRecord:
            print 'Wired Configure!!!'
        else:
            wellRecord.append(repli)
f.close()

# processing the raw data
TimeRecord=[]
f=open(raw_data,'r')
for line in f:
    row=line.rstrip().split('\t')
    if row[0]=='Time [s]':
        timeseries=row[1:]
        for timepoint in timeseries:
            TimeRecord.append(float(timepoint)/3600)
        timeseries=row[1:]
        for strain in TimeCourse:
            TimeCourse[strain]['Raw']={}
            for number,timepoint in enumerate(timeseries):
                TimeCourse[strain]['Raw'][number]=[]
        break
f.close()

f=open(raw_data,'r')
flag=False
for line in f:
    row=line.rstrip().split('\t')
    if row[0] in wellRecord:
        well=row[0]
        strain=Well_strain_dic[well]
        flag=True
    elif row[0] in AllWell:
        flag=False
    if row[0]=='Mean' and flag:
        for number,OD in enumerate(row[1:]):
            TimeCourse[strain]['Raw'][number].append(float(OD))
f.close()

# afterwards, all data was processed as dic
# {strain:{'Raw':{'0':[OD1,OD2,OD3],'1':[], ...}}}
# then we need to extract the average and stdev

for strain in TimeCourse:
    TimeCourse[strain]['Mean']=[]
    TimeCourse[strain]['STDEV']=[]
    for number in TimeCourse[strain]['Raw']:
        print strain
        print TimeCourse[strain]['Raw'][number]
        average=np.mean(TimeCourse[strain]['Raw'][number])
        stdev=np.std(TimeCourse[strain]['Raw'][number])
        TimeCourse[strain]['Mean'].append(average)
        TimeCourse[strain]['STDEV'].append(stdev)

# output face
os.system('cat /dev/null > %s.processedmean.txt'%(prefix))
g=open('%s.processedmean.txt'%(prefix),'r+')
os.system('cat /dev/null > %s.processedstd.txt'%(prefix))
k=open('%s.processedstd.txt'%(prefix),'r+')
g.write('Time/h\t')
k.write('Time/h\t')
writtenLine=''
for timepoint in TimeRecord:
    writtenLine+=str(timepoint)+'\t'
g.write(writtenLine[:-1]+'\n')
k.write(writtenLine[:-1]+'\n')

for strain in strainRecord:
    g.write('%s\t'%(strain))
    k.write('%s\t'%(strain))
    writtenLineG=''
    writtenLineK=''
    for mean in TimeCourse[strain]['Mean']:
        writtenLineG+=str(mean)+'\t'
    for stdev in TimeCourse[strain]['STDEV']:
        writtenLineK+=str(stdev)+'\t'
    g.write(writtenLineG[:-1]+'\n')
    k.write(writtenLineK[:-1]+'\n')
g.close()
k.close()
    
            
        



    