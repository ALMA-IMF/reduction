Data reduction repository for ALMA-IMF.
The current 'line_imaging.py' makes use of the auto-masking method by combing both auto-multithresh and multiscale. Nevertheless, this combination has not been extensively tested as noted in CASAguide at 
https://casaguides.nrao.edu/index.php/M100_Band3_Combine_5.4 .  When constructing your own parameter sets in 'imaging_parameters.py', please try using `hogbom` clean instead.
We have not yet converged on the best set of parameters for the line cleaning.


