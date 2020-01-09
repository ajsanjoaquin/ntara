import os, sys, inspect
import pandas
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
gparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, gparentdir)
import copy
import scobra
import pandas
from scobra.classes import model
from scobra.cyc import BuildModel


def returnCountFront(x):
## Module used in ReactionParserExcel function. 
      count = 0
      for a in x[0:]:
         if a == "," :
            return count
         else:
            count += 1
      return count
	  
def ReactionParserExcel(x,reaclist):
## Parsers through a list of reactions (which includes commmas, spaces) where the list also contains several reactions as a single entry,
## and returns a list of reactions in a proper format (where an entry in the list only consists of 1 reaction)
	while len(str(x)) > 3:
		y = x[0:returnCountFront(x)]
		if int(returnCountFront(x)) != len(x):
			reaclist.append(y)
			return ReactionParserExcel(x[returnCountFront(x) + 2:], reaclist)
		else:
			reaclist.append(x)
			break 

def removerepetition(x):
## Removes repetitions present in the list
   list = []
   for string in x:
        if string not in list:
            list.append(string)
   return list
 
def GeneFinderFinal(userlist, csv):
## Returns to the user a dictionary, with the key being a Reaction, and its value being a list of Genes that is related to the Reaction in the GENE RXN PWY file.
    dictionary = {}
    for reac in userlist:
        genelist = []
        count = 0
        for cell in csv["Reactions"][0:]:
           if cell == 0:
              count += 1
           elif cell != 0:
              if str(reac) in cell:
                 gene = csv["ID"][count]
                 genelist.append(gene)
                 count += 1
              else: 
                 count += 1
                 
        
        dictionary[reac] = genelist
        
    return dictionary

def eraser(csv, columnname):
## Converts all values in the file to None Type
    count = 0
    for cell in csv[columnname][0:]:
        csv.loc[count, columnname] = ''
        count += 1

def GPRfillerupdated(dictionary, csv):
## For every reaction in the CSV, the function fills its 'GPR' and 'Genes' columns with the reaction's related genes in the appropriate format
    for reac in dictionary:
        count = 0
        for cell in csv["Abbreviation"][0:]:
            if str(reac) == csv["Abbreviation"][count]:
                csv.loc[count, 'GPR'] = str(dictionary[reac][0])
                csv.loc[count, 'Genes'] = str(dictionary[reac][0])
                for i in range(1, int(dictionaryvaluelength(dictionary,reac))):
                   csv.loc[count, 'GPR'] += " or " + str(dictionary[reac][i])
                   csv.loc[count, 'Genes'] += ' ' + str(dictionary[reac][i])
                break
            else:
                count += 1
    return csv

def dictionaryvaluelength(dictionary, reac):
   number = 0   
   for value in dictionary[reac]:
      number += 1
   return number

def MetaboliteReturner(csv):
## The function returns a list of metabolites that either does not have a Neutral Formula or Charged Formula 
    MetaboliteList = []
    count = 0
    for cell in csv["Abbreviation"]:
        if csv["Neutral formula"][count]== '' or csv["Charged formula"][count] == '':
            MetaboliteList.append(str(cell))
            count += 1
        else:
            count += 1
    return MetaboliteList

def MetaboliteInfoReturner(userlist, csv):
## The function searches for information (charge, formula etc) of the metabolites from MetaboliteReturner from already available csv files. The function first finds 
## whether the said metabolites exist in the reference csv file, before creating a dictionary that contains the metabolite's netural formula, charged formula, and charge
## in that exact order.
    dictionary = {}
    for metabolite in userlist:
        infolist = []
        count = 0 
        for cell in csv["Abbreviation"][0:]:
            if str(metabolite) not in cell:
                count += 1
            elif str(metabolite) == str(cell)[:-2]:
               if csv["Neutral formula"][count] != 0 and csv["Charged formula"][count] != 0:
                  infolist.append(str(csv["Neutral formula"][count]))
                  infolist.append(str(csv["Charged formula"][count]))
                  infolist.append(int(csv["Charge"][count]))
                  break
               else:
                  infolist.append("Not Enough Information")
                  break
        if infolist != []:
           dictionary[str(metabolite)] = infolist
        else:
           dictionary[str(metabolite)] = "No Information"
    return dictionary
	
