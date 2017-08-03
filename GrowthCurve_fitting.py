import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import math
import matplotlib.pyplot as plt
from random import randint

ODdata=sys.argv[1]
incubation=float(sys.argv[2])
medium=sys.argv[3] # either LB or MOPS or M9YE
TimeLimit=float(sys.argv[4]) # data before which is used
prefix=sys.argv[5]
# parameter guess for ODmax, umax and lag time/h
p_guess=[0.5,0.3,5]

figure_print=False
flag=raw_input("Whether you would like to print growth curve figure (yes or no):   ")
if flag=='yes':
    figure_print=True
print 'print figure!'

# threshold to judge growth
growthThre=0.1
# max OD for figure
ODLimit=0.3

# convert Tecan read to OD600
def tecan_to_OD(tecanLst,medium,incubation):
    ODLst=[]
    if medium=='MOPS':
        for value in tecanLst:
            tecan=float(value)
            ODLst.append(2.7228*tecan**2+0.58*tecan-0.1064)
    elif medium=='LB':
        for value in tecanLst:
            tecan=float(value)
            ODLst.append(3.0125*tecan-0.5457)
    elif medium=='M9YE':
        for value in tecanLst:
            tecan=float(value)
            ODLst.append(2.3606*tecan-0.358)
    else:
        print 'unrecorded medium!!'
        sys.exit(1)
    ODini=np.mean(ODLst[:3])
    BlankremovedLst=[]
    for ODvalue in ODLst:
        BlankremovedLst.append(ODvalue-ODini+incubation)
    return BlankremovedLst


strainRecord=[]
DataSet={}
f=open(ODdata,'r')
TimeRecord=[]
Point_limit=0 # point number that exceeding time limit
for line in f:
    row=line.rstrip().split('\t')
    if row[0]=='Time/h':
        for i,time in enumerate(row[1:]):
            time=float(time)
            TimeRecord.append(time)
            if time>TimeLimit:
                Point_limit=i+2
                break
    else:
        strain=row[0]
        strainRecord.append(strain)
        DataSet[strain]={}
        DataSet[strain]['OD']=tecan_to_OD(row[1:Point_limit],medium,incubation)
        DataSet[strain]['Category']=''
        DataSet[strain]['Lag']=TimeLimit+float(randint(-1000,1000))/10000
        DataSet[strain]['Umax']=float(randint(-1000,1000))/100000
        DataSet[strain]['StationaryOD']=float(randint(-1000,1000))/50000
f.close()

# Gompertz equation to fit
def fitting_function(x, a,umax,lag):
    #a = upper asymptote
    #b = negative = x axis displacement
    #c = negative = growth rate
    return a*(np.exp(-np.exp(umax*(math.e)*(lag-x)/a+1)))

# linear regression to fit
def linear_regression(x, slope,intercept):
    return slope*x+intercept

# define ODlast/2=Log50;  Firstreachof0.9*ODlast+3h=Steady
for strain in strainRecord:
    ODlast=np.mean(DataSet[strain]['OD'][-3:])
    ODini=np.mean(DataSet[strain]['OD'][:3])
    ODmax=max(DataSet[strain]['OD'])
    sigOD = [ODvalue for ODvalue in DataSet[strain]['OD'] if ODvalue >= growthThre]
    x1=[]
    y1=[]
    if len(sigOD)<=3:
        DataSet[strain]['Category']='Nogrowth'
        DataSet[strain]['StationaryOD']=ODmax
    elif ODlast*1.2<ODmax:
        DataSet[strain]['Category']='Deadphase'
        # remove dead phase and do fitting
        for i,ODvalue in enumerate(DataSet[strain]['OD']):
            time=TimeRecord[i]
            if time>0.5:
                x1.append(time)
                y1.append(ODvalue)
            if ODvalue>=ODmax or time>TimeLimit:
                break
        x1=np.array(x1)
        y1=np.array(y1)
        pars, pcov = opt.curve_fit(fitting_function, x1, y1, p_guess, maxfev=10000)
        DataSet[strain]['StationaryOD']=pars[0]
        DataSet[strain]['Umax']=pars[1]
        DataSet[strain]['Lag']=pars[2]
    elif ODlast*1.2>ODmax:
        # do fitting
        for i,ODvalue in enumerate(DataSet[strain]['OD']):
            time=TimeRecord[i]
            if time>0.5:
                x1.append(time)
                y1.append(ODvalue)
            if time>TimeLimit:
                break
        x1=np.array(x1)
        y1=np.array(y1)
        pars, pcov = opt.curve_fit(fitting_function, x1, y1, p_guess, maxfev=10000)
        pars_linear, pcov_linear = opt.curve_fit(linear_regression, x1[-5:], y1[-5:], p0=[0.1,0], maxfev=10000)
        slope=pars_linear[0]
        print 'strain:  %s  lastSlope:  %s  umax:  %s'%(strain,str(slope)[:5],str(pars[1])[:5])
        if (slope>0 and slope>0.33*pars[1]):  # the growth didn't reach stationary phase 
            DataSet[strain]['Category']='Linear'
            pars_linearAll, pcov_linearAll = opt.curve_fit(linear_regression, x1[3:], y1[3:], p0=[0.1,0], maxfev=10000)
            DataSet[strain]['StationaryOD']=pars_linearAll[0]*TimeLimit+pars_linearAll[1]
            DataSet[strain]['Umax']=pars_linearAll[0]
        else:
            DataSet[strain]['Category']='Normal'
            DataSet[strain]['StationaryOD']=pars[0]
            DataSet[strain]['Umax']=pars[1]
            DataSet[strain]['Lag']=pars[2]
    else:
        DataSet[strain]['Category']='Others'
        DataSet[strain]['StationaryOD']=ODmax

os.system('cat /dev/null > %s_fitting.txt'%(prefix))
g=open('%s_fitting.txt'%(prefix),'r+')
g.write('Construct\tCategory\tstationaryOD\tUmax\tLag\n')
for strain in strainRecord:
    category=DataSet[strain]['Category']
    staOD=DataSet[strain]['StationaryOD']
    umax=DataSet[strain]['Umax']
    lag=DataSet[strain]['Lag']
    if figure_print:
        plt.plot(np.array(TimeRecord),np.array(DataSet[strain]['OD']))
        plt.title('%s--%s--staOD:%s--umax:%s--lag/h:%s'%(strain,category,str(staOD)[:5],str(umax)[:5],str(lag)[:5]))
        plt.xlim(0,TimeLimit)
        plt.ylim(0,ODLimit)
        plt.show()
    g.write('%s\t%s\t%s\t%s\t%s\n'%(strain,category,str(staOD),str(umax),str(lag)))
g.close()
