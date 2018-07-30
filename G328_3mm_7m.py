from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes
__rethrow_casa_exceptions = True
context = h_init()
context.set_state('ProjectSummary', 'proposal_code', '2017.1.01355.L')
context.set_state('ProjectSummary', 'piname', 'unknown')
context.set_state('ProjectSummary', 'proposal_title', 'unknown')
context.set_state('ProjectStructure', 'ous_part_id', 'X1988847564')
context.set_state('ProjectStructure', 'ous_title', 'Undefined')
context.set_state('ProjectStructure', 'ppr_file', '/opsw/alma/dared/opt/c5r1/mnt/dataproc/2017.1.01355.L_2017_11_22T16_25_55.616/SOUS_uid___A001_X1296_X167/GOUS_uid___A001_X1296_X168/MOUS_uid___A001_X1296_X16d/working/PPR_uid___A001_X1296_X16e.xml')
context.set_state('ProjectStructure', 'ps_entity_id', 'uid://A001/X1220/Xddd')
context.set_state('ProjectStructure', 'recipe_name', 'hifa_calimage')
context.set_state('ProjectStructure', 'ous_entity_id', 'uid://A001/X1220/Xdd9')
context.set_state('ProjectStructure', 'ousstatus_entity_id', 'uid://A001/X1296/X16d')
try:
    hifa_importdata(vis=['uid___A002_Xc6c0d5_X3f2e'], session=['session_1'])
    #fixsyscaltimes(vis = 'uid___A002_Xc6d2f9_X4380.ms')# SACM/JAO - Fixes
    fixsyscaltimes(vis = 'uid___A002_Xc6c0d5_X3f2e.ms')# SACM/JAO - Fixes
    h_save() # SACM/JAO - Finish weblog after fixes
    h_init() # SACM/JAO - Restart weblog after fixes
    hifa_importdata(vis=['uid___A002_Xc6c0d5_X3f2e'], session=['session_1'])
    hifa_flagdata(pipelinemode="automatic")
    hifa_fluxcalflag(pipelinemode="automatic")
    hif_rawflagchans(pipelinemode="automatic")
    hif_refant(pipelinemode="automatic")
    #flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms',antenna='CM06',correlation="YY")
    h_tsyscal(pipelinemode="automatic")
    flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
             mode='manual', spw='16:990~1100', field="G328.25", reason='N2HP_line')
    hifa_tsysflag(pipelinemode="automatic")
    # Here implementing manual flagging following Roberto's suggestion
    #
    # hifa_tsysflag(pipelinemode="automatic")
    #
    # The Tsys calibration table is analyzed and deviant points are flagged.
    #
    #flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         mode='summary')
#    flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         mode='summary')
 #   
 #   flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         mode='summary')
#    flagdata(flagbackup=False,
#         vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         reason='any', mode='list', action='apply', savepars=False,
#         inpfile=["mode='summary' name='before'", "spw='18' antenna='CM06' timerange='2017/11/12/17:05:20~2017/11/12/17:05:21' reason='max_abs'","spw='18' antenna='CM06' timerange='2017/11/12/17:30:21~2017/11/12/17:30:22' reason='max_abs'","spw='18' antenna='CM06' timerange='2017/11/12/17:17:51~2017/11/12/17:17:53' reason='max_abs'", "spw='18' antenna='CM06' timerange='2017/11/12/17:03:22~2017/11/12/17:03:24' reason='max_abs'", "spw='18' antenna='CM06' timerange='2017/11/12/17:15:58~2017/11/12/17:15:59' reason='max_abs'", "spw='18' antenna='CM06' timerange='2017/11/12/17:28:28~2017/11/12/17:28:30' reason='max_abs'", "mode='summary' name='after'"])
    
#    flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         mode='summary')
#    
#    flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#         mode='summary')
    #flagdata(vis='uid___A002_Xc6d2f9_X4380.ms.h_tsyscal.s6_3.tsyscal.tbl',        # mode='summary')
    #flagdata(vis='uid___A002_Xc6d2f9_X4380.ms.h_tsyscal.s6_3.tsyscal.tbl',         #mode='summary')
#    flagdata(vis='uid___A002_Xc6c0d5_X3f2e.ms.h_tsyscal.s6_1.tsyscal.tbl',
#             mode='manual', spw='16:990~1100', reason='N2HP_line')
   
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
