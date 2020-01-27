#%%
#Class testing

import os, sys, inspect
import pandas
currentdir = 'C:\\Users\\reneg\\Documents\\ComputationalB\\scobra\\Ntara'
gparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, gparentdir)
import scobra
ntara=currentdir+"/ntaratest.xlsx"
soy=currentdir+"/Models/soybean.xls"
from Ntara.BuildModelGRF import *

#%%
n=scobra.Model(ntara)
a=scobra.model(n)
b=scobra.model.ImbalanceReactions(a)

#%%
imb=Imbalancedreac(b,soy)
#%%
test=imb.list_imbalances()
a=imb.reference(test)
#%%
#pandas.DataFrame.from_dict(a,orient='index').to_excel('NTARA New ImbalancedReactions.xlsx')
#%%
test=Test(soy, '01Aug')
a=test.sortcpm(['_tx', '_mc', '_pc','_vc','_xc', '_biomass'])
test.test_model(a)
#test.atp_model(a)
#%%

def getreac(targetpath,fluxpath,reacref,name,*biomasses):
    '''Gets the Reactions (that produce the Biomasses from Solution Fluxes) from Reference and stores it into [name] Biomass Reactions.xlsx
    '''
    #puts reactions into lists
    writer= pandas.ExcelWriter('TESTSoybean_Reactions.xlsx')
    ref=pandas.read_excel(reacref, sheet_name = 'Reaction List')

    for biomass in biomasses:
        sheet=pandas.read_excel(fluxpath, sheet_name = biomass, sep = '\t')
        target=pandas.read_excel(targetpath, sheet_name = 'Reaction List', sep = '\t')
        sheet['Abbreviation']=sheet.index
        sheet['Abbreviation']=sheet.loc[sheet.iloc[:,0]!=0].iloc[:,1]
        c=target['Abbreviation'][target['Abbreviation'].isin(sheet['Abbreviation'])]
        result=pandas.DataFrame(sheet.loc[:,['Abbreviation','fluxes']][~sheet['Abbreviation'].isin(c)]).dropna().reset_index().drop('index',axis=1)
        
        data=ref['Abbreviation'].isin(result.iloc[:,0])
        ref_final=pandas.DataFrame(ref[data].loc[:,['Abbreviation','Reaction']].copy()).dropna().reset_index().drop('index',axis=1) 
        final= pandas.merge(result,ref_final,on='Abbreviation')
        final.to_excel(writer,sheet_name=biomass,index=False,header=False)        
    writer.save()

flux=currentdir+'/01Aug Solution Fluxes.xlsx'
getreac(ntara,flux,soy,'Soybean','Cellulose_biomass','Starch_biomass','pARG_biomass','pASN_biomass','pGLN_biomass','pGLU_biomass','pGLY_biomass','pLEU_biomass','pLYS_biomass','pMET_biomass','pPRO_biomass','pTHR_biomass','pVAL_biomass','s2KG_biomass','sARG_biomass','sCIT_biomass','sGABA_biomass','sGLN_biomass','sGLU_biomass','sGLYCOLATE_biomass','sISOCIT_biomass','sLEU_biomass', 'sLYS_biomass','sMET_biomass','sORN_biomass','sPRO_biomass', 'sPYROGLU_biomass','sSUC_biomass','sTHR_biomass')



#%%
df.loc[df.iloc[:,1]=='B'].iloc[:,0]
df.loc[df.iloc[:,0]!=0].iloc[:,1]

sheet.loc[sheet.iloc[:,0]!=0].index
#returns all non-zero reactions
#returns all non-zero reactions WITHIN target

#%%



#check if ntara biomass not optimal but in soybean, get non-zero reactions
#not lump biomass with stoic

