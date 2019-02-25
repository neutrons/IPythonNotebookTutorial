#!/usr/bin/env python

"""
Andrie's comments on the workflow

Events in TOF -> Events in dE ----> /Van -> Histogram, dE (good for horace-alike. not the best normalization)
                               |
                               ---> /1.0 -> Events (best normalization: normalization by Van is done later)

In the future, it is better to save the reduced nxs (events with pixel and dE)
without the vanadium calibration because this should be done at the later step.

The traditional approach of saving reduced nxs with V calib was because of the
ease of working with horace or mslice, which need data that is calibrated.
"""

import sys,os
sys.path.append("/opt/Mantid/bin")
from mantid.simpleapi import *
from matplotlib import *
use("agg")
from matplotlib.pyplot import *
# Logs at: /var/log/SNS_applications/autoreduce.log
import numpy
from ARLibrary import * #note that ARLibrary would set mantidpath as well
import warnings
warnings.simplefilter('ignore')



# parameters
RawVanadium="/SNS/SEQ/IPTS-16076/nexus/SEQ_102084.nxs.h5"
processed_van_file = None
ProcessedVanadium="van102084_nov_2016_2x2.nxs"
Emin=-0.5
Emax=0.95
Estep=0.005
grouping="/SNS/SEQ/shared/autoreduce/SEQ_1x1_grouping.xml" #allowed values 1x1, 2x1, 4x1, 8x1, 8x2 powder
create_elastic_nxspe=True

# additional parameters
numpy.seterr("ignore")#ignore division by 0 warning in plots
#processing parameters
HardMaskFile=''
IntegrationRange=[0.3,1.2] #integration range for Vanadium in angstroms
MaskBTPParameters=[]
def updateMask():
    MaskBTPParameters.append({'Pixel': '1-7,122-128'})
    MaskBTPParameters.append({'Bank': '114,115,75,76,38,39'})
    MaskBTPParameters.append({'Tube': '2-4', 'Pixel': '30-35', 'Bank': '88'})
    MaskBTPParameters.append({'Tube': '7-8', 'Pixel': '99-128', 'Bank': '127'})
    MaskBTPParameters.append({'Bank': '99-102'})
    MaskBTPParameters.append({'Pixel': '120-128', 'Bank': '38-42'})
    MaskBTPParameters.append({'Pixel': '119-128', 'Bank': '43'})
    MaskBTPParameters.append({'Pixel': '120-128', 'Bank': '44-48'})
    MaskBTPParameters.append({'Tube': '1,5', 'Bank': '44'})
    MaskBTPParameters.append({'Tube': '8', 'Bank': '63'})
    MaskBTPParameters.append({'Tube': '8', 'Bank': '70'})
    MaskBTPParameters.append({'Tube': '8', 'Pixel': '1-95', 'Bank': '74'})
    MaskBTPParameters.append({'Tube': '8', 'Bank': '96'})
    MaskBTPParameters.append({'Tube': '8', 'Bank': '109'})
    MaskBTPParameters.append({'Pixel': '113-128', 'Bank': '130-132'})
    MaskBTPParameters.append({'Tube': '4', 'Bank': '148'})
    MaskBTPParameters.append({'Tube': '5', 'Bank': '45'})
    MaskBTPParameters.append({'Bank': '62'})
    MaskBTPParameters.append({'Tube': '1,3-6,8', 'Bank': '119'})
    MaskBTPParameters.append({'Tube': '6-8', 'Pixel': '105-110', 'Bank': '46'})
 
    return
updateMask()
#uninstalled packs at far left
#MaskBTPParameters.append({'Bank':"114,115,75,76,38,39"})

#examples of how to mask, but these should be done with the web interface.
#MaskBTPParameters.append({'Bank':"62,92"})
#MaskBTPParameters.append({'Bank':"98",'Tube':"6-8"})
#MaskBTPParameters.append({'Bank':"108",'Tube':"4"})
#MaskBTPParameters.append({'Bank':"141"})
#MaskBTPParameters.append({'Bank':"70"})

#MaskBTPParameters.append({'Pixel': '1-8,121-128'})
#MaskBTPParameters.append({'Bank': '114,115,75,76,38,39'})
#MaskBTPParameters.append({'Tube': '1', 'Bank': '116'})

clean=True
NXSPE_flag=True

NormalizedVanadiumEqualToOne = True


