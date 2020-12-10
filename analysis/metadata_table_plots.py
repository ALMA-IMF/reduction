import numpy as np
from astropy import table
from astropy.table import Table

import runpy
runpy.run_path('latex_table.py')
runpy.run_path('latex_table_bsens.py')

bp_tbl = Table.read('bandpass_fraction.ecsv')
bp_tbl['band'] = [f'B{b}' for b in bp_tbl['band']]
bp_tbl.rename_column('field','region')
bp_tbl = table.join(bp_tbl.group_by('config').groups[0], bp_tbl.group_by('config').groups[1], keys=('region', 'band'))
bp_tbl.rename_column('bwfrac_1', '12Mlong_frac')
bp_tbl.rename_column('bwfrac_2', '12Mshort_frac')
bp_tbl.remove_column('config_1')
bp_tbl.remove_column('config_2')


tbl_selfcal = table.join(Table.read('metadata_sc.ecsv'), bp_tbl, keys=('region', 'band'))
bad = np.array(['diff' in x for x in tbl_selfcal['filename']])
keep_selfcal = ((tbl_selfcal['suffix'] == 'finaliter') &
                (tbl_selfcal['robust'] == 'r0.0') &
                (~tbl_selfcal['pbcor']) &
                (~tbl_selfcal['bsens']) & 
                (~bad))
wtbl_selfcal = tbl_selfcal[keep_selfcal]
assert len(wtbl_selfcal) == 29

tbl_bsens = table.join(Table.read('metadata_bsens_cleanest.ecsv'), bp_tbl, keys=('region', 'band'))
bad = np.array(['diff' in x for x in tbl_bsens['filename']])
keep_bsens = ((tbl_bsens['suffix'] == 'finaliter') &
              (tbl_bsens['robust'] == 'r0.0') &
              (~tbl_bsens['pbcor']) &
              (tbl_bsens['bsens']) &
              (~bad))
wtbl_bsens = tbl_bsens[keep_bsens]
assert len(wtbl_bsens) == 29


wtbl_bsens['bsens_improvement'] = wtbl_bsens['mad_sample_bsens']/wtbl_bsens['mad_sample_cleanest']

b3style = {'marker':'o', 'markersize':10, 'alpha':0.75, 'markeredgecolor':(0,0,0,0.1), 'linestyle':'none'}
b6style = {'marker':'s', 'markersize':10, 'alpha':0.75, 'markeredgecolor':(0,0,0,0.1), 'linestyle':'none'}

import pylab as pl

b3 = wtbl_selfcal['band'] == 'B3'
b6 = wtbl_selfcal['band'] == 'B6'

