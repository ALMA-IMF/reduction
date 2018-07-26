from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X458885948')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opt/dared/mnt/spool/2017.1.01355.L_2018_05_08T13_10_00.360/SOUS_uid___A001_X1296_X211/GOUS_uid___A001_X1296_X212/MOUS_uid___A001_X1296_X217/working/PPR_uid___A001_X1296_X218.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X217')
try:
    hifa_importdata(vis=['uid___A002_Xc733ea_X753', 'uid___A002_Xc772ca_X392', 'uid___A002_Xca2b8a_X6be2', 'uid___A002_Xcbdb2a_X6e67', 'uid___A002_Xcbdb2a_X8114', 'uid___A002_Xcbdb2a_X13ce2', 'uid___A002_Xcc10e0_X6dd3', 'uid___A002_Xcc3ae3_X95bc', 'uid___A002_Xccb526_Xcc36', 'uid___A002_Xccb526_Xd6ae'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_11', 'session_11'])
    fixsyscaltimes(vis = 'uid___A002_Xcbdb2a_X13ce2.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcc3ae3_X95bc.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcbdb2a_X6e67.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc772ca_X392.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcc10e0_X6dd3.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xccb526_Xcc36.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcbdb2a_X8114.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc733ea_X753.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xccb526_Xd6ae.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xca2b8a_X6be2.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    context = h_init() # SACM/JAO - Restart weblog after fixes
    context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
    context.set_state('ProjectSummary', 'piname', 'unknown')
    context.set_state('ProjectSummary', 'proposal_title', 'unknown')
    context.set_state('ProjectStructure', 'ous_part_id', 'X458885948')
    context.set_state('ProjectStructure', 'ous_title', 'Undefined')
    context.set_state('ProjectStructure', 'ppr_file', '/opt/dared/mnt/spool/2017.1.01355.L_2018_05_08T13_10_00.360/SOUS_uid___A001_X1296_X211/GOUS_uid___A001_X1296_X212/MOUS_uid___A001_X1296_X217/working/PPR_uid___A001_X1296_X218.xml')
    context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
    context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
    context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
    context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X217')
    hifa_importdata(vis=['uid___A002_Xc733ea_X753', 'uid___A002_Xc772ca_X392', 'uid___A002_Xca2b8a_X6be2', 'uid___A002_Xcbdb2a_X6e67', 'uid___A002_Xcbdb2a_X8114', 'uid___A002_Xcbdb2a_X13ce2', 'uid___A002_Xcc10e0_X6dd3', 'uid___A002_Xcc3ae3_X95bc', 'uid___A002_Xccb526_Xcc36', 'uid___A002_Xccb526_Xd6ae'], session=['session_1', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_11', 'session_11'])
    hifa_flagdata(pipelinemode="automatic")
    hifa_fluxcalflag(pipelinemode="automatic")
    hif_rawflagchans(pipelinemode="automatic")
    hif_refant(pipelinemode="automatic")
    h_tsyscal(pipelinemode="automatic")
    #Flagging Tsys channels contaminated with emission from the science target or ISM
    flagdata(vis = 'uid___A002_Xc733ea_X753.ms.h_tsyscal.s6_1.tsyscal.tbl', mode = 'manual', spw = '26:245~275', flagbackup = False)
    flagdata(vis = 'uid___A002_Xc772ca_X392.ms.h_tsyscal.s6_3.tsyscal.tbl', mode = 'manual', spw = '26:245~275', flagbackup = False)
    flagdata(vis = 'uid___A002_Xca2b8a_X6be2.ms.h_tsyscal.s6_5.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xcbdb2a_X13ce2.ms.h_tsyscal.s6_11.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xcbdb2a_X6e67.ms.h_tsyscal.s6_7.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xcbdb2a_X8114.ms.h_tsyscal.s6_9.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xcc10e0_X6dd3.ms.h_tsyscal.s6_13.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xcc3ae3_X95bc.ms.h_tsyscal.s6_15.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xccb526_Xcc36.ms.h_tsyscal.s6_17.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    flagdata(vis = 'uid___A002_Xccb526_Xd6ae.ms.h_tsyscal.s6_19.tsyscal.tbl', mode = 'manual', spw = '26:298~308', flagbackup = False)
    hifa_tsysflag(pipelinemode="automatic")
    hifa_antpos(pipelinemode="automatic")
    hifa_wvrgcalflag(pipelinemode="automatic")
    hif_lowgainflag(pipelinemode="automatic")
    hif_setmodels(pipelinemode="automatic")
    hifa_bandpassflag(pipelinemode="automatic")
    hifa_spwphaseup(pipelinemode="automatic")
    hifa_gfluxscaleflag(pipelinemode="automatic")
    hifa_gfluxscale(pipelinemode="automatic")
    hifa_timegaincal(pipelinemode="automatic")
    hif_applycal(pipelinemode="automatic")
    hifa_imageprecheck(pipelinemode="automatic")
    hif_makeimlist(intent='PHASE,BANDPASS,CHECK')
    hif_makeimages(pipelinemode="automatic")
    hif_checkproductsize(maxcubelimit=40.0, maxproductsize=400.0, maxcubesize=30.0)
    hifa_exportdata(pipelinemode="automatic")
    hif_mstransform(pipelinemode="automatic")
    hifa_flagtargets(pipelinemode="automatic")
    hif_makeimlist(specmode='mfs')
    hif_findcont(pipelinemode="automatic")
    hif_uvcontfit(pipelinemode="automatic")
    hif_uvcontsub(pipelinemode="automatic")
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(specmode='cont')
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(pipelinemode="automatic")
    hif_makeimages(pipelinemode="automatic")
    hif_makeimlist(specmode='repBW')
    hif_makeimages(pipelinemode="automatic")
    hifa_exportdata(pipelinemode="automatic")
finally:
    h_save()