def preprocessVanadium(Raw,Processed,Parameters):
    if os.path.isfile(Processed):
        LoadNexus(Filename=Processed,OutputWorkspace="__VAN")
        dictvan={'UseProcessedDetVan':'1','DetectorVanadiumInputWorkspace':'__VAN'}
    else:
        LoadEventNexus(Filename=Raw,OutputWorkspace="__VAN",Precount=0)
        # adjust time for pack B15 wired strangely
        #ChangeBinOffset(InputWorkspace="__VAN",OutputWorkspace="__VAN",Offset=500,IndexMin=14336,IndexMax=15359) 
        for d in Parameters:
            MaskBTP(Workspace="__VAN",**d)
        dictvan={'SaveProcessedDetVan':'1','DetectorVanadiumInputWorkspace':'__VAN','SaveProcDetVanFilename':Processed}
    return dictvan
        
def preprocessData(filename, setEi=None):
    f1 = os.path.split(filename)[-1]
    runnum = int(f1.strip('SEQ_').replace('.nxs.h5',''))
    __MonWS=LoadNexusMonitors(Filename=filename)

    #Example of PV streamer not running. Copying logs from some other run
    #if (runnum >= 55959 and runnum <= 55960):
    #    LoadNexusLogs(__MonWS,"/SNS/SEQ/IPTS-10531/nexus/SEQ_55954.nxs.h5")
    #
    
    #Example of filtering by a logvalue
    #FilterByLogValue("__MonWS",OutputWorkspace="__MonWS",LogName="CCR22Rot",MinimumValue=52.2,MaximumValue=52.4)

    if setEi:
        Eguess = setEi
    else:
        Eguess=__MonWS.getRun()['EnergyRequest'].getStatistics().mean
    #check whether the fermi chopper is in the beam
    fermi=__MonWS.run().getProperty('vChTrans').value[0]

    if fermi == 2 :
        Efixed = numpy.nan
        T0 = numpy.nan
        
    else:
        [Efixed,T0]=GetEiT0atSNS("__MonWS",Eguess)

    #Load an event Nexus file
    LoadEventNexus(Filename=filename,OutputWorkspace="__IWS",Precount=0) 

    #Fix that all time series log values start at the same time as the proton_charge
    CorrectLogTimes('__IWS')
    
    # adjust time for pack B15 wired strangely
    #ChangeBinOffset(InputWorkspace="__IWS",OutputWorkspace="__IWS",Offset=500,IndexMin=14336,IndexMax=15359)

    #delete all bad pulses below   10% of the average of the file.
    FilterBadPulses(InputWorkspace="__IWS",OutputWorkspace = "__IWS",LowerCutoff = 10)
    AddSampleLogMultiple("__IWS","CalculatedEi,CalculatedT0",str(Efixed)+','+str(T0))
    return [Eguess,Efixed,T0]
  
    
def WS_clean():
    DeleteWorkspace('__IWS')
    DeleteWorkspace('__OWS')
    DeleteWorkspace('__VAN')
    DeleteWorkspace('__MonWS')
    

