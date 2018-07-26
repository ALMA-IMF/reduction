from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X501228279')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opsw/alma/dared/opt/c5r1/mnt/dataproc/2017.1.01355.L_2018_01_22T00_53_28.968/SOUS_uid___A001_X1296_X12d/GOUS_uid___A001_X1296_X12e/MOUS_uid___A001_X1296_X133/working/PPR_uid___A001_X1296_X134.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X133')
try:
    hifa_importdata(vis=['uid___A002_Xc89480_X5f49', 'uid___A002_Xc89480_X67a2', 'uid___A002_Xc89480_Xfb30', 'uid___A002_Xc8b2b0_X7f0d', 'uid___A002_Xc8b2b0_X8853', 'uid___A002_Xc8d560_X7abc', 'uid___A002_Xc92012_Xe8b', 'uid___A002_Xc92fe3_X7c3b'], session=['session_2', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8'])
    fixsyscaltimes(vis = 'uid___A002_Xc92012_Xe8b.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc8b2b0_X8853.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc89480_X5f49.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc89480_X67a2.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc8b2b0_X7f0d.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc8d560_X7abc.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc89480_Xfb30.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc92fe3_X7c3b.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    h_init() # SACM/JAO - Restart weblog after fixes
    hifa_importdata(vis=['uid___A002_Xc89480_X5f49', 'uid___A002_Xc89480_X67a2', 'uid___A002_Xc89480_Xfb30', 'uid___A002_Xc8b2b0_X7f0d', 'uid___A002_Xc8b2b0_X8853', 'uid___A002_Xc8d560_X7abc', 'uid___A002_Xc92012_Xe8b', 'uid___A002_Xc92fe3_X7c3b'], session=['session_2', 'session_2', 'session_3', 'session_4', 'session_5', 'session_6', 'session_7', 'session_8'])
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
