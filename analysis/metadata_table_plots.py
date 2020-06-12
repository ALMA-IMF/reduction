import numpy as np
from astropy.table import Table

tbl_selfcal = Table.read('metadata_sc.ecsv')
bad = np.array(['diff' in x for x in tbl_selfcal['filename']])
keep_selfcal = (tbl_selfcal['suffix'] == 'finaliter') & (tbl_selfcal['robust'] == 'r0.0') & (~tbl_selfcal['pbcor']) & (~tbl_selfcal['bsens']) & (~bad)
wtbl_selfcal = tbl_selfcal[keep_selfcal]

tbl_bsens = Table.read('metadata_bsens_cleanest.ecsv')
bad = np.array(['diff' in x for x in tbl_bsens['filename']])
keep_bsens = (tbl_bsens['suffix'] == 'finaliter') & (tbl_bsens['robust'] == 'r0.0') & (~tbl_bsens['pbcor']) & (tbl_bsens['bsens']) & (~bad)
wtbl_bsens = tbl_bsens[keep_bsens]


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


fig3 = pl.figure(3, figsize=(10,5))
fig3.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_bsens['sum_cleanest'][b3]/wtbl_bsens['ppbeam'][b3], wtbl_bsens['mad_sample_bsens'][b3]/wtbl_bsens['mad_sample_cleanest'][b3], **b3style)
ax1.plot(wtbl_bsens['sum_cleanest'][b6]/wtbl_bsens['ppbeam'][b6], wtbl_bsens['mad_sample_bsens'][b6]/wtbl_bsens['mad_sample_cleanest'][b6], **b6style)
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum (cleanest) [Jy]")
ax1.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_cleanest'][b3], wtbl_bsens['mad_sample_bsens'][b3]/wtbl_bsens['mad_sample_cleanest'][b3], **b3style, label='B3')
ax2.plot(wtbl_bsens['max_cleanest'][b6], wtbl_bsens['mad_sample_bsens'][b6]/wtbl_bsens['mad_sample_cleanest'][b6], **b6style, label='B6')
#ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak (cleanest)")
ax2.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax2.add_patch(pl.Rectangle((-0.05,0.4), width=0.45, height=0.55, facecolor='r', alpha=0.25))
pl.legend(loc='best')

pl.savefig("../datapaper/figures/bsens_rms_change.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/bsens_rms_change.png", bbox_inches='tight')



b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'
wtbl_selfcal['SensVsReq'] = wtbl_selfcal['mad_sample_post'] / wtbl_selfcal['Req_Sens'] * 1000

fig1 = pl.figure(4, figsize=(10,5))
fig1.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], wtbl_selfcal['SensVsReq'][b3sc], **b3style)
ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], wtbl_selfcal['SensVsReq'][b6sc], **b6style)
ax1.annotate('W51-E', (wtbl_selfcal['sum_post'][b3sc & (wtbl_selfcal['region'] == 'W51-E')]/wtbl_selfcal['ppbeam'][b3sc & (wtbl_selfcal['region'] == 'W51-E')],
                       wtbl_selfcal['SensVsReq'][b3sc & (wtbl_selfcal['region'] == 'W51-E')]))
#ax1.annotate('W51-IRS2', (wtbl_selfcal['sum_post'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]/wtbl_selfcal['ppbeam'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')],
#                          wtbl_selfcal['SensVsReq'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
#ax1.annotate('G010.62', (wtbl_selfcal['sum_post'][b3sc & (wtbl_selfcal['region'] == 'G010.62')]/wtbl_selfcal['ppbeam'][b3sc & (wtbl_selfcal['region'] == 'G010.62')],
#                         wtbl_selfcal['SensVsReq'][b3sc & (wtbl_selfcal['region'] == 'G010.62')]))
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Sensitivity / Requested Sensitivity")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3sc], wtbl_selfcal['SensVsReq'][b3sc], **b3style, label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6sc], wtbl_selfcal['SensVsReq'][b6sc], **b6style, label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.annotate('W51-E', (wtbl_selfcal['max_post'][b3sc & (wtbl_selfcal['region'] == 'W51-E')], wtbl_selfcal['SensVsReq'][b3sc & (wtbl_selfcal['region'] == 'W51-E')]))
#ax2.annotate('W51-IRS2', (wtbl_selfcal['max_post'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')], wtbl_selfcal['SensVsReq'][b3sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
ax2.annotate('W51-IRS2', (wtbl_selfcal['max_post'][b6sc & (wtbl_selfcal['region'] == 'W51-IRS2')], wtbl_selfcal['SensVsReq'][b6sc & (wtbl_selfcal['region'] == 'W51-IRS2')]))
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Sensitivity / Requested Sensitivity")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/noise_excess.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess.png", bbox_inches='tight')




