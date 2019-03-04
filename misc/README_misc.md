I suggest to add a summary of what the script does in this file. 

### Summary of casa_pipescript_BirdieTsysFlag.py  ###

Regarding my pipeline tests in uid___A002_Xc889b6_X5cbc.ms to manually flag extra "birdies" in Tsys not taken by the pipeline (the pipeline only recognized one in DA43, but there were similar in 6 more antennas).

Following the instructions in the Pipeline Users Guide did not work: I ran fully (except the final cube making) casa_pipescript.py and added the extra flagging in the "Helper" flagtemplate.txt file. The pipeline ignored my manual flagging. confirmed this by plotting in plotms uid___A002_Xc889b6_X5cbc.ms.h_tsyscal.s6_1.tsyscal.tbl (where the pipeline-determined flag in DA43 is seen but not my manual flag to many other antennas is not), and by checking the CASA log file (where the pipeline flag command in DA43 is seen but my mannual flag commands are not).
In the end, it worked by manually commenting out hifa_tsysflag(pipelinemode="automatic") in casa_pipescript, and substituting it by all its flagdata commands as extracted from casa_commands.log plus the extra flagging I wanted.

The Tsys birdies in Tsys spw19 (sci spw27) are not the cause of the large-scale continuum ripples detected by Adam in the spw27 continuum image. To me, it looks like some bad phases in some undetected antenna ...
