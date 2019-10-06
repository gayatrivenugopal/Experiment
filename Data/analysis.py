from data import Data
import numpy as np

if __name__ == '__main__':
    #load the ranked dataset
    data = Data().data
    words = set()
    words = data['words']
    print(words, len(words))
    #print(len(data[data['complexity']==0]))

    #TODO:  Calculate Fleiss' Kappa

    '''
    array: number of raters who assigned word i to category j (j=0 simple,1 complex)
    '''