def run(filename, outdir, setEi=None):
    DGSdict=preprocessVanadium(RawVanadium, processed_van_file, MaskBTPParameters)
    #--------------------------------------
    #Preprocess data to get Ei and T0
    #--------------------------------------
    [EGuess,Ei,T0]=preprocessData(filename, setEi=setEi)
    """

    if os.path.isfile(outdir+'experiment_log.csv'):
        fm='fastappend'
    else:
        fm='new'
        
    snames='RunNumber,Title,Comment,StartTime,EndTime,Duration,ProtonCharge,'+\
    'vChTrans,Speed1,Speed1,Speed1,Phase1,Phase1,Phase1,Speed2,Speed2,Speed2,'+\
    'Phase2,Phase2,Phase2,Speed3,Speed3,Speed3,Phase3,Phase3,Phase3,EnergyRequest,s1t,s1r,s1l,s1b,'+\
    'vAttenuator2,vAttenuator1,svpressure,svpressure,svpressure,dvpressure,dvpressure,dvpressure'+\
    'phi,phi,phi,Lakeshore1SensorA,Lakeshore1SensorA,Lakeshore1SensorA,'+\
    'Lakeshore1SensorB,Lakeshore1SensorB,Lakeshore1SensorB,'+\
    'Lakeshore1SensorC,Lakeshore1SensorC,Lakeshore1SensorC,'+\
    'Lakeshore1SensorD,Lakeshore1SensorD,Lakeshore1SensorD,'+\
    'Lakeshore2SensorA,Lakeshore2SensorA,Lakeshore2SensorA,'+\
    'Lakeshore2SensorB,Lakeshore2SensorB,Lakeshore2SensorB,'+\
    'Lakeshore2SensorC,Lakeshore2SensorC,Lakeshore2SensorC,'+\
    'Lakeshore2SensorD,Lakeshore2SensorD,Lakeshore2SensorD,'+\
    'SampleTemperatureOrangeCryo,SampleTemperatureOrangeCryo,SampleTemperatureOrangeCryo,CalculatedEi,CalculatedT0'
    
    stitles='RunNumber,Title,Comment,StartTime,EndTime,Duration,ProtonCharge,'+\
    'vChTrans,Speed1min,Speed1max,Speed1avg,Phase1min,Phase1max,Phase1avg,Speed2min,Speed2max,Speed2avg,'+\
    'Phase2min,Phase2max,Phase2avg,Speed3min,Speed3max,Speed3avg,Phase3min,Phase3max,Phase3avg,'+\
    'EnergyRequest,s1t,s1r,s1l,s1b,'+\
    'vAttenuator2,vAttenuator1,svpressuremin,svpressuremax,svpressureavg,dvpressuremin,dvpressuremax,dvpressureavg'+\
    'phimin,phimax,phiavg,Lakeshore1SensorAmin,Lakeshore1SensorAmax,Lakeshore1SensorAavg,'+\
    'Lakeshore1SensorBmin,Lakeshore1SensorBmax,Lakeshore1SensorBavg,'+\
    'Lakeshore1SensorCmin,Lakeshore1SensorCmax,Lakeshore1SensorCavg,'+\
    'Lakeshore1SensorDmin,Lakeshore1SensorDmax,Lakeshore1SensorDavg,'+\
    'Lakeshore2SensorAmin,Lakeshore2SensorAmax,Lakeshore2SensorAavg,'+\
    'Lakeshore2SensorBmin,Lakeshore2SensorBmax,Lakeshore2SensorBavg,'+\
    'Lakeshore2SensorCmin,Lakeshore2SensorCmax,Lakeshore2SensorCavg,'+\
    'Lakeshore2SensorDmin,Lakeshore2SensorDmax,Lakeshore2SensorDavg,'+\
    'SampleTemperatureOrangeCryomin,SampleTemperatureOrangeCryomax,SampleTemperatureOrangeCryoavg,CalculatedEi,CalculatedT0'
    
    
    soperations = ['0']*len(snames.split(','))
    
    for i,name in enumerate(stitles.split(',')):
        name=name.strip()
        if name in ['RunNumber','Title','Comment','StartTime','EndTime']:
            soperations[i] = 'None'
        if name.find('min') == len(name)-3:
            soperations[i] = 'min'
        if name.find('max') == len(name)-3:
            soperations[i] = 'max'
        if name.find('avg') == len(name)-3:
            soperations[i] = 'average'
                           
    
    ExportExperimentLog(InputWorkspace = '__IWS',
                        OutputFilename = outdir+'experiment_log.csv',
                        FileMode = fm,
                        SampleLogNames = snames,
                        SampleLogTitles = stitles,
                        SampleLogOperation = ','.join(soperations),
                        FileFormat = "comma (csv)",
                        TimeZone = "America/New_York")
    """
    elog=ExperimentLog()
    elog.setLogList('vChTrans,Speed1,Phase1,Speed2,Phase2,Speed3,Phase3,EnergyRequest,s1t,s1r,s1l,s1b,s2t, s2r, s2l, s2b,  vAttenuator2,vAttenuator1,svpressure,dvpressure,Lakeshore1SensorA, Lakeshore1SensorB, Lakeshore2SensorB')
    elog.setSimpleLogList("vChTrans, EnergyRequest, s1t, s1r, s1l, s1b, s2t, s2r, s2l, s2b, vAttenuator2, vAttenuator1, Lakeshore1SensorA, Lakeshore1SensorB, Lakeshore2SensorB")
    elog.setSERotOptions('CCR13VRot, SEOCRot, CCR16Rot, CCR22Rot,phi')
    elog.setSETempOptions('SampleTemp, sampletemp, SensorA, SensorA340 ')
    elog.setFilename(outdir+'experiment_log.csv')
    angle=elog.save_line('__MonWS',CalculatedEi=Ei,CalculatedT0=T0)
    
    outpre='SEQ'
    runnum=str(mtd['__IWS'].getRunNumber()) 
    outfile=outpre+'_'+runnum+'_autoreduced'
    if not numpy.isnan(Ei):
        DGSdict['SampleInputWorkspace']='__IWS'
        DGSdict['SampleInputMonitorWorkspace']='__MonWS'
        DGSdict['IncidentEnergyGuess']=Ei
        DGSdict['UseIncidentEnergyGuess']='1'
        DGSdict['TimeZeroGuess']=T0
        DGSdict['EnergyTransferRange']=[Emin*EGuess,Estep*EGuess,Emax*EGuess]  #Typical values are -0.5*EGuess, 0.005*EGuess, 0.95*EGuess
        DGSdict['SofPhiEIsDistribution']='0' # keep events
        DGSdict['HardMaskFile']=HardMaskFile
        DGSdict['GroupingFile']=grouping   #'/SNS/SEQ/shared/autoreduce/SEQ_2x2_grouping.xml' #Typically an empty string '', choose 2x1 or some other grouping file created by GenerateGroupingSNSInelastic or GenerateGroupingPowder
        DGSdict['IncidentBeamNormalisation']='None'  #NEXUS file does not have any normaliztion, but the nxspe IS normalized later in code by charge
        DGSdict['UseBoundsForDetVan']='1'
        DGSdict['DetVanIntRangeHigh']=IntegrationRange[1]
        DGSdict['DetVanIntRangeLow']=IntegrationRange[0]
        DGSdict['DetVanIntRangeUnits']='Wavelength'
        DGSdict['OutputWorkspace']='__OWS'
        DgsReduction(**DGSdict)
        

        if create_elastic_nxspe:
            DGSdict['OutputWorkspace']='reduce_elastic'
            EGuess=DGSdict['IncidentEnergyGuess']
            DGSdict['EnergyTransferRange']=[-0.02*EGuess,0.005*EGuess,0.02*EGuess]
            DgsReduction(**DGSdict)
            nxspe_filename=os.path.join(outdir, "elastic","SEQ_" + runnum + "_elastic.nxspe")
            SaveNXSPE(Filename=nxspe_filename, InputWorkspace="reduce_elastic", Psi=angle, KiOverKfScaling='1')
            os.chmod(nxspe_filename,0664)

        #Do normalization of vanadum to 1
        # This step only runs ONCE if the processed vanadium file is not already present.
        if DGSdict.has_key('SaveProcessedDetVan') and NormalizedVanadiumEqualToOne:
              filename=DGSdict['SaveProcDetVanFilename']
              LoadNexus(Filename=filename,OutputWorkspace="__VAN")
              datay = mtd['__VAN'].extractY()
              meanval = float(datay[datay>0].mean())
              CreateSingleValuedWorkspace(OutputWorkspace='__meanval',DataValue=meanval)
              #Divide the vanadium by the mean
              Divide(LHSWorkspace='__VAN',RHSWorkspace='__meanval',OutputWorkspace='__VAN')
              #multiple by the mean of vanadium Normalized data = Data / (Van/meanvan) = Data *meanvan/Van
              # this is because in DgsReduction the output data was already normalized by vanadium data.
              # The only thing is that the normalization of vanadium to 1 is happening afterwards 
              # right here in this section. So we need to compensate for that.
              Multiply(LHSWorkspace='__OWS',RHSWorkspace='__meanval',OutputWorkspace='__OWS') 
              SaveNexus(InputWorkspace="__VAN", Filename= filename)        
        
        SaveNexus(InputWorkspace="__OWS", Filename= outdir+outfile+".nxs")
        RebinToWorkspace(WorkspaceToRebin="__OWS",WorkspaceToMatch="__OWS",OutputWorkspace="__OWS",PreserveEvents='0')
        NormaliseByCurrent(InputWorkspace="__OWS",OutputWorkspace="__OWS")
        #Divide by bin width
        ConvertToDistribution(Workspace="__OWS") 
        #generate summed spectra_plot		                                                                