fig1 = pl.figure(1, figsize=(10,5))
fig1.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3]/wtbl_selfcal['ppbeam'][b3], wtbl_selfcal['dr_improvement'][b3], **b3style)
ax1.plot(wtbl_selfcal['sum_post'][b6]/wtbl_selfcal['ppbeam'][b6], wtbl_selfcal['dr_improvement'][b6], **b6style)
ax1.plot(np.linspace(0, 50), np.linspace(0, 50)*0.45/50 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Dynamic Range Improvement")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3], wtbl_selfcal['dr_improvement'][b3], **b3style, label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6], wtbl_selfcal['dr_improvement'][b6], **b6style, label='B6')
ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/dynamic_range_improvement_selfcal.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/dynamic_range_improvement_selfcal.png", bbox_inches='tight')





b3 = wtbl_bsens['band'] == 'B3'
b6 = wtbl_bsens['band'] == 'B6'

fig2 = pl.figure(2, figsize=(10,5))
fig2.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_bsens['sum_cleanest'][b3]/wtbl_bsens['ppbeam'][b3], wtbl_bsens['sum_bsens'][b3]/wtbl_bsens['sum_cleanest'][b3], **b3style)
ax1.plot(wtbl_bsens['sum_cleanest'][b6]/wtbl_bsens['ppbeam'][b6], wtbl_bsens['sum_bsens'][b6]/wtbl_bsens['sum_cleanest'][b6], **b6style)
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum (cleanest) [Jy]")
ax1.set_ylabel("Sum (bsens) / Sum (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_cleanest'][b3], wtbl_bsens['max_bsens'][b3]/wtbl_bsens['max_cleanest'][b3], **b3style, label='B3')
ax2.plot(wtbl_bsens['max_cleanest'][b6], wtbl_bsens['max_bsens'][b6]/wtbl_bsens['max_cleanest'][b6], **b6style, label='B6')
#ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak (cleanest)")
ax2.set_ylabel("Peak (bsens) / Peak (cleanest)")
#ax2.add_patch(pl.Rectangle((-0.05,0.4), width=0.45, height=0.55, facecolor='r', alpha=0.25))
pl.legend(loc='best')

pl.savefig("../datapaper/figures/bsens_flux_change.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/bsens_flux_change.png", bbox_inches='tight')


b3bs = wtbl_bsens['band'] == 'B3'
b6bs = wtbl_bsens['band'] == 'B6'

fig9 = pl.figure(9, figsize=(10,5))
fig9.clf()
fig9.suptitle("DIAGNOSTIC - everywhere vs sampled mad")
ax1 = pl.subplot(1,2,1)
ax1.set_title("BSENS")
ax1.plot(wtbl_bsens['mad_bsens'][b3bs], wtbl_bsens['mad_sample_bsens'][b3bs], **b3style)
ax1.plot(wtbl_bsens['mad_bsens'][b6bs], wtbl_bsens['mad_sample_bsens'][b6bs], **b6style)
ax1.plot([0,0.001], [0, 0.001], 'k--')
ax1.set_xlabel("MAD everywhere")
ax1.set_ylabel("MAD sampleregion")

ax2 = pl.subplot(1,2,2)
ax2.set_title("cleanest")
ax2.plot(wtbl_bsens['mad_cleanest'][b3bs], wtbl_bsens['mad_sample_cleanest'][b3bs], **b3style)
ax2.plot(wtbl_bsens['mad_cleanest'][b6bs], wtbl_bsens['mad_sample_cleanest'][b6bs], **b6style)
ax2.set_xlabel("MAD everywhere")
ax2.set_ylabel("MAD sampleregion")
ax2.plot([0,0.001], [0, 0.001], 'k--')


# bsens_rms_change:
# How much does the RMS noise improve going from cleanest (denominator) to bsens (numerator)?
fig3 = pl.figure(3, figsize=(15,5))
fig3.clf()
ax1 = pl.subplot(1,3,1)
ax1.plot(wtbl_bsens['sum_cleanest'][b3]/wtbl_bsens['ppbeam'][b3], wtbl_bsens['mad_sample_bsens'][b3]/wtbl_bsens['mad_sample_cleanest'][b3], **b3style)
ax1.plot(wtbl_bsens['sum_cleanest'][b6]/wtbl_bsens['ppbeam'][b6], wtbl_bsens['mad_sample_bsens'][b6]/wtbl_bsens['mad_sample_cleanest'][b6], **b6style)
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum (cleanest) [Jy]")
ax1.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

ax2 = pl.subplot(1,3,2)
ax2.plot(wtbl_bsens['max_cleanest'][b3], wtbl_bsens['mad_sample_bsens'][b3]/wtbl_bsens['mad_sample_cleanest'][b3], **b3style, label='B3')
ax2.plot(wtbl_bsens['max_cleanest'][b6], wtbl_bsens['mad_sample_bsens'][b6]/wtbl_bsens['mad_sample_cleanest'][b6], **b6style, label='B6')
#ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak (cleanest)")
ax2.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax2.add_patch(pl.Rectangle((-0.05,0.4), width=0.45, height=0.55, facecolor='r', alpha=0.25))
pl.legend(loc='best')

ax3 = pl.subplot(1,3,3)
ax3.plot(wtbl_bsens['12Mshort_frac'][b3], wtbl_bsens['mad_sample_bsens'][b3]/wtbl_bsens['mad_sample_cleanest'][b3], **b3style)
ax3.plot(wtbl_bsens['12Mshort_frac'][b6], wtbl_bsens['mad_sample_bsens'][b6]/wtbl_bsens['mad_sample_cleanest'][b6], **b6style)
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax3.set_xlabel("Fraction of Bandwidth in 'cleanest'")
ax3.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

pl.savefig("../datapaper/figures/bsens_rms_change.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/bsens_rms_change.png", bbox_inches='tight')


b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'
wtbl_selfcal['SensVsReqPost'] = wtbl_selfcal['mad_sample_post'] / wtbl_selfcal['Req_Sens'] * 1000


fig1 = pl.figure(4, figsize=(10,5))
fig1.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], wtbl_selfcal['SensVsReqPost'][b3sc], **b3style)
ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], wtbl_selfcal['SensVsReqPost'][b6sc], **b6style)