def ExcelMetaboliteInfoFiller(dictionary, csv):
## This function then fills up the information in the original csv for the metabolites (those that the function MetaboliteInfoReturner can find info for) 
    for entry in dictionary:
        count = 0
        if dictionary[entry] != 'No Information' and dictionary[entry] != ['Not Enough Information']:
           for cell in csv["Abbreviation"][0:]:
              if entry == str(cell): 
                 csv.loc[count, 'Neutral formula'] = dictionary[entry][0]
                 csv.loc[count, 'Charged formula'] = dictionary[entry][1]
                 csv.loc[count, 'Charge'] = dictionary[entry][2]
                 break
              else:
                 count += 1
    return csv

def CompartmentModel(m, compartments):
   """ compartments = {"default":"cpt", "compartments":{"cpt":[]}, "suffix":{"cpt":"suffix"}} """
   default_cpm = compartments["default"]
   if not compartments["compartments"].has_key(default_cpm):
      compartments["compartments"][default_cpm] = []
   if not compartments.has_key('suffix'):
      cpms = compartments["compartments"].keys()
      compartments["suffix"] = dict(zip(cpms, cpms))
   reacs_not_default_cpm = []
   for cpm in compartments["compartments"]:
      if cpm != default_cpm:
         for reac in compartments["compartments"][cpm]:
            if reac not in compartments["compartments"][default_cpm]:
               reacs_not_default_cpm.append(reac)
   for reac in m.Reactions():
      if reac not in reacs_not_default_cpm:
         if reac not in compartments["compartments"][default_cpm]:
            compartments["compartments"][default_cpm].append(reac)
   compartmented_model = model.model()
   for cpm in compartments["compartments"]:
      cpm_suffix = compartments["suffix"][cpm]
      for reac in compartments["compartments"][cpm]:
         cpm_reac = m.GetReaction(reac).copy()
         cpm_reac.id = reac + cpm_suffix
         compartmented_model.add_reaction(cpm_reac)
         for met in list(cpm_reac.metabolites):
            SubMetabolites(compartmented_model, {met: str(met)+cpm_suffix}, cpm_reac)
   return compartmented_model
  
def SubMetabolites(m, subdic, reac):
    """ substitute metabolites; subdic = {"old_met":"new_met"} """
    for submet in subdic.keys():
        newmet = subdic[submet]
        if newmet in m.Metabolites():
            newmet = m.GetMetabolite(newmet)
        else:
            newmet = m.GetMetabolite(submet).copy()
            newmet.id = subdic[submet]
        for reac in m.InvolvedWith(submet):
           m.ChangeReactionStoichiometry(reac, {newmet:m.InvolvedWith(submet)[reac], submet:0})
        m.DelMetabolite(submet)
    m.repair()

class Imbalancedreac:
    '''must call class with variable assigned to scobra.model.ImbalanceReactions(model)'''
    def __init__(self,scobramodel,refdir):
        self.scobramodel=scobramodel
        self.refdir=refdir

    def list_imbalances(self):
       ''' (scobra.model)->list
       Creates a list of imbalanced reactions that contain no repetition
       '''
       ImbalanceReacList = []
       for reac in self.scobramodel:
            if reac not in ImbalanceReacList:
                ImbalanceReacList.append(reac)
       return ImbalanceReacList
	
    def reference(self, ImbalanceReacList):
        '''(csv,list)->dict
    [Opposite of OriginalReactionInfo]

        For imbalanced reactions in the model 
    (contained in the ImbalanceReacList), the function 
    refers to reference csv and creates a dictionary
    { imbalanced reaction: reaction stoichiometry from the reference csv} 
        '''
        ref = pandas.read_excel(self.refdir, sheet_name = 0, sep = '\t')
        dictionary = {}
        for reac in ImbalanceReacList:
            index = 0
            for rxn in ref["Abbreviation"]:
                if reac == rxn:
                    ReactionInfo = ref.loc[index, 'Reaction'] 
                    dictionary[str(reac)] = str(ReactionInfo)
                    break
                else:
                    index += 1
        return dictionary

    def fiximbalance (self, dictionary):
        ''' (dict,csv)->dict
        The function substitutes the reaction stoichiometries of 
        the imbalanced reactions in the model with those found in 
        the reference csv as done so by the function ReferenceReactionInfo
        '''
        ref = pandas.read_excel(self.refdir, sheet_name = 'Reaction List', sep = '\t')
        for reac in dictionary:
            count = 0 
            for rxn in ref["Abbreviation"]:
                if str(reac) == str(rxn):
                    ref.loc[count, 'Reaction'] = dictionary[reac]
                    #you equate the cells in column Reaction to the value of dictionary with key reac at that point
                    #but why substitute when they are already the same? (because dictionary[reac] was already taken from soybean
                    # in the first place through FCN referencereactioninfo)
                    break
                else:
                    count += 1
        return ref


