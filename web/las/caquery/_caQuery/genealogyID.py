class GenealogyID ():
    def __init__ (self,genID=''):
        if len (genID) < 26:
            genID = genID + (26-len(genID))*'-'
        elif len (genID) > 26:
            genID = '--------------------------'
        
        self._genID = genID
        self._originalDict = {'CRC':'colorectal', 'BRC':'breast', 'MEL':'melanoma', 'LNG':'lung', 'OVR':'ovarian', 'GTR':'gastric', 'EPC':'exocrine pancreatic cancer', 'KDC':'Kidney cancer', 'LNF':'Lymphoma', 'THC':'Thyroid cancer', 'CHC':'CHolangioCarcinoma', 'CRL':'ColoRectal cell Line', 'LNL':'Lung cell Line', 'BRL':'Breast cell Line', 'NEC':'NeuroEndocrine cancer', 'HNC':'Head&Neck carcinoma', 'HCC':'HepatoCellular Carcinoma'}
        self._tissueDict = {'PR':'primary tumor', 'LM':'liver met', 'CM':'cutaneous met', 'PM':'peritoneal met', 'TM':'lung met (thoracic met)', 'BM':'brain met', 'SM':'bone met (skeletal met)', 'TR':'thoracentesis', 'TH':'thymus met', 'LY':'lynphonode Met', 'AM':'adrenal metastasis', 'NL':'normal liver', 'NB':'normal brain', 'NN':'normal lynphonode (normale node)', 'NM':'normal mucosa', 'NC':'normal cutis', 'BL':'blood'}
        self._vectorSampleDict = {'H':'Human', 'X':'Xenos', 'S':'Spheres', 'A':'adherent lines'}
        self._tissueTypeDict = {'TUM':'tumor', 'LNG':'lung', 'LIV':'liver', 'GUT':'gut', 'BLD':'blood', 'MLI':'liver mets', 'MBR':'brain mets', 'MLN':'lung mets'}
        self._implantSiteDict = {'SCR': 'Sub cutis Right', 'SCL': 'Sub cutis Left', 'FPR': 'Fat pad Right', 'FPL': 'Fat pad Left', 'CEC': 'Cecum', 'LVR': 'Liver', 'PRT': 'Peritoneoum', 'BRN': 'Brain', 'LNG': 'Lung'}
        self._archivedMaterial = {'000': 'null', 'VT':'Viable', 'SF':'Snap Frozen', 'RL':'RNAlater', 'PL':'Plasma isolation', 'FF':'Formalin Fixed', 'OF':'OCT frozen', 'PS':'Paraffin section', 'OS':'OCT section', 'SI':'serum isolation', 'CH':'ChinaBlack', 'R':'RNA', 'D':'DNA', 'P':'Protein','PX':'PAXtube','FR':'Frozen','FS':'FrozenSediment'}
        # tuple with start index and lenght of the code
        self._indexes= {'origin':(0,3), 'caseCode':(3,4), 'tissue':(7,2), 'sampleVector':(9,1), 'lineage':(10,2), 'samplePassage':(12,2), 'mouse':(14,3), 'tissueType':(17,3), 'implantSite':(17,3), 'archiveMaterial1': (20,1), 'archiveMaterial2': (20,2), 'aliqExtraction1':(21,2), 'aliqExtraction2':(22,2), '2derivation': (23,1), '2derivationGen':(24,2)}
        self._materialLen = self._setArchivedMaterial()

    # clear all fields following <field> by setting them to '--'
    def clearFieldsAfter(self, field):
        try:
            self._genID = self._genID[:self._indexes[field][0]+self._indexes[field][1]] + (26-self._indexes[field][0]-self._indexes[field][1])*'-'
            return self
        except:
            raise KeyError
            
    # zero out all fields following <field> by setting them to 0
    def zeroOutFieldsAfter(self, field):
        try:
            self._genID = self._genID[:self._indexes[field][0]+self._indexes[field][1]] + (26-self._indexes[field][0]-self._indexes[field][1])*'0'
            return self
        except:
            raise KeyError
      
    # set the origin
    def setOrigin(self, o):
        if o in self._originalDict.keys():
            self._genID = o + self._genID[self._indexes['origin'][0]+self._indexes['origin'][1]:]
        return self

    # set the being type of the aliquot (e.g., human, xeno)
    def setSampleVector(self, v):
        if v in self._vectorSampleDict.keys():
            self._genID = self._genID[:self._indexes['sampleVector'][0]] + v + self._genID[self._indexes['sampleVector'][0]+self._indexes['sampleVector'][1]:]
        return self

    # set the passage of the lineage
    def setSamplePassage(self, p):
        self._genID = self._genID[:self._indexes['samplePassage'][0]] + "%02d" % p + self._genID[self._indexes['samplePassage'][0]+self._indexes['samplePassage'][1]:]
        return self

    # set the mouse number in the current lineage+passage
    def setMouse(self, n):
        self._genID = self._genID[:self._indexes['mouse'][0]] + "%03d" % n + self._genID[self._indexes['mouse'][0]+self._indexes['mouse'][1]:]
        return self
    
    # set the tissue type of the aliquot (e.g., TUM, LNG)
    def setTissueType(self, t):
        if t in self._tissueTypeDict.keys():
            self._genID = self._genID[:self._indexes['tissueType'][0]] + t + self._genID[self._indexes['tissueType'][0]+self._indexes['tissueType'][1]:]
        return self

    # set the mouse implant site (e.g., SCR, SCL)
    def setImplantSite(self, t):
        if t in self._implantSiteDict.keys():
            self._genID = self._genID[:self._indexes['implantSite'][0]] + t + self._genID[self._indexes['implantSite'][0]+self._indexes['implantSite'][1]:]
        return self

    # set the type of the archived material (e.g., 00 for human, VT, SF)
    # use clearFieldsAfter('tissueType') before calling this
    def setArchivedMaterial(self, m):
        if m in self._archivedMaterial.keys():
            self._materialLen = len(m)-1
            if self._materialLen:
                self._genID = self._genID[:self._indexes['archiveMaterial2'][0]] + m + self._genID[self._indexes['archiveMaterial2'][0]+self._indexes['archiveMaterial2'][1]:]
            else:
                self._genID = self._genID[:self._indexes['archiveMaterial1'][0]] + m + self._genID[self._indexes['archiveMaterial1'][0]+self._indexes['archiveMaterial1'][1]:]
        return self
    
    # set the number of the aliquot extraction
    def setAliquotExtraction (self, n):
        if self._materialLen:
            self._genID = self._genID[:self._indexes['aliqExtraction2'][0]] + "%02d" % n + self._genID[self._indexes['aliqExtraction2'][0]+self._indexes['aliqExtraction2'][1]:]
        else:
            self._genID = self._genID[:self._indexes['aliqExtraction1'][0]] + "%02d" % n + self._genID[self._indexes['aliqExtraction1'][0]+self._indexes['aliqExtraction1'][1]:]
        return self

    # tell if genealogy id represents a xenopatient
    def isMouse(self):
        if self.getSampleVector() == 'X' and self._genID[self._indexes['implantSite'][0]+self._indexes['implantSite'][1]:] == (26-self._indexes['implantSite'][0]-self._indexes['implantSite'][1])*'0':
            return True
        else:
            return False
        
    # tell if genealogy id represents an aliquot
    def isAliquot(self):
        if self._genID[self._indexes['implantSite'][0]+self._indexes['implantSite'][1]:] != (26-self._indexes['implantSite'][0]-self._indexes['implantSite'][1])*'0':
            return True
        else:
            return False
            
    # tell if genealogy id represents a 2nd-level derivative aliquot
    def is2Derivation(self):
        if self.get2Derivation() in ['R', 'D']:
            return True
        else:
            return False

    # get Origin of the tumor (e.g., CRC, BRC)
    def getOrigin(self):
        return self._genID[self._indexes['origin'][0]:self._indexes['origin'][0]+self._indexes['origin'][1]]

    # get the code of the case related to the origin
    def getCaseCode(self):
        return self._genID[self._indexes['caseCode'][0]:self._indexes['caseCode'][0]+self._indexes['caseCode'][1]]

    # concatenate the origin and the case code (e.g., CRC0001)
    def getCase(self):
        return self.getOrigin() + self.getCaseCode()

    # get the tissue of the origin
    def getTissue(self):
        return self._genID[self._indexes['tissue'][0]:self._indexes['tissue'][0]+self._indexes['tissue'][1]]

    # get the being type of the aliquot (e.g., human, xeno)
    def getSampleVector(self):
        return self._genID[self._indexes['sampleVector'][0]:self._indexes['sampleVector'][0]+self._indexes['sampleVector'][1]]

    # get the lineage (e.g., 0A, 0B)
    def getLineage(self):
        return self._genID[self._indexes['lineage'][0]:self._indexes['lineage'][0]+self._indexes['lineage'][1]]

    # get the passage of the lineage
    def getSamplePassage(self):
        return self._genID[self._indexes['samplePassage'][0]:self._indexes['samplePassage'][0]+self._indexes['samplePassage'][1]]

    # get the mouse in the lineage+passage
    def getMouse(self):
        return self._genID[self._indexes['mouse'][0]:self._indexes['mouse'][0]+self._indexes['mouse'][1]]

    # concatenate the being, the lineage and the passage
    def getGeneration(self):
        return self.getSampleVector() + self.getLineage() + self.getSamplePassage()

    # get the tissue type of the aliquot (e.g., TUM, LNG)
    def getTissueType(self):
        return self._genID[self._indexes['tissueType'][0]:self._indexes['tissueType'][0]+self._indexes['tissueType'][1]]

    # get the mouse implant site (e.g., SCR, SCL)
    def getImplantSite(self):
        return self._genID[self._indexes['implantSite'][0]:self._indexes['implantSite'][0]+self._indexes['implantSite'][1]]

    # get the type of the archived material (e.g., 00 for human, VT, SF)
    def getArchivedMaterial(self):
        if self._materialLen:
            return self._genID[self._indexes['archiveMaterial2'][0]:self._indexes['archiveMaterial2'][0]+self._indexes['archiveMaterial2'][1]]
        else:
            return self._genID[self._indexes['archiveMaterial1'][0]:self._indexes['archiveMaterial1'][0]+self._indexes['archiveMaterial1'][1]]

    # get the number of the aliquot extraction
    def getAliquotExtraction (self):
        if self._materialLen:
            return self._genID[self._indexes['aliqExtraction2'][0]:self._indexes['aliqExtraction2'][0]+self._indexes['aliqExtraction2'][1]]
        else:
            return self._genID[self._indexes['aliqExtraction1'][0]:self._indexes['aliqExtraction1'][0]+self._indexes['aliqExtraction1'][1]]

    # get the information about the 2nd derivation process (if available)
    def get2Derivation(self):
        if self.getArchivedMaterial() == 'R':
            return self._genID[self._indexes['2derivation'][0]:self._indexes['2derivation'][0]+self._indexes['2derivation'][1]]
        else:
            return None

    # get the number of 2nd derivation processes (if available)
    def get2DerivationGen(self):
        return self._genID[self._indexes['2derivationGen'][0]:self._indexes['2derivationGen'][0]+self._indexes['2derivationGen'][1]]

    # return the genealogyID
    def getGenID(self):
        return self._genID#, len(self._genID)
   
    #ritorna tutti i caratteri fino al tessuto tumorale impiantato nel topo
    def getPartForDerAliq(self):
        return self.getCase()+self.getTissue()+self.getGeneration()+self.getMouse()+self.getTissueType()
   
    #ritorna tutti i caratteri fino alla prima derivazione
    def getPartFor2DerivationAliq(self):
        return self.getCase()+self.getTissue()+self.getGeneration()+self.getMouse()+self.getTissueType()+self.getArchivedMaterial()+self.getAliquotExtraction()

    #ritorna la lunghezza dello spazio riservato alla seconda derivazione
    def getLen2Derivation(self):
        return int(self._indexes['2derivation'][1])+int(self._indexes['2derivationGen'][1])

    # (private function) evaluate the type of archived material based on the structure of the genealogyID
    def _setArchivedMaterial (self):
        if self._archivedMaterial.has_key(self._genID[self._indexes['archiveMaterial2'][0]:self._indexes['archiveMaterial2'][0]+self._indexes['archiveMaterial2'][1]]):
            return self._indexes['archiveMaterial2'][1]-1
        else:
            return self._indexes['archiveMaterial1'][1]-1

    #update genealogyID according to the data dictionary
    def updateGenID (self, data):
        tempGenID = self._genID
        for k, v in data.items():
            if self._indexes.has_key (k):
                if len(v) == self._indexes[k][1]:
                    tempGenID = tempGenID[:self._indexes[k][0]] + v + tempGenID[self._indexes[k][0]+self._indexes[k][1]:]
                else:
                    return
        self._genID = tempGenID
        return

    #compare parts of Genealogy IDs		
    def compareGenIDs(self, other):
        atypevoid=""
        if self._materialLen:
            atypevoid="--"
        else:
            atypevoid="-"
       
        if((self.getOrigin()=="---" or other.getOrigin()==self.getOrigin())and(self.getCaseCode()=="----" or self.getCaseCode()==other.getCaseCode())and(self.getTissue()=="--" or self.getTissue()==other.getTissue())and(self.getSampleVector()=="-" or self.getSampleVector()==other.getSampleVector())and(self.getLineage()=="--" or other.getLineage()==self.getLineage())and(self.getSamplePassage()=="--" or self.getSamplePassage()==other.getSamplePassage())and(self.getMouse()=="---" or self.getMouse()==other.getMouse())and(self.getTissueType()=="---" or self.getTissueType()==other.getTissueType())and(self.getArchivedMaterial()==atypevoid or self.getArchivedMaterial()==other.getArchivedMaterial())and(self.getAliquotExtraction()=="--" or self.getAliquotExtraction()==other.getAliquotExtraction())and(self.get2Derivation()=="-" or self.get2Derivation()==other.get2Derivation())and(self.get2DerivationGen()=="--" or self.get2DerivationGen()==other.get2DerivationGen())):
            return True
        else:
            return False
                    
def main():
    g = GenealogyID('CRC0176LMX0A06013TUMR01000')
    #g = GenealogyID('')
    print g.getGenID()
    print g.getOrigin()
    print g.getCase()
    print g.getTissue()
    print g.getSampleVector()
    print g.getLineage()
    print g.getSamplePassage()
    print g.getMouse()
    print g.getGeneration()
    print g.getTissueType()
    print g.getArchivedMaterial()
    print g.getAliquotExtraction()
    print g.get2Derivation()
    print g.get2DerivationGen()
    print g.updateGenID({'2derivation':'D','2derivationGen':'04'})
    print g.getGenID()
    #print g._setArchivedMaterial()
    print g.getPartForDerAliq()
    print g.getPartFor2DerivationAliq()
       

if __name__=='__main__':
        main()