w51e_sel = (wtbl_selfcal['region'] == 'W51-E')
if (b3sc & w51e_sel).sum() == 1:
    ax1.annotate('W51-E', (wtbl_selfcal['sum_post'][b3sc & w51e_sel]/wtbl_selfcal['ppbeam'][b3sc & w51e_sel],
                           wtbl_selfcal['SensVsReqPost'][b3sc & w51e_sel]))
else:
    print("W51-E B3 is missing!  Or there are too many!")
#ax1.annotate('W51-IRS2', (wtbl_selfcal['sum_post'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]/wtbl_selfcal['ppbeam'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')],
#                          wtbl_selfcal['SensVsReqPost'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
#ax1.annotate('G010.62', (wtbl_selfcal['sum_post'][b3sc & (wtbl_selfcal['region'] == 'G010.62')]/wtbl_selfcal['ppbeam'][b3sc & (wtbl_selfcal['region'] == 'G010.62')],
#                         wtbl_selfcal['SensVsReqPost'][b3sc & (wtbl_selfcal['region'] == 'G010.62')]))
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Measured Noise / Requested Sensitivity")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3sc], wtbl_selfcal['SensVsReqPost'][b3sc], **b3style, label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6sc], wtbl_selfcal['SensVsReqPost'][b6sc], **b6style, label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
if (b3sc & w51e_sel).sum() == 1:
    ax2.annotate('W51-E', (wtbl_selfcal['max_post'][b3sc & w51e_sel], wtbl_selfcal['SensVsReqPost'][b3sc & w51e_sel]))