def RemoveUnwantedReactionsDictionary(dictionary, reactionlist):
    ## The function removes reactions that do not exist in the model from the Compartment Model dictionary 
        copydictionary = copy.deepcopy(dictionary)
        for cpms in copydictionary['compartments']:
          for entry in copydictionary['compartments'][cpms]:
            print "Compartment = " + str(cpms)
            print "Entry = " + str(entry)
            if entry not in reactionlist:
                    print "Deleting Entry = " + str(entry)
                    copydictionary['compartments'][cpms].remove(entry)
        return copydictionary
    


def GetFromReference (refmodelpathname, referencedlist,targetlist):
   '''
    (path to model csv,path to referenced list(ReferenceReactionInfo), path to targetlist)
    -> (dict)
    get reactions and their stoic from refmodel, 
    store as dataframe, and update the current file (by adding the reactions to current file)
   '''
   reflist=pandas.read_excel(referencedlist,sheet_name='Sheet1',sep='\t')
   target=pandas.read_excel(targetlist,sheet_name='Reaction List',sep='\t')
   model = pandas.read_excel(refmodelpathname, sheet_name = 'Reaction List', sep = '\t')
   refrow= (model["Abbreviation"].isin(reflist['R']))
   df_revised=(model[refrow].loc[:,['Abbreviation', 'Reaction']].copy())
   target=target.append(df_revised)
   return target
      #FIX with proper indices

#update^^
def MakeListFromDic(dictionary):
    reaclist = []
    for entry in dictionary:
        for content in dictionary[entry]:
            reaclist.append(content)
    return reaclist

class Test:
    def __init__(self,refdir,name):
        self.refdir=refdir
        self.name=name
        self.model=scobra.Model(refdir)

    def sortcpm(self, endsuffixlist):
    ## Sorts reactions in the model according to the end suffixes present in the endsuffixlist. Returns a dictionary in the following format:
    ## {end suffix: list of reactions containing this end suffix}
        csv = pandas.read_excel(self.refdir, sheet_name = 'Reaction List', sep = '\t')
        dictionary = {}
        for endsuffix in endsuffixlist:
            print "End Suffix = " + str(endsuffix)
            reactionlist = []
            for entry in csv['Abbreviation']:
                print "Entry = " + str(entry)
                compartment = str(entry)[-len(endsuffix) :]
                print 'Compartment = '  + str(compartment)
                if compartment == endsuffix:
                    reactionlist.append(str(entry))
            dictionary[endsuffix] = reactionlist
        return dictionary
	
    def test_model(self, CPMdict):
        '''
        CPMdict refers to CPMdictionary result
        model refers to variable initialized by scobra.Model (remember to chang constraints in source code if not using NTARA)

        Tests model according to the following (modifiable) parameters:
        The function sets the fluxes of all _tx reactions to 0, then sets the constraints of certain _tx reactions to certain constraints. Objective is to 
        minimize GLC_tx consumption. 
        Then, the function tests the model, and forces the production of each biomass for each loop. (setting it to -1,-1) Writes out solution fluxes and biomasses produced
        '''
        

        TXdictionary = {}
        for tx_rxn in CPMdict['_tx']:
            TXdictionary[tx_rxn] = (0,0) ## sets the constraint for all TX reactions to be 0
        self.model.SetConstraints(TXdictionary)
        BiomassDictionary = {}
        for biomass in CPMdict['_biomass']:
            BiomassDictionary[biomass] = (0,0) 
        self.model.SetConstraints(BiomassDictionary) ## sets the constraint for all Biomass reactions to be 0
        ## Sets the constraints for the TX reactions GLC_tx, CO2_tx, O2_tx, H2O_tx, H_tx, NO3_tx, SO4_tx
        self.model.SetConstraints({'GLC_tx':(0, 1000), 'CO2_tx': (-1000, 1000), 'PROTON_tx': (-1000,1000),'O2_tx': (-1000,1000), 'H2O_tx':(-1000,1000), 'NO3_tx': (-1000,1000), 'SO4_tx': (-1000, 1000),'Pi_tx':(-1000,1000)}) #H_tx changed to PROTON_tx; added Pi_tx
        self.model.SetObjective('GLC_tx')
        self.model.SetObjDirec('Min')
        optimallist = []
        name = self.name + ' Solution Fluxes'+ '.xlsx'
        writer = pandas.ExcelWriter(name)
        ## Sets the constraint for each biomass to be -1, and tests whether the production of said biomass is possible. 
        for biomass in CPMdict['_biomass']:
            self.model.SetConstraint(biomass, -1, -1)
            self.model.Solve()
            self.model.GetStatusMsg()
            if self.model.GetStatusMsg() == 'optimal':
                optimallist.append(biomass)
            if self.model.solution != None:
                Sol = self.model.solution.fluxes
                df = Sol.to_frame()
                df.to_excel(writer, biomass)
            self.model.SetConstraint(biomass, 0, 0)
        writer.save()
        biomass_dictionary = {}
        biomass_dictionary['Optimal'] = optimallist 
        nonoptimallist = []
        for reac in CPMdict['_biomass']:
            if reac not in optimallist:
                nonoptimallist.append(reac)
        biomass_dictionary['No solution'] = nonoptimallist
        df2=pandas.DataFrame(dict([(k,pandas.Series(v))for k,v in biomass_dictionary.iteritems()]))
        df2.to_excel(self.name+ ' Biomass Production.xlsx')
        print optimallist ## Prints out the biomasses which are able to be produced.
        return biomass_dictionary

    def atp_model(self,CPMdict):
        '''This function takes in the dictionary containing Compartment names as keys and the reactions as values, with the dictionary
        being the one generated by SortReactionCpmDictionary; the model itself; and the name of the model as a string.

        The function prints whether it is possible for the model to generate ATPase, and also generates an excel sheet which will
        contain the solution fluxes if the model can generate ATPase. Otherwise, the excel sheet will be a blank sheet.
        '''
        
        TXdictionary = {}
        for tx_rxn in CPMdict['_tx']:
            TXdictionary[tx_rxn] = (0,0)
        self.model.SetConstraints(TXdictionary)
        BiomassDictionary = {}
        for biomass in CPMdict['_biomass']:
            BiomassDictionary[biomass] = (0,0)
        self.model.SetConstraints(BiomassDictionary)
        self.model.SetObjective('ATPase_tx')
        self.model.SetObjDirec('Min')
        self.model.SetConstraints({'ATPase_tx':(-1000,0),'GLC_tx':(1,1),'CO2_tx': (-1000, 1000), 'O2_tx': (-1000,1000), 'H_tx': (-1000,1000), 'H2O_tx':(-1000,1000)})
        print self.model.GetConstraints(['ATPase_tx','GLC_tx','CO2_tx', 'O2_tx', 'H2O_tx', 'H_tx'])
        #print model.GetState()
        name = self.name + ' Solution Fluxes'+ '.xlsx'
        print name
        writer = pandas.ExcelWriter(name)
        self.model.Solve()
        self.model.GetStatusMsg()
        if self.model.solution != None:
            Sol = self.model.solution.fluxes
            df = Sol.to_frame()
            df.to_excel(writer, 'ATPase_tx')
        writer.save()


        

