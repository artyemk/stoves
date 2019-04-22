import os
from glob import glob

for i in glob("*"):
    os.rename(i,i.replace(" ","_"))
