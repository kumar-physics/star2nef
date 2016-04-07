

import sys
sys.path.append('STARparser/')
import bmrb

class star2nef(object):
    
    def __init__(self,fname):
        self.fname=fname
        
        
    def readFile(self):
        dat=bmrb.entry.fromFile(self.fname)
        print dat.printTree()
        

if __name__=="__main__":
    s=star2nef('/home/kumaran/Desktop/ForKumaran/2LCI/2LCI.nef')
    s.readFile()
    