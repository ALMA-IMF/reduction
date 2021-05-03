'''
Script to pass the continuum self-calibration to the line data, which is a per-spw, per observing block. 
Note: as of 26.02.2021 this is only working for the wide-BW spws (3 out of 4 in B3) because the narrow-BW spws do not have self-cal continuum solutions. 
But it works for the narrow-band spw if one uses solutions from the neighboring wide-band spw, e.g., for B3 spw0 visibilities could use spw1 solutions. 
'''

#vis=['/lustre/roberto/ALMA_IMF/lines/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e7/calibrated/uid___A002_Xcc626d_X9fda_G010.62_B3_spw1.split', '/lustre/roberto/ALMA_IMF/lines/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e5/calibrated/uid___A002_Xc86fe5_X7a9e_G010.62_B3_spw1.split', '/lustre/roberto/ALMA_IMF/lines/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e5/calibrated/uid___A002_Xc89480_X57ef_G010.62_B3_spw1.split'],concatvis="/lustre/roberto/ALMA_IMF/lines/science_goal.uid___A001_X1296_X1e3/group.uid___A001_X1296_X1e4/member.uid___A001_X1296_X1e9/calibrated/G010.62_B3_spw1_12M.concat.ms"

vis_list = ['uid___A002_Xcc626d_X9fda_G010.62_B3_spw1.split.sc1', 'uid___A002_Xc86fe5_X7a9e_G010.62_B3_spw1.split.sc1', 'uid___A002_Xc89480_X57ef_G010.62_B3_spw1.split.sc1']
tab_list = ['G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase1_inf.cal', 'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase2_40s.cal', \
'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase3_25s.cal', 'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase4_10s.cal', \
'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase5_10s.cal', 'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase6_10s.cal', \
'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase7_inf.cal', 'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_amp8_inf.cal', \
'G010.62_B3_uid___A001_X1296_X1e5_continuum_merged_12M_phase9_inf.cal']

#vis_list = ['uid___A002_Xc8ed16_X5c3d_G333.60_B3_spw1.split.sc2','uid___A002_Xcd07af_X41d5_G333.60_B3_spw1.split.sc2']
#tab_list = ['G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_phase1_inf.cal','G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_phase2_15s.cal',\
#'G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_phase3_5s.cal','G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_phase4_int.cal',\
#'G333.60_B3_uid___A001_X1296_X1a3_continuum_merged_12M_phase5_inf.cal']



from casatasks import vishead
from casatools import table
tb = table()

def get_spw_map(vis, caltables):

    vhead_spw = vishead(vis=vis, mode='get', hdkey='spw_name')
    vis_spwname = vhead_spw[0][0]
    vhead_spw = vishead(vis=vis, mode='get', hdkey='schedule')
    vis_ebname = vhead_spw[0]['r1']

    print('Visibility spw name:')
    print(vis_spwname)
    print('Visibility EB name:')
    print(vis_ebname)

    spwmap = []
    for table in caltables:
    
        # Extract spw index to use from calibration table 
        tab = table
        
        print(f"\nWorking on table {tab}")
        
        tb.open(tab+'/OBSERVATION')
        obsid_schedule = tb.getcol('SCHEDULE')
        tb.close()
        
        #print(f"obsid_schedule: {obsid_schedule}\n\nvis_ebname={vis_ebname}")
        
        obsid_match = np.where(np.all(obsid_schedule == vis_ebname, axis=0))[0]
        if len(obsid_match) == 1:
            obsid_match = obsid_match[0]
        else:
            raise ValueError("Found multiple obsid matches, which shouldn't happen.")
        #print(f"obsid_match={obsid_match}")
        
        tb.open(tab+'/SPECTRAL_WINDOW')
        #print('\n Colnames in SPECTRAL_WINDOW table:')
        #print(tb.colnames())
        tab_spws = tb.getcol('NAME')
        tb.close()
        
        tb.open(tab)
        spw_id_num = tb.getcol('SPECTRAL_WINDOW_ID')
        obs_id_num = tb.getcol('OBSERVATION_ID')
        tb.close()

        index_spw = np.where(tab_spws == vis_spwname)
        #print(f"index_spw={index_spw}")
        #print(f"spw_id_num={spw_id_num}")
        
        spw_match = np.any(spw_id_num[None,:] == index_spw[0][:,None], axis=0)
        assert spw_match.shape == obs_id_num.shape
        
        match = (obs_id_num == obsid_match) & spw_match
        unique_spw_id = np.unique(spw_id_num[match])
        print(f"unique_spw_id={unique_spw_id}")
        if len(unique_spw_id) != 1:
            raise ValueError("Found 0 or >1 SPW ids")

        # unique_spw_id should be a length-1 array
        spwmap.append(unique_spw_id[0])
        print(f'Index in cal table of spw corresponding to ms file is: {unique_spw_id}')
    return spwmap


if __name__ == "__main__":
    #Clearcal with addmodel
    clearcal(vis=vis, addmodel=True)

    # Run applycal
    '''
    Note: gainfield='nearest' to apply the solutions per mosaic pointing. Selecting a specific field (gainfield='6' for center of G333.6 B3 mosaic) or leaving in blank (gainfield='') also seem to work. 
    #2021-02-27 01:12:45	INFO	applycal::::	Calibration field mapping for G333.60_B3__continuum_merged_12M_phase1_inf.cal (via gainfield='nearest'): [6, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    #2021-02-27 01:12:45	INFO	applycal::::+	 Separations (deg): [0.0038401, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Note: interp='linearperobs' to interpolate linearly in time but respect boundaries of the different observing blocks (observations) produces warning: 
    2021-02-27 01:35:58 WARN applycal	Multiple ObsIds found in G333.60_B3__continuum_merged_12M_phase1_inf.cal, but they do not match the MS ObsIds; turning off 'perobs'.
    Note: no specification for frequency in interp= because the calibration table has only one value per spw, and the applycal
    documentation says: Specifications for frequency are ignored when the calibration table has no channel-dependence. But if interp='linear,nearest' is used, it also works. 
    Note: applymode='calflag' (default 'calflag)'. Should we use 'calonly' to avoid flagging data without solutions? I think this was used for the continuum selfcal, although the documentation warns against this option. 
    Note: putting the wrong spw in spwmap also works, so applycal ends up doing the frequency interpolation, but the number of rejected points increases. For example, if spw3 is used for spw1 visibilities: 
    # 2021-02-27 01:44:33	INFO	applycal::::	   T Jones: In: 448892160 / 1862784000   (24.0979179551%) --> Out: 817658880 / 1862784000   (43.8944547516%) (G333.60_B3__continuum_merged_12M_phase1_inf.cal)
    '''

    print('Running applycal ...')
    applycal(vis=vis, gaintable=tab_list, gainfield='nearest', interp='linear', spwmap=spwmap, applymode='calonly', calwt=False)
    # applymode='trial' for trial tests

