# in order to write parameters for the CORE module without being inside the CORE module
# we copy our local parameters file and clone it into a parameters.py file within the CORE module, before we init the module
coreParamFile = open("./CORE/parameters.py", "w")
lParamFile = open("parameters.py", "r")
lines = lParamFile.readlines()
coreParamFile.writelines(lines)
coreParamFile.close()

import pipeline
import CORE.main # this will now reference the clone of our local param file within the CORE module

CORE.main.start(pipeline.pipeline) # entry point