b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'

fig5 = pl.figure(5, figsize=(10,5))
fig5.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], 1./wtbl_selfcal['BeamVsReq'][b3sc], **b3style)
ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], 1./wtbl_selfcal['BeamVsReq'][b6sc], **b6style)
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3sc], 1./wtbl_selfcal['BeamVsReq'][b3sc], **b3style, label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6sc], 1./wtbl_selfcal['BeamVsReq'][b6sc], **b6style, label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Recovered Beam Major Axis / Requested beam major axis")
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
wtbl_bsens['SensVsReq'] = wtbl_bsens['mad_sample_bsens'] / wtbl_bsens['Req_Sens'] * 1000

fig7 = pl.figure(7, figsize=(10,5))
fig7.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_bsens['sum_bsens'][b3bs]/wtbl_bsens['ppbeam'][b3bs], wtbl_bsens['SensVsReq'][b3bs], **b3style)
ax1.plot(wtbl_bsens['sum_bsens'][b6bs]/wtbl_bsens['ppbeam'][b6bs], wtbl_bsens['SensVsReq'][b6bs], **b6style)
ax1.annotate('W51-E', (wtbl_bsens['sum_bsens'][b3bs & (wtbl_bsens['region'] == 'W51-E')]/wtbl_bsens['ppbeam'][b3bs & (wtbl_bsens['region'] == 'W51-E')],
                       wtbl_bsens['SensVsReq'][b3bs & (wtbl_bsens['region'] == 'W51-E')]))
ax1.annotate('W51-IRS2', (wtbl_bsens['sum_bsens'][b3bs & (wtbl_bsens['region'] == 'W51-IRS2')]/wtbl_bsens['ppbeam'][b3bs & (wtbl_bsens['region'] == 'W51-IRS2')],
                          wtbl_bsens['SensVsReq'][b3bs & (wtbl_bsens['region'] == 'W51-IRS2')]))
#ax1.annotate('G010.62', (wtbl_bsens['sum_bsens'][b3bs & (wtbl_bsens['region'] == 'G010.62')]/wtbl_bsens['ppbeam'][b3bs & (wtbl_bsens['region'] == 'G010.62')],
#                         wtbl_bsens['SensVsReq'][b3bs & (wtbl_bsens['region'] == 'G010.62')]))
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Sensitivity / Requested Sensitivity")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_bsens'][b3bs], wtbl_bsens['SensVsReq'][b3bs], **b3style, label='B3')
ax2.plot(wtbl_bsens['max_bsens'][b6bs], wtbl_bsens['SensVsReq'][b6bs], **b6style, label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.annotate('W51-E', (wtbl_bsens['max_bsens'][b3bs & (wtbl_bsens['region'] == 'W51-E')], wtbl_bsens['SensVsReq'][b3bs & (wtbl_bsens['region'] == 'W51-E')]))
ax2.annotate('W51-IRS2', (wtbl_bsens['max_bsens'][b3bs & (wtbl_bsens['region'] == 'W51-IRS2')], wtbl_bsens['SensVsReq'][b3bs & (wtbl_bsens['region'] == 'W51-IRS2')]))
ax2.annotate('W51-IRS2', (wtbl_bsens['max_bsens'][b6bs & (wtbl_bsens['region'] == 'W51-IRS2')], wtbl_bsens['SensVsReq'][b6bs & (wtbl_bsens['region'] == 'W51-IRS2')]))
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Sensitivity / Requested Sensitivity")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/noise_excess_bsens.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess_bsens.png", bbox_inches='tight')




fig8 = pl.figure(8, figsize=(10,5))
fig8.clf()
ax1 = pl.subplot(1,2,1)
ax1.hist(wtbl_bsens['SensVsReq'][b3bs], bins=np.linspace(0.45, 4.5, 10), alpha=0.5)
ax1.hist(wtbl_selfcal['SensVsReq'][b3sc], bins=np.linspace(0.45, 4.5, 10), alpha=0.5)
ax1.set_xlabel("Sensitivity / Requested Sensitivity")
ax1.set_title("B3")

ax2 = pl.subplot(1,2,2)
ax2.hist(wtbl_bsens['SensVsReq'][b6bs], bins=np.linspace(0.45, 2, 10), alpha=0.5, label='BSENS')
ax2.hist(wtbl_selfcal['SensVsReq'][b6sc], bins=np.linspace(0.6, 2, 10), alpha=0.5, label='Cleanest')
ax2.set_xlabel("Sensitivity / Requested Sensitivity")
ax2.set_title("B6")
pl.legend(loc='best')


pl.savefig("../datapaper/figures/noise_excess_bsens_vs_selfcal.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess_bsens_vs_selfcal.png", bbox_inches='tight')



