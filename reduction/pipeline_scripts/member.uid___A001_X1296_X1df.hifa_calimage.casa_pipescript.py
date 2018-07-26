from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X870875696')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opsw/alma/dared/opt/c5r1/mnt/dataproc/2017.1.01355.L_2018_06_02T08_12_17.718/SOUS_uid___A001_X1296_X1d9/GOUS_uid___A001_X1296_X1da/MOUS_uid___A001_X1296_X1df/working/PPR_uid___A001_X1296_X1e0.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X1df')
try:
    hifa_importdata(vis=['uid___A002_Xcb339b_X50b4', 'uid___A002_Xcb4a8e_X405c', 'uid___A002_Xcb4a8e_X52b0', 'uid___A002_Xcbc47c_Xeadc', 'uid___A002_Xcbf591_X9bc1', 'uid___A002_Xcc10e0_X11fa', 'uid___A002_Xcc10e0_X1c46', 'uid___A002_Xccde5b_X387c', 'uid___A002_Xccea8d_X4bd1', 'uid___A002_Xccea8d_Xe1d1', 'uid___A002_Xcd64ec_X45ba', 'uid___A002_Xcd64ec_X5416', 'uid___A002_Xcd64ec_Xe856'], session=['session_1', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_9', 'session_10', 'session_11', 'session_12', 'session_12', 'session_13'])
    fixsyscaltimes(vis = 'uid___A002_Xcbf591_X9bc1.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcb339b_X50b4.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcd64ec_X45ba.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xccea8d_X4bd1.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcd64ec_Xe856.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcb4a8e_X52b0.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcc10e0_X11fa.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcc10e0_X1c46.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xccde5b_X387c.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcb4a8e_X405c.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcbc47c_Xeadc.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xccea8d_Xe1d1.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xcd64ec_X5416.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    h_init() # SACM/JAO - Restart weblog after fixes
    hifa_importdata(vis=['uid___A002_Xcb339b_X50b4', 'uid___A002_Xcb4a8e_X405c', 'uid___A002_Xcb4a8e_X52b0', 'uid___A002_Xcbc47c_Xeadc', 'uid___A002_Xcbf591_X9bc1', 'uid___A002_Xcc10e0_X11fa', 'uid___A002_Xcc10e0_X1c46', 'uid___A002_Xccde5b_X387c', 'uid___A002_Xccea8d_X4bd1', 'uid___A002_Xccea8d_Xe1d1', 'uid___A002_Xcd64ec_X45ba', 'uid___A002_Xcd64ec_X5416', 'uid___A002_Xcd64ec_Xe856'], session=['session_1', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8', 'session_9', 'session_10', 'session_11', 'session_12', 'session_12', 'session_13'])
    hifa_flagdata(pipelinemode="automatic")
    hifa_fluxcalflag(pipelinemode="automatic")
    hif_rawflagchans(pipelinemode="automatic")
    hif_refant(pipelinemode="automatic")
    h_tsyscal(pipelinemode="automatic")
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
    hif_checkproductsize(maxcubelimit=80.0, maxproductsize=800.0, maxcubesize=60.0)
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
finally:
    h_save()
