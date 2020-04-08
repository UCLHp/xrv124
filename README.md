# xrv124

![Current Version](https://img.shields.io/badge/version-0.1.0-green.svg)

A set of scripts for the analysis and visualization of data acquired by the Logos XRV-124 scintillating cone. Analysis currently includes, for a selection of gantry angles and beam energies:

  * Spot shifts (in x and y of the BEV coordinates)
  * Spot sizes (in both BEV and "spot" coordinate systems; see documentation)


## Usage
To run the analysis: ```python xrv124_run.py```.  

You will need the full data set acquired during monthly QA, with beams corresponding to the gantry angles and energies specified in xrv124_run.py


## Limitations / known bugs
In this first version there are several limitations:

  * The analysis will only run on the full data set. The logos software does not have a way of recognising beam energy, hence if any beam was not captured during the acquisition it would not be possible to match the output files generated with a specific gantry angle and energy.
  * Spot images may saturate if the wrong acquisition parameters are used. This will mean any Gaussian fit when extracting sigmas will not be reliable.
  * Apparently very occasionally the entry and exit spot images can be of different sizes. I have not dealt with this yet.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

