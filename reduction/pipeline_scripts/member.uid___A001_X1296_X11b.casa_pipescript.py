from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X711178443')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opsw/alma/dared/opt/c5r1/mnt/dataproc/2017.1.01355.L_2018_01_15T10_00_42.752/SOUS_uid___A001_X1296_X119/GOUS_uid___A001_X1296_X11a/MOUS_uid___A001_X1296_X11b/working/PPR_uid___A001_X1296_X11c.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X11b')
try:
    hifa_importdata(vis=['uid___A002_Xc7a409_X351d', 'uid___A002_Xc7cf4e_X52fc', 'uid___A002_Xc7e4e4_X3ac2'], session=['session_1', 'session_2', 'session_3'])
    fixsyscaltimes(vis = 'uid___A002_Xc7e4e4_X3ac2.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc7cf4e_X52fc.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc7a409_X351d.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    h_init() # SACM/JAO - Restart weblog after fixes
    hifa_importdata(vis=['uid___A002_Xc7a409_X351d', 'uid___A002_Xc7cf4e_X52fc', 'uid___A002_Xc7e4e4_X3ac2'], session=['session_1', 'session_2', 'session_3'])
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
    hif_checkproductsize(maxcubelimit=40.0, maxproductsize=400.0, maxcubesize=30.0)
finally:
    h_save()