#---------------------------------------          
        s=SumSpectra("__OWS")
        x=s.readX(0)
        y=s.readY(0)
        # where is postprocessing?
        try:
            from postprocessing.publish_plot import plot1d
            plot1d(runnum, [x[1:], y], instrument='SEQ', 
                x_title="Energy transfer (meV)",
                y_title="Intensity", y_log=True)
        except:
            logger.error("Failed to publish plot")
        
        if NXSPE_flag:    
            angle=mtd["__OWS"].run()['phi'].getStatistics().mean      
            SaveNXSPE(InputWorkspace="__OWS", Filename= outdir+outfile+".nxspe",Efixed=Ei,Psi=angle,KiOverKfScaling=True)
            GenerateGroupingPowder(InputWorkspace="__OWS",AngleStep=0.5, GroupingFilename=outdir+'powdergroupfile.xml')
            GroupDetectors(InputWorkspace="__OWS", OutputWorkspace="powdergroupdata", MapFile=outdir+'powdergroupfile.xml',Behaviour='Average')
            SaveNXSPE(InputWorkspace="powdergroupdata", Filename= outdir+"/powder/"+outfile+"_powder.nxspe",
                      Efixed=Ei,Psi=angle,KiOverKfScaling=True,ParFile=outdir+'powdergroupfile.par') 
        if clean:
            WS_clean()
    else:
       ConvertUnits(InputWorkspace="__IWS",OutputWorkspace="__IWS",Target='dSpacing')
       Rebin(InputWorkspace="__IWS",OutputWorkspace="__OWS",Params='0.5,0.005,10',PreserveEvents='0')
       SaveNexus(InputWorkspace="__OWS", Filename= outdir+outfile+".nxs")
                                                    
    return


