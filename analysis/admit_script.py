# set up admit in the casa environment
import admit
import os

project = os.getenv('PROJECT')
if project is None:
    raise ValueError
else:
    print(f"Project -> {project}")

basefn = os.path.basename(project).replace(".image","")
print(f"basefn = {basefn}")

p = admit.Project(f'{basefn}.admit', dataserver=True)
# Flow tasks.
t0  = p.addtask(admit.Ingest_AT(file=basefn+'.image'))
t1  = p.addtask(admit.CubeStats_AT(ppp=True), [t0])
t2  = p.addtask(admit.CubeSum_AT(numsigma=5.0, sigma=99.0), [t0, t1])
t3  = p.addtask(admit.CubeSpectrum_AT(), [t0, t2])
t4  = p.addtask(admit.LineSegment_AT(csub=[0, 0], minchan=4, maxgap=6, numsigma=5.0), [t1, t3])
t5 = p.addtask(admit.ContinuumSub_AT(fitorder=1, pad=60),[t0, t4])
t6 = p.addtask(admit.CubeStats_AT(ppp=True), [t5])
t7 = p.addtask(admit.CubeSpectrum_AT(), [t5, t6])
t8 = p.addtask(admit.Moment_AT(mom0clip=2.0, numsigma=[3.0]), [t5, t6])
t9 = p.addtask(admit.LineID_AT(csub=[0, 0], minchan=4, maxgap=6, numsigma=5.0), [t6, t7])
t10 = p.addtask(admit.LineCube_AT(pad=40), [t5, t9])
t11 = p.addtask(admit.Moment_AT(mom0clip=2.0, moments=[0, 1, 2]), [t10, t6])
t11 = p.addtask(admit.CubeSpectrum_AT(), [t10, t11])
p.run()

print(f"Done running ADMIT for {basefn} <-> {project}")
