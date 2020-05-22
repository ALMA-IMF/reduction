import numpy as np
from astropy.table import Table

tbl_selfcal = Table.read('metadata_sc.ecsv')
keep_selfcal = (tbl_selfcal['suffix'] == 'finaliter') & (tbl_selfcal['robust'] == 'r0.0') & (tbl_selfcal['pbcor']) & (~tbl_selfcal['bsens'])
wtbl_selfcal = tbl_selfcal[keep_selfcal]

tbl_bsens = Table.read('metadata_bsens_cleanest.ecsv')
keep_bsens = (tbl_bsens['suffix'] == 'finaliter') & (tbl_bsens['robust'] == 'r0.0') & (tbl_bsens['pbcor']) & (tbl_bsens['bsens'])
wtbl_bsens = tbl_bsens[keep_bsens]


import pylab as pl

b3 = wtbl_selfcal['band'] == 'B3'
b6 = wtbl_selfcal['band'] == 'B6'

fig1 = pl.figure(1, figsize=(10,5))
fig1.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3]/wtbl_selfcal['ppbeam'][b3], wtbl_selfcal['dr_improvement'][b3], 'x')
ax1.plot(wtbl_selfcal['sum_post'][b6]/wtbl_selfcal['ppbeam'][b6], wtbl_selfcal['dr_improvement'][b6], '+')
ax1.plot(np.linspace(0, 50), np.linspace(0, 50)*0.45/50 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Dynamic Range Improvement")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3], wtbl_selfcal['dr_improvement'][b3], 'x', label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6], wtbl_selfcal['dr_improvement'][b6], '+', label='B6')
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
ax1.plot(wtbl_bsens['sum_cleanest'][b3]/wtbl_bsens['ppbeam'][b3], wtbl_bsens['sum_bsens'][b3]/wtbl_bsens['sum_cleanest'][b3], 'x')
ax1.plot(wtbl_bsens['sum_cleanest'][b6]/wtbl_bsens['ppbeam'][b6], wtbl_bsens['sum_bsens'][b6]/wtbl_bsens['sum_cleanest'][b6], '+')
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum (cleanest) [Jy]")
ax1.set_ylabel("Sum (bsens) / Sum (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_cleanest'][b3], wtbl_bsens['max_bsens'][b3]/wtbl_bsens['max_cleanest'][b3], 'x', label='B3')
ax2.plot(wtbl_bsens['max_cleanest'][b6], wtbl_bsens['max_bsens'][b6]/wtbl_bsens['max_cleanest'][b6], '+', label='B6')
#ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak (cleanest)")
ax2.set_ylabel("Peak (bsens) / Peak (cleanest)")
#ax2.add_patch(pl.Rectangle((-0.05,0.4), width=0.45, height=0.55, facecolor='r', alpha=0.25))
pl.legend(loc='best')

pl.savefig("../datapaper/figures/bsens_flux_change.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/bsens_flux_change.png", bbox_inches='tight')




fig3 = pl.figure(3, figsize=(10,5))
fig3.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_bsens['sum_cleanest'][b3]/wtbl_bsens['ppbeam'][b3], wtbl_bsens['mad_bsens'][b3]/wtbl_bsens['mad_cleanest'][b3], 'x')
ax1.plot(wtbl_bsens['sum_cleanest'][b6]/wtbl_bsens['ppbeam'][b6], wtbl_bsens['mad_bsens'][b6]/wtbl_bsens['mad_cleanest'][b6], '+')
#ax1.plot(np.linspace(0, 3000), np.linspace(0, 3000)*0.45/3000 + 1, 'k--', zorder=-5, alpha=0.5)
ax1.set_xlabel("Sum (cleanest) [Jy]")
ax1.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax1.add_patch(pl.Rectangle((-0.05,0.2), width=26, height=0.7, facecolor='r', alpha=0.25))

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_bsens['max_cleanest'][b3], wtbl_bsens['mad_bsens'][b3]/wtbl_bsens['mad_cleanest'][b3], 'x', label='B3')
ax2.plot(wtbl_bsens['max_cleanest'][b6], wtbl_bsens['mad_bsens'][b6]/wtbl_bsens['mad_cleanest'][b6], '+', label='B6')
#ax2.plot(np.linspace(0, 1), np.linspace(0, 1)*0.17 + 1, 'k--', zorder=-5, alpha=0.5)
ax2.set_xlabel("Peak (cleanest)")
ax2.set_ylabel("MAD (bsens) / MAD (cleanest)")
#ax2.add_patch(pl.Rectangle((-0.05,0.4), width=0.45, height=0.55, facecolor='r', alpha=0.25))
pl.legend(loc='best')

pl.savefig("../datapaper/figures/bsens_rms_change.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/bsens_rms_change.png", bbox_inches='tight')



b3sc = wtbl_selfcal['band'] == 'B3'
b6sc = wtbl_selfcal['band'] == 'B6'

fig1 = pl.figure(4, figsize=(10,5))
fig1.clf()
ax1 = pl.subplot(1,2,1)
ax1.plot(wtbl_selfcal['sum_post'][b3sc]/wtbl_selfcal['ppbeam'][b3sc], wtbl_selfcal['SensVsReq'][b3sc], 'x')
ax1.plot(wtbl_selfcal['sum_post'][b6sc]/wtbl_selfcal['ppbeam'][b6sc], wtbl_selfcal['SensVsReq'][b6sc], '+')
ax1.plot(ax1.get_xlim(), [1,1], 'k--')
ax1.set_xlabel("Sum [Jy]")
ax1.set_ylabel("Sensitivity / Requested Sensitivity")

ax2 = pl.subplot(1,2,2)
ax2.plot(wtbl_selfcal['max_post'][b3sc], wtbl_selfcal['SensVsReq'][b3sc], 'x', label='B3')
ax2.plot(wtbl_selfcal['max_post'][b6sc], wtbl_selfcal['SensVsReq'][b6sc], '+', label='B6')
ax2.plot(ax2.get_xlim(), [1,1], 'k--')
ax2.set_xlabel("Peak [Jy beam$^{-1}$]")
ax2.set_ylabel("Sensitivity / Requested Sensitivity")
pl.legend(loc='best')

pl.savefig("../datapaper/figures/noise_excess.pdf", bbox_inches='tight')
pl.savefig("../datapaper/figures/noise_excess.png", bbox_inches='tight')