def MergeWith(model, other_model, replace_with_new=False):
   """ keep attributes of current model if there is repetition in IDs  """
   for reac in other_model.reactions:
      if reac.id not in model.Reactions():
                model.add_reaction(reac)
      else:
         if replace_with_new:
            model.DelReaction(reac.id)
            model.add_reaction(reac)  
   return model
   
def ModelFixerforMetabolite(refmodelcsvpathname, metabolitelist, modelcsvpathname, modelname, Metabolite_Sheet):
## This function replaces the reaction stoichiometries of certain metabolites of the model (as found in the metabolitelist)
## with the ones found inside the reference model instead. The new reaction stoichiometry is printed in the console, 
## alongside the reaction name, and the reactions substituted are returned in the form of a list
    refcsv = pandas.read_excel(refmodelcsvpathname, sheet_name = 'Reaction List', sep = '\t')
    csv = pandas.read_excel(modelcsvpathname, sheet_name = 'Reaction List', sep = '\t')
    reacinfo = {}
    for metabolite in metabolitelist:
        print 'Metabolite = ' + str(metabolite)
        count = 0
        for entry in refcsv['Reaction']:
            if str(metabolite) in entry:
               reactioninfo = refcsv['Reaction'][count]
               print 'Reaction Info = ' + str(reactioninfo)
               reaction = refcsv['Abbreviation'][count]
               print 'Reaction that Metabolite is in = ' + str(reaction)
               reacinfo[str(reaction)] = str(reactioninfo)
               count += 1
            else:
                count += 1
    reaclist = []
    for reaction in reacinfo:
        count = 0
        for entry in csv['Abbreviation']:
            if str(reaction) == str(entry):
                print 'Equivalent Reaction = ' + str(reaction) +' found, substitution of reaction stoichiometry in progress...'
                csv.loc[count, 'Reaction'] = reacinfo[reaction]
                reaclist.append(str(reaction))
            else:
                count += 1
    name = modelname + '.xlsx'
    writer = pandas.ExcelWriter(name)
    csv.to_excel(writer, 'Reaction List', index = False)
    Metabolite_Sheet.to_excel(writer,'Metabolite List', index = False)
    Unsubstituted_Pumped_Proton_Reactions = []
    for reaction in reacinfo:
		if reaction not in reaclist:
			Unsubstituted_Pumped_Proton_Reactions.append(reaction)
    print reacinfo
    print Unsubstituted_Pumped_Proton_Reactions
    return reaclist

def ModifiedReactions(modifiedmodelcsvpathname, modelcsvpathname, reaclist):
## Returns a list of reactions in the model that have modified reaction stoichiometries in comparison with its earlier version
    modifiedcsv = pandas.read_excel(modifiedmodelcsvpathname, sheet_name = 'Reaction List', sep = '\t')
    csv = pandas.read_excel(modelcsvpathname, sheet_name = 'Reaction List', sep = '\t')
    modifiedreac = []
    for reac in reaclist:
        count = 0
        for entry in csv['Abbreviation']:
            if str(entry) == str(reac):
                csvinfo = str(csv['Reaction'][count])
                print reac
                print "Original Reaction Info = " + csvinfo
                for modentry in modifiedcsv['Abbreviation']:
                    if str(modentry) == str(reac):
                        print 'Modified Entry = ' + str(modentry)
                        modcsvinfo =  str(modifiedcsv['Reaction'][count])
                        print 'New Reaction Info = ' + modcsvinfo
                        if csvinfo != modcsvinfo:
                            print 'Modification present!'
                            modifiedreac.append(str(reac))
                        break
                        
            else:
                count += 1
    return modifiedreac	
	
def StoiDicMaker(reactionlist, model):
## Creates a Stoichiometric Dictionary for reactions in the reaction list as according to the stoichiometric ratios present in the model. 
    reacdic = {}
    for reac in reactionlist:
        stoidic = {}
        InvolvedWithDic = model.InvolvedWith(reac)
        for entry in InvolvedWithDic:
            stoidic[(str(entry))] = model.InvolvedWith(reac)[entry]
        reacdic[reac] = stoidic
    return reacdic	