# dictionary of rrm indexed by the primary Ei
rrm_Eis = {
    120: 20,
    2000: 48,
    1000: 42.8,
    900: 41.8,
    800: 40.8,
    700: 39.6,
    600: 38.0,
    500: 36.3,
    400: 34.0,
    300: 31.7,
    }

def checkRRM(path):
    import h5py
    f = h5py.File(path)
    logs = f['entry/DASlogs']
    try:
        aem = logs['AutoEiMode']
    except:
        return
    v = aem['value'][0]
    vs = aem['value_strings'][0][0]
    rt = v==3 and vs=='RRM'
    f.close()
    return rt

def getEiGuess(filename):
    f1 = os.path.split(filename)[-1]
    runnum = int(f1.strip('SEQ_').replace('.nxs.h5',''))
    __MonWS=LoadNexusMonitors(Filename=filename)
    Eguess=__MonWS.getRun()['EnergyRequest'].getStatistics().mean
    return Eguess


def main():
    #check number of arguments
    if (len(sys.argv) != 3): 
        print "autoreduction code requires a filename and an output directory"
        sys.exit()
    if not(os.path.isfile(sys.argv[1])):
        print "data file ", sys.argv[1], " not found"
        sys.exit()
    else:
        filename = sys.argv[1]
        outdir = sys.argv[2]
        if filename.endswith('.nxs'):
            outdir+='LEGACY/'

    # trival preprocessing of parameters
    global processed_van_file
    processed_van_file = ProcessedVanadium
    if not os.path.isabs(processed_van_file):
        processed_van_file = os.path.join(outdir, ProcessedVanadium)

    # save autoreduce script in the output directory
    ar_changed=check_newer_script("SEQ",outdir)
    # write readme
    write_readme(outdir, ['log', 'ar_script', 'dE_event_nxs', 'elastic_nxspe', 'dE_nxspe', 'powder_nxspe'])
    
    # check if it is RRM
    if checkRRM(filename):
        # get primary Ei guess
        Ei_primary = getEiGuess(filename)
        if Ei_primary < 150:
            Ei_primary = int(round(Ei_primary, -1))
        else:
            Ei_primary = int(round(Ei_primary, -2))
        Ei_2ndary = rrm_Eis[Ei_primary]
        print " * RRM is on. Secondary Ei: %s" % Ei_2ndary
    else:
        Ei_2ndary = None

    # primary
    run(filename, outdir)

    if Ei_2ndary:
        global create_elastic_nxspe
        create_elastic_nxspe=False
        outdir2 = os.path.join(outdir, 'rrm_%smeV'%Ei_2ndary)
        if not os.path.exists(outdir2):
            os.makedirs(outdir2)
        outdir2 += '/'
        run(filename, outdir2, setEi=Ei_2ndary)
    return

if __name__ == '__main__': main()