#ax2.annotate('W51-IRS2', (wtbl_selfcal['max_post'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')], wtbl_selfcal['SensVsReqPost'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
ax2.annotate('W51-IRS2', (wtbl_selfcal['max_post'][b6sc & (wtbl_selfcal['region'] == 'W51-IRS2')], wtbl_selfcal['SensVsReqPost'][b6sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Measured Noise / Requested Sensitivity")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/noise_excess.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess.png", bbox_inches='tight')




b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'

# fig5 = pl.figure(5, figsize=(10,5))
# fig5.clf()
# ax1 = pl.subplot(1,2,1)
# ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], 1./wtbl_selfcal['BeamVsReq'][b3sc], **b3style)
# ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], 1./wtbl_selfcal['BeamVsReq'][b6sc], **b6style)
# ax1.plot(ax1.get_xlim(), [1,1], 'k--')
# ax1.set_xlabel("Sum [Jy]")
# ax1.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")
#
# ax2 = pl.subplot(1,2,2)
# ax2.plot(wtbl_selfcal['max_post'][b3sc], 1./wtbl_selfcal['BeamVsReq'][b3sc], **b3style, label='B3')
# ax2.plot(wtbl_selfcal['max_post'][b6sc], 1./wtbl_selfcal['BeamVsReq'][b6sc], **b6style, label='B6')
# ax2.plot(ax2.get_xlim(), [1,1], 'k--')
# ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
# ax2.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")
# pl.legend(loc='best')
#
# pl.savefig("../datapaper/figures/beam_size_comparison.pdf", bbox_inches='tight')
# pl.savefig("../datapaper/figures/beam_size_comparison.png", bbox_inches='tight')


fig5 = pl.figure(5, figsize=(10,5))
fig5.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['SensVsReqPost'][b3sc], 1./wtbl_selfcal['BeamVsReq'][b3sc], label='B3', **b3style)
ax1.plot(wtbl_selfcal['SensVsReqPost'][b6sc], 1./wtbl_selfcal['BeamVsReq'][b6sc], label='B6', **b6style)
lims = ax1.axis()
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.plot([1,1], ax1.get_ylim(), 'k--')
ax1.set_xlabel("Measured Noise / Requested Sensitivity")
ax1.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")
ax1.axis(lims)

b3bs = wtbl_bsens['band'] == 'B3'
b6bs = wtbl_bsens['band'] == 'B6'
wtbl_bsens['SensVsReqPost'] = wtbl_bsens['mad_sample_bsens'] / wtbl_bsens['Req_Sens'] * 1000

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['SensVsReqPost'][b3bs], 1./wtbl_bsens['BeamVsReq'][b3bs], label='B3', **b3style)
ax2.plot(wtbl_bsens['SensVsReqPost'][b6bs], 1./wtbl_bsens['BeamVsReq'][b6bs], label='B6', **b6style)
lims = ax2.axis()
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.plot([1,1], ax2.get_ylim(), 'k--')
ax2.set_xlabel("Measured Noise / Requested Sensitivity")
ax2.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")
ax2.axis(lims)

pl.legend(loc='best')

pl.savefig("../datapaper/figures/beam_size_comparison.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/beam_size_comparison.png", bbox_inches='tight')







b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'

fig6 = pl.figure(6, figsize=(10,5))
fig6.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], wtbl_selfcal['dr_post'][b3sc], **b3style)
ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], wtbl_selfcal['dr_post'][b6sc], **b6style)
#ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Dynamic Range (self-calibrated)")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3sc], wtbl_selfcal['dr_post'][b3sc], **b3style, label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6sc], wtbl_selfcal['dr_post'][b6sc], **b6style, label='B6')
#ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Dynamic Range (self-calibrated)")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/dynamic_range.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/dynamic_range.png", bbox_inches='tight')





b3bs = wtbl_bsens['band'] == 'B3'
b6bs = wtbl_bsens['band'] == 'B6'

fig7 = pl.figure(7, figsize=(10,5))
fig7.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_bsens['sum_bsens'][b3bs]/wtbl_bsens['ppbeam'][b3bs], wtbl_bsens['SensVsReqPost'][b3bs], **b3style)
ax1.plot(wtbl_bsens['sum_bsens'][b6bs]/wtbl_bsens['ppbeam'][b6bs], wtbl_bsens['SensVsReqPost'][b6bs], **b6style)
w51e_sel_bsens = (wtbl_bsens['region'] == 'W51-E')
if (b3bs & w51e_sel_bsens).sum() > 0:
    ax1.annotate('W51-E', (wtbl_bsens['sum_bsens'][b3bs & w51e_sel_bsens]/wtbl_bsens['ppbeam'][b3bs & w51e_sel_bsens],
                           wtbl_bsens['SensVsReqPost'][b3bs & w51e_sel_bsens]))
w51irs2_sel_bsens = (wtbl_bsens['region'] == 'W51-IRS2')
if (b3bs & w51irs2_sel_bsens).sum() > 0:
    ax1.annotate('W51-IRS2', (wtbl_bsens['sum_bsens'][b3bs & w51irs2_sel_bsens]/wtbl_bsens['ppbeam'][b3bs & w51irs2_sel_bsens],
                              wtbl_bsens['SensVsReqPost'][b3bs & w51irs2_sel_bsens]))
