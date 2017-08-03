import os
import sys
import numpy as np

ODdata=sys.argv[1]
FLUdata=sys.argv[2]
ODstdev=sys.argv[3]
FLUstdev=sys.argv[4]
prefix=sys.argv[5]
step=0.38
SteadyReachRange=1

strainRecord=[]
DataSet={}
f=open(ODdata,'r')
TimeRecord=[]
for line in f:
    row=line.rstrip().split('\t')
    if row[0]!='Time/h':
        strainRecord.append(row[0])
        DataSet[row[0]]={}
        DataSet[row[0]]['OD']=row[1:]
    else:
        TimeRecord=row[1:]
f.close()

f=open(ODstdev,'r')
for line in f:
    row=line.rstrip().split('\t')
    if row[0]!='Time/h':
        strain=row[0]
        DataSet[strain]['ODstdev']=row[1:]
f.close()

f=open(FLUstdev,'r')
for line in f:
    row=line.rstrip().split('\t')
    if row[0]!='Time/h':
        strain=row[0]
        DataSet[strain]['FLUstdev']=row[1:]
f.close()

f=open(FLUdata,'r')
for line in f:
    row=line.rstrip().split('\t')
    if row[0]!='Time/h':
        DataSet[row[0]]['FLU']=row[1:]
        DataSet[row[0]]['ODLog50']='0.0'
        DataSet[row[0]]['ODLog50stdev']='0.0'
        DataSet[row[0]]['FLULog50']='0.0'
        DataSet[row[0]]['FLULog50stdev']='0.0'
        DataSet[row[0]]['ODSteady']='0.0'
        DataSet[row[0]]['ODSteadystdev']='0.0'
        DataSet[row[0]]['FLUSteady']='0.0'
        DataSet[row[0]]['FLUSteadystdev']='0.0'
        DataSet[row[0]]['TimeLog50']='0.0'
        DataSet[row[0]]['TimeSteady']='0.0'
f.close()

# define ODlast/2=Log50;  Firstreachof0.9*ODlast+3h=Steady
for strain in strainRecord:
    ODlastSTDEV=np.std([float(DataSet[strain]['OD'][-3]),float(DataSet[strain]['OD'][-2]),float(DataSet[strain]['OD'][-1])])
    ODlast=(float(DataSet[strain]['OD'][-3])+float(DataSet[strain]['OD'][-2])+float(DataSet[strain]['OD'][-1]))/3
    ODini=(float(DataSet[strain]['OD'][0])+float(DataSet[strain]['OD'][1])+float(DataSet[strain]['OD'][2]))/3
    #print '%s\t%s'%(strain,str(ODlast))
    # if growth
    if (ODlast-ODini)>0.2 and (ODlast>0.9 or ODlastSTDEV<0.1):
        Log50=ODini+(ODlast-ODini)*0.4
        Steady=ODlast*0.9
        flagLog=False
        flagSteady=False
        SteadyCount=0
        Log50Time=0
        SteadyTime=0
        for i,ODvalue in enumerate(DataSet[strain]['OD']):
            if float(ODvalue)>Log50 and flagLog==False:
                ODLog50=ODvalue
                ODLog50stdev=DataSet[strain]['ODstdev'][i]
                FluLog50=DataSet[strain]['FLU'][i]
                FluLog50stdev=DataSet[strain]['FLUstdev'][i]
                Log50Time=TimeRecord[i]
                flagLog=True
            if float(ODvalue)>Steady and flagSteady==False:
                SteadyCount+=1
            if SteadyCount>SteadyReachRange/step and flagSteady==False:
                ODSteady=ODvalue
                ODSteadystdev=DataSet[strain]['ODstdev'][i]
                FluSteady=DataSet[strain]['FLU'][i]
                FluSteadystdev=DataSet[strain]['FLUstdev'][i]
                SteadyTime=TimeRecord[i]
                flagSteady=True
            if flagSteady and flagLog:
                DataSet[strain]['ODLog50']=ODLog50
                DataSet[strain]['ODLog50stdev']=ODLog50stdev
                DataSet[strain]['FLULog50']=FluLog50
                DataSet[strain]['FLULog50stdev']=FluLog50stdev
                DataSet[strain]['ODSteady']=ODSteady
                DataSet[strain]['ODSteadystdev']=ODSteadystdev
                DataSet[strain]['FLUSteady']=FluSteady
                DataSet[strain]['FLUSteadystdev']=FluSteadystdev
                DataSet[strain]['TimeLog50']=Log50Time
                DataSet[strain]['TimeSteady']=SteadyTime
                break

os.system('cat /dev/null > %s_ExtractedLogSteady.txt'%(prefix))
g=open('%s_ExtractedLogSteady.txt'%(prefix),'r+')
g.write('Construct\tLog50Time\tLog50OD\tLog50FLU\tSteadyTime\tSteadyOD\tSteadyFLU\tLog50ODstdev\tLog50FLUstdev\tSteadyODstdev\tSteadyFLUstdev\n')
for strain in strainRecord:
    ODLog50=DataSet[strain]['ODLog50']
    ODLog50stdev=DataSet[strain]['ODLog50stdev']
    FluLog50=DataSet[strain]['FLULog50']
    FluLog50stdev=DataSet[strain]['FLULog50stdev']
    ODSteady=DataSet[strain]['ODSteady']
    ODSteadystdev=DataSet[strain]['ODSteadystdev']
    FluSteady=DataSet[strain]['FLUSteady']
    FluSteadystdev=DataSet[strain]['FLUSteadystdev']
    Log50Time=DataSet[strain]['TimeLog50']
    SteadyTime=DataSet[strain]['TimeSteady']
    g.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(strain,Log50Time,ODLog50,FluLog50,SteadyTime,ODSteady,FluSteady,ODLog50stdev,FluLog50stdev,ODSteadystdev,FluSteadystdev))
g.close()


          

