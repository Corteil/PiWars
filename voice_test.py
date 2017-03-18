import os
text = "'Hello World'"
command = "flite -voice rms -t " + text
os.system(command)