else:
    print("W51 IRS2 B3 is missing")
#ax1.annotate('G010.62', (wtbl_bsens['sum_bsens'][b3bs & (wtbl_bsens['region'] == 'G010.62')]/wtbl_bsens['ppbeam'][b3bs & (wtbl_bsens['region'] == 'G010.62')],
#                         wtbl_bsens['SensVsReqPost'][b3bs & (wtbl_bsens['region'] == 'G010.62')]))
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Measured Noise / Requested Sensitivity")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_bsens'][b3bs], wtbl_bsens['SensVsReqPost'][b3bs], **b3style, label='B3')
ax2.plot(wtbl_bsens['max_bsens'][b6bs], wtbl_bsens['SensVsReqPost'][b6bs], **b6style, label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
if (b3bs & w51e_sel_bsens).sum() > 0:
    ax2.annotate('W51-E', (wtbl_bsens['max_bsens'][b3bs & w51e_sel_bsens], wtbl_bsens['SensVsReqPost'][b3bs & w51e_sel_bsens]))
if (b3bs & w51irs2_sel_bsens).sum() > 0:
    ax2.annotate('W51-IRS2', (wtbl_bsens['max_bsens'][b3bs & w51irs2_sel_bsens], wtbl_bsens['SensVsReqPost'][b3bs & w51irs2_sel_bsens]))
if (b6bs & w51irs2_sel_bsens).sum() > 0:
    ax2.annotate('W51-IRS2', (wtbl_bsens['max_bsens'][b6bs & w51irs2_sel_bsens], wtbl_bsens['SensVsReqPost'][b6bs & w51irs2_sel_bsens]))
else:
    print("W51 IRS2 B6 is missing!")
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Measured Noise / Requested Sensitivity")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/noise_excess_bsens.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess_bsens.png", bbox_inches='tight')




fig8 = pl.figure(8, figsize=(10,5))
fig8.clf()
ax1 = pl.subplot(1,2,1)
bins_b3 = np.linspace(0.45, 4.5, 10)

for tb,msk in ((wtbl_bsens, b3bs,), (wtbl_selfcal, b3sc)):
    if any(tb['SensVsReqPost'][msk] < bins_b3.min()) or any(tb['SensVsReqPost'][msk] > bins_b3.max()):
        raise ValueError("bad binning b3")

ax1.hist(wtbl_bsens['SensVsReqPost'][b3bs], bins=bins_b3, alpha=0.5)
ax1.hist(wtbl_selfcal['SensVsReqPost'][b3sc], bins=bins_b3, alpha=0.5)
ax1.set_xlabel("Measured Noise / Requested Sensitivity")
ax1.set_title("B3")

bins_b6 = np.linspace(0.45, 2, 10)
for tb,msk in ((wtbl_bsens, b3bs,), (wtbl_selfcal, b3sc)):
    if any(tb['SensVsReqPost'][msk] < bins_b3.min()) or any(tb['SensVsReqPost'][msk] > bins_b3.max()):
        raise ValueError("bad binning b3")

ax2 = pl.subplot(1,2,2)
ax2.hist(wtbl_bsens['SensVsReqPost'][b6bs], bins=bins_b6, alpha=0.5, label='BSENS')
ax2.hist(wtbl_selfcal['SensVsReqPost'][b6sc], bins=bins_b6, alpha=0.5, label='Cleanest')
ax2.set_xlabel("Measured Noise / Requested Sensitivity")
ax2.set_title("B6")
pl.legend(loc='best')


pl.savefig("../datapaper/figures/noise_excess_bsens_vs_selfcal.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess_bsens_vs_selfcal.png", bbox_inches='tight')



