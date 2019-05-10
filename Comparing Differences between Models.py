
# coding: utf-8

# In[3]:


import scobra


# In[4]:


import pandas


# In[5]:


from scobra.cyc import BuildModel


# In[29]:


def Compare_Model_Reactions(modelpathname, refmodelpathname):
## Returns a list of reactions that are found in the reference model but not in the target model.
    csv = pandas.read_excel(modelpathname, sheet_name = 'Reaction List', sep = '\t')
    refcsv = pandas.read_excel(refmodelpathname, sheet_name = 'Reaction List', sep = '\t')
    reactionlist = []
    refreactionlist = []
    for reac in csv['Abbreviation']:
        reactionlist.append(str(reac))
    for reac in refcsv['Abbreviation']:
        refreactionlist.append(str(reac))
    print 'Model has ' + str(len(reactionlist)) + ' reactions.'
    print 'Reference Model has ' + str(len(refreactionlist)) + ' reactions.'
    difference = []
    for reac in refreactionlist:
        if reac not in reactionlist:
            difference.append(str(reac))
    return difference


# In[17]:


soyvssperg = Compare_Model_Reactions('C:/Users/Wayne/SpergulariaTransportersModelFixedTESTV4.xlsx', 'C:/Users/Wayne/Desktop/Yale NUS stuff/Computational Biology/Files/soybean.xls')


# In[18]:


soyvssperg


# In[19]:


len(soyvssperg)


# In[20]:


arabidopsisvssperg = Compare_Model_Reactions('C:/Users/Wayne/SpergulariaTransportersModelFixedTESTV4.xlsx', 'C:/Users/Wayne/Desktop/Yale NUS stuff/Computational Biology/Files/C3single_v14.xls')


# In[21]:


arabidopsisvssperg 


# In[22]:


len(arabidopsisvssperg )


# In[23]:


soyvsntara = Compare_Model_Reactions('C:/Users/Wayne/NtaraUnbalancedTransportersModelFixedTESTV4.xlsx', 'C:/Users/Wayne/Desktop/Yale NUS stuff/Computational Biology/Files/soybean.xls')


# In[24]:


soyvsntara


# In[28]:


len(soyvsntara)


# In[25]:


arabidopsisvsntara = Compare_Model_Reactions('C:/Users/Wayne/NtaraUnbalancedTransportersModelFixedTESTV4.xlsx', 'C:/Users/Wayne/Desktop/Yale NUS stuff/Computational Biology/Files/C3single_v14.xls')


# In[26]:


arabidopsisvsntara


# In[27]:


len(arabidopsisvsntara)


# In[ ]:


writer = pandas.ExcelWriter('Differences V3.xlsx')
df1 = pandas.DataFrame({'Reactions':soyvssperg})
df2 = pandas.DataFrame({'Reactions' : arabidopsisvssperg})
df3 = pandas.DataFrame({"Reactions": soyvsntara})
df4 = pandas.DataFrame({"Reactions" : arabidopsisvsntara})
df1.to_excel(writer, "Soybean vs Spergularia")
df2.to_excel(writer,"Arabidopsis vs Spergularia")
df3.to_excel(writer, "Soybean vs Ntara")
df4.to_excel(writer, "Arabidopsis vs Ntara")
writer.save()

