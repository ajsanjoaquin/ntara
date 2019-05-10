
# coding: utf-8

# In[3]:


import scobra


# In[4]:


import pandas


# In[5]:


from scobra.cyc import BuildModel


# In[6]:


Ntara_to_be_modified = scobra.Model('C:/Users/Wayne/ntara_20190209.xlsx')


# In[7]:


soybean_ref = scobra.Model('C:/Users/Wayne/soybean.xls')


# In[8]:


Ntara_to_be_modified


# In[9]:


soybean_ref


# In[107]:


Soybean =pandas.read_excel('C:/Users/Wayne/soybean.xls', sheet_name = 'Reaction List', sep = '\t')


# In[108]:


Soybean


# In[109]:


Ntara_Reactions = pandas.read_excel('C:/Users/Wayne/ntara_20190209.xlsx', sheet_name = 'Reaction List', sep = '\t')


# In[114]:


Ntara_Metabolite = pandas.read_excel('C:/Users/Wayne/ntara_20190209.xlsx', sheet_name = 'Metabolite List', sep = '\t')


# In[110]:


Ntara_Reactions


# In[81]:


add_reactions = [

"ALANINE--TRNA-LIGASE-RXN_c",

"ARGININE--TRNA-LIGASE-RXN_c",

"ASPARAGINE--TRNA-LIGASE-RXN_c",

"ASPARTATE--TRNA-LIGASE-RXN_c",

"CYSTEINE--TRNA-LIGASE-RXN_c",

"DNA_Processing_c",

"FAD_reg_m",

"FAD_reg_x",

"GLUCISOM-RXN_c",

"GLUCOSE-6-PHOSPHATASE-RXN_c",

"GLUTAMINE--TRNA-LIGASE-RXN_c",

"GLYCINE--TRNA-LIGASE-RXN_c",

"HISTIDINE--TRNA-LIGASE-RXN_c",

"HYDROXYPYRUVATE-REDUCTASE-RXN-NADP_c",

"HYDROXYPYRUVATE-REDUCTASE-RXN-NADP_p",

"HYDROXYPYRUVATE-REDUCTASE-RXN-NAD_x",

"ISOCIT-CLEAV-RXN_x",

"ISOLEUCINE--TRNA-LIGASE-RXN_c",

"LEUCINE--TRNA-LIGASE-RXN_c",

"L-ASCORBATE-PEROXIDASE-RXN_c",

"L-ASCORBATE-PEROXIDASE-RXN_m",

"L-ASCORBATE-PEROXIDASE-RXN_p",

"L-ASCORBATE-PEROXIDASE-RXN_x",

"L-ASPARTATE_GLU_mc",

"LEUCINE--TRNA-LIGASE-RXN_c",

"LYSINE--TRNA-LIGASE-RXN_c",

"MALSYN-RXN_x",

"METHIONINE--TRNA-LIGASE-RXN_c",

"PHENYLALANINE--TRNA-LIGASE-RXN_c",

"PROLINE--TRNA-LIGASE-RXN_c",

"PROPIONYL-COA_mc",

"PROPIONYL-COA_xc",

"PROTON_mc",

"PROTON_pc",

"PROTON_tx",

"PROTON_vc",

"PROTON_xc",

"PRO_GLU_mc",

"Pi_tx",

"Protein_Processing_c",

"RNA_Processing_c",

"RXN-3523_c",

"RXN-3523_m",

"RXN-3523_p",

"RXN-3523_x",

"RXN490-3650_p",

"SEDOBISALDOL-RXN_p",

"SERINE--TRNA-LIGASE-RXN_c",

"SPONTPRO-RXN_c",

"SPONTPRO-RXN_m",

"SPONTPRO-RXN_p",

"THREONINE--TRNA-LIGASE-RXN_c",

"TIGLYLCOA-HYDROXY-RXN_m",

"TRYPTOPHAN--TRNA-LIGASE-RXN_c",

"TYROSINE--TRNA-LIGASE-RXN_c",

"UMPKI-RXN_c",

"UMPKI-RXN_p",
]


# In[82]:


len(add_reactions)


# In[47]:


## For each reaction in the reaclist, the function finds the relevant information from
## a reference model and returns a dictionary which has the form:
## Key: Reaction, Value: A dictionary which itself has key: Column Name and value: Relevant Information.
def find_reaction_information(reaclist, refmodelcsv, column_names):
    dictionary = {}
    for reac in reaclist:
        count = 0 
        name_dictionary = {}
        for cell in refmodelcsv["Abbreviation"]:
            if str(reac) == str(cell):
                for name in column_names:
                    name_dictionary[name] = str(refmodelcsv[name][count])
                    dictionary[reac] = name_dictionary
            else:
                count += 1
    return dictionary
    
                
        
        
    


# In[48]:


wanted_columns = ["Description", "Reaction", "Subsystem", "Reversible", "Lower bound", "Upper bound","Objective", "Confidence Score", "EC Number", "Notes", "References"]


# In[85]:


reac_info_dictionary = find_reaction_information(add_reactions, Soybean, wanted_columns)


# In[104]:


reac_info_dictionary


# In[111]:


## Adds the reaction as well as the information required for each of the columns of the model for the reaction into the csv.
def reac_info_adder(dictionary, csv):
    count = 0
    for cell in csv['Abbreviation']:
        if cell != 'nan':
            count += 1 
        else:
            count = count
    for reac in dictionary:
        csv.loc[count,"Abbreviation"] = reac
        for column_name in dictionary[reac]:
            csv.loc[count, column_name]= dictionary[reac][column_name]
        count += 1
    return csv


# In[112]:


Ntara_Reactions_Edited = reac_info_adder(reac_info_dictionary, Ntara_Reactions)


# In[113]:


Ntara_Reactions_Edited


# In[115]:


writer = pandas.ExcelWriter('Ntara_20190222.xlsx')
Ntara_Reactions_Edited.to_excel(writer,'Reaction List', index = False)
Ntara_Metabolite.to_excel(writer, 'Metabolite List', index = False)
writer.save()


# In[ ]:


## The below reactions check whether all the reactions to be added are properly added inside the model. 
## I subsequently realized that there was a duplicate reaction inside the 57 reactions, meaning that there is only 56 distinct
## reactions to be added.


# In[97]:


reaclist = []
for reac in add_reactions:
    if reac in reac_info_dictionary:
        reaclist.append(reac)
len(reaclist)


# In[99]:


reaclist = []
for reac in add_reactions:
    if reac not in reaclist:
        reaclist.append(reac)
    else:
        print reac
len(reaclist)


# In[87]:


len(reac_info_dictionary)


# In[ ]:


## If running this model using scobra.Model doesn't work properly, with the error being related to 'cannot assign objective to
## a missing model, just open the excel file of the model and delete all the entries in the 'objective' column. That should 
## work properly.

