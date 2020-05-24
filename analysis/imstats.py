import numpy as np
import warnings
import json
from astropy.table import Table,Column
from astropy import units as u
from astropy import wcs
from astropy.io import fits
from astropy.stats import mad_std
from radio_beam import Beam
import regions
import os
import glob


def get_requested_sens():
    # use this file's path
    requested_fn = os.path.join(os.path.dirname(__file__), 'requested.txt')
    from astropy.io import ascii
    tbl = ascii.read(requested_fn, data_start=2)
    return tbl

def imstats(fn, reg=None):
    fh = fits.open(fn)

    bm = Beam.from_fits_header(fh[0].header)

    data = fh[0].data

    mad = mad_std(data, ignore_nan=True)
    peak = np.nanmax(data)
    imsum = np.nansum(data)

    ww = wcs.WCS(fh[0].header)
    pixscale = wcs.utils.proj_plane_pixel_area(ww)*u.deg**2
    ppbeam = (bm.sr / pixscale).decompose()
    assert ppbeam.unit.is_equivalent(u.dimensionless_unscaled)
    ppbeam = ppbeam.value


    meta = {'beam': bm.to_header_keywords(),
            'bmaj': bm.major.to(u.arcsec).value,
            'bmin': bm.minor.to(u.arcsec).value,
            'bpa': bm.pa.value,
            'mad': mad,
            'peak': peak,
            'peak/mad': peak / mad,
            'ppbeam': ppbeam,
            'sum': imsum,
            'fluxsum': imsum / ppbeam,
           }

    if reg is not None:
        reglist = regions.read_ds9(reg)
        data = fh[0].data.squeeze()
        fullmask = np.zeros(data.shape, dtype='bool')
        for reg in reglist:

            preg = reg.to_pixel(ww.celestial)
            msk = preg.to_mask()
            mimg = msk.to_reg()
            fullmask |= mimg

        meta['mad_sample'] = mad_std(data[fullmask], ignore_nan=True)
        meta['std_sample'] = np.nanstd(data[fullmask])

    return meta

def parse_fn(fn):

    basename = os.path.basename(fn)

    split = basename.split("_")

    selfcal_entry = 'selfcal0'
    for entry in split:
        if 'selfcal' in entry and 'pre' not in entry:
            selfcal_entry = entry

    robust_entry = 'robust999'
    for entry in split:
        if 'robust' in entry:
            robust_entry = entry


    if selfcal_entry == 'postselfcal':
        selfcaliter = 'Last'
    else:
        selfcaliter = int(selfcal_entry.split('selfcal')[-1])
    robust = float(robust_entry.split('robust')[-1])

    return {'region': split[0],
            'band': split[1],
            'array': '12Monly' if '12M' in split else '7M12M' if '7M12M' in split else '????',
            'selfcaliter': 'sc'+str(selfcaliter),
            'robust': 'r'+str(robust),
            'suffix': split[-1],
            'bsens': 'bsens' in fn.lower(),
            'pbcor': 'pbcor' in fn.lower(),
           }

def assemble_stats(globstr, ditch_suffix=None):
    import glob
    from astropy.utils.console import ProgressBar

    allstats = []

    for fn in ProgressBar(glob.glob(globstr)):
        if fn.endswith('diff.fits'):
            continue
        if fn.count('.fits') > 1:
            # these are diff images, or something like that
            continue
        if ditch_suffix is not None:
            meta = parse_fn(fn.split(ditch_suffix)[0])
            # don't do this on the suffix-ditched version
            meta['pbcor'] = 'pbcor' in fn.lower()
        else:
            meta = parse_fn(fn)
        meta['filename'] = fn
        stats = imstats(fn, reg=get_noise_region(meta['region'], meta['band']))
        allstats.append({'meta': meta, 'stats': stats})

    return allstats


def get_noise_region(field, band):
    basepath = os.path.dirname(__file__)
    noisepath = os.path.join(basepath, 'noise_estimation_regions')
    assert os.path.exists(noisepath)

    regfn = f"{noisepath}/{field}_{band}_noise_sampling.reg"

    if os.path.exists(regfn):
        return regfn


class MyEncoder(json.JSONEncoder):
    "https://stackoverflow.com/a/27050186/814354"
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

def make_quicklook_analysis_form(filename, metadata, savepath, prev, next_,
                                 base_form_url="https://docs.google.com/forms/d/e/1FAIpQLSczsBdB3Am4znOio2Ky5GZqAnRYDrYTD704gspNu7fAMm2-NQ/viewform?embedded=true"):

    if '1FAIpQLSc3QnQWNDl97B8XeTFRNMWRqU5rlxNPqIC2i1jMr5nAjcHDug' in base_form_url:
        #entry.868884739: reviwername
        #entry.1301985958: comment
        #entry.457220938.other_option_response: goodenoughforrelease
        #entry.457220938: __other_option__
        #entry.639517087: field
        #entry.400258516: 3
        #entry.841871158: selfcaliter
        #entry.312922422: 12M
        #entry.678487127: -2
        #fvv: 1
        #draftResponse: [null,null,"6280405489446951000"]
        #pageHistory: 0
        #fbzx: 6280405489446951000
        form_url_dict = {#"868884739":"{reviewer}",
                         "639517087": "{field}",
                         "400258516": "{band}",
                         "841871158": "{selfcal}" if isinstance(metadata['selfcal'], int) else "preselfcal",
                         "312922422": "{array}",
                         "678487127": "{robust}",
                         #"1301985958": "{comment}",
                        }
    elif '1FAIpQLSczsBdB3Am4znOio2Ky5GZqAnRYDrYTD704gspNu7fAMm2' in base_form_url:
        form_url_dict = {#"868884739":"{reviewer}",
                         "639517087": "{field}",
                         "400258516": "{band}",
                         "841871158": "{selfcal}" if isinstance(metadata['selfcal'], int) else "preselfcal",
                         "312922422": "{array}",
                         "678487127": "{robust}",
                         #"1301985958": "{comment}",
                        }
    form_url = base_form_url + "".join(f'&entry.{key}={value}' for key,value in form_url_dict.items())

    template = """
    <html>
    <body onbeforeunload="document.write('unloading...')" beforeunload=null>
    <center>
        <div> {filename} </div>
        <img src="{filename}" style="width: 100%;" border=0>
    </center>
    <iframe id=frame name=frame sandbox="allow-scripts allow-forms
        allow-pointer-lock allow-same-origin" src="{form_url}" width="1200"
        height="1326" frameborder="0" marginheight="0"
        marginwidth="0">Loading…</iframe>
    </body>
    <script type="text/javascript">
    window.onbeforeunload="document.write('unloading...')";
    window.beforeunload=null;
    </script>
    Previous: <a href="{prev}">{prev}</a> |
    Next: <a href="{next_}">{next_}</a>
    <script type="text/javascript">
    let params = new URLSearchParams(location.search);
    var name = params.get('name');
    if (name) {{{{document.getElementById('frame').src = document.getElementById('frame').src + "&entry.868884739=" + name;}}}}
    </script>
    </html>
    """

    with open(f'{savepath}/{filename}.html', 'w') as fh:
        fh.write(template
                 .format(form_url=form_url, filename=filename+".png",
                         prev=prev, next_=next_)
                 .format(**metadata)
                )


def get_selfcal_number(fn):
    numberstring = fn.split("selfcal")[1][0]
    try:
        return int(numberstring)
    except:
        return 0

def make_analysis_forms(basepath="/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/",
                        base_form_url="https://docs.google.com/forms/d/e/1FAIpQLSczsBdB3Am4znOio2Ky5GZqAnRYDrYTD704gspNu7fAMm2-NQ/viewform?embedded=true",
                        dontskip_noresid=False
                       ):
    import glob
    from diagnostic_images import load_images, show as show_images
    from astropy import visualization
    import pylab as pl

    savepath = f'{basepath}/quicklooks'

    try:
        os.mkdir(savepath)
    except:
        pass



    filedict = {(field, band, config, robust, selfcal):
        glob.glob(f"{field}/B{band}/{imtype}{field}*_B{band}_*_{config}_robust{robust}*selfcal{selfcal}*.image.tt0*.fits")
                for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split()
                for band in (3,6)
                #for config in ('7M12M', '12M')
                for config in ('12M',)
                #for robust in (-2, 0, 2)
                for robust in (0,)
                for selfcal in ("",) + tuple(range(0,9))
                for imtype in (('',) if 'October31' in basepath else ('cleanest/', 'bsens/'))
               }
    badfiledict = {key: val for key, val in filedict.items() if len(val) == 1}
    print(f"Bad files: {badfiledict}")
    filedict = {key: val for key, val in filedict.items() if len(val) > 1}
    filelist = [key + (fn,) for key, val in filedict.items() for fn in val]

    prev = 'index.html'

    flist = []

    #for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split():
    ##for field in ("G333.60",):
    #    for band in (3,6):
    #        for config in ('7M12M', '12M'):
    #            for robust in (-2, 0, 2):

    #                # for not all-in-the-same-place stuff
    #                fns = [x for x in glob.glob(f"{field}/B{band}/{field}*_B{band}_*_{config}_robust{robust}*selfcal[0-9]*.image.tt0*.fits") ]

    #                for fn in fns:
    for ii,(field, band, config, robust, selfcal, fn) in enumerate(filelist):

        image = fn
        basename,suffix = image.split(".image.tt0")
        if 'diff' in suffix:
            continue
        outname = basename.split("/")[-1]

        if prev == outname+".html":
            print(f"{ii}: {(field, band, config, robust, fn)} yielded the same prev "
                  f"{prev} as last time, skipping.")
            continue


        jj = 1
        while jj < len(filelist):
            if ii+jj < len(filelist):
                next_ = filelist[ii+jj][5].split(".image.tt0")[0].split("/")[-1]+".html"
            else:
                next_ = "index.html"

            if next_ == outname+".html":
                jj = jj + 1
            else:
                break

        assert next_ != outname+".html"

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                print(f"{ii}: {(field, band, config, robust, fn, selfcal)}"
                      f" basename='{basename}', suffix='{suffix}'")
                imgs, cubes = load_images(basename, suffix=suffix)
        except KeyError as ex:
            print(ex)
            raise
        except Exception as ex:
            print(f"EXCEPTION: {type(ex)}: {str(ex)}")
            raise
            continue
        norm = visualization.ImageNormalize(stretch=visualization.AsinhStretch(),
                                            interval=visualization.PercentileInterval(99.95))
        # set the scaling based on one of these...
        # (this call inplace-modifies logn, according to the docs)
        if 'residual' in imgs:
            norm(imgs['residual'][imgs['residual'] == imgs['residual']])
            imnames_toplot = ('mask', 'model', 'image', 'residual')
        elif 'image' in imgs and dontskip_noresid:
            imnames_toplot = ('image', 'mask',)
            norm(imgs['image'][imgs['image'] == imgs['image']])
        else:
            print(f"Skipped {fn} because no image OR residual was found.  imgs.keys={imgs.keys()}")
            continue
        pl.close(1)
        pl.figure(1, figsize=(14,6))
        show_images(imgs, norm=norm, imnames_toplot=imnames_toplot)

        pl.savefig(f"{savepath}/{outname}.png",
                   dpi=150,
                   bbox_inches='tight')

        metadata = {'field': field,
                    'band': band,
                    'selfcal': selfcal, #get_selfcal_number(basename),
                    'array': config,
                    'robust': robust,
                    'finaliter': 'finaliter' in fn,
                   }
        make_quicklook_analysis_form(filename=outname,
                                     metadata=metadata,
                                     savepath=savepath,
                                     prev=prev,
                                     next_=next_,
                                     base_form_url=base_form_url
                                    )
        metadata['outname'] = outname
        metadata['suffix'] = suffix
        if robust == 0:
            # only keep robust=0 for simplicity
            flist.append(metadata)
        prev = outname+".html"


    #make_rand_html(savepath)
    make_index(savepath, flist)

    return flist

def make_index(savepath, flist):
    css = """
    .right {
    width: 80%;
    float: right;
}

.left {
    float: left;
    /* the next props are meant to keep this block independent from the other floated one */
    width: auto;
    overflow: hidden;
}
"""
    js = """
      <script>

      let params = new URLSearchParams(location.search);
      var name = params.get('name');

      function changeSrc(loc) {
          if (name) {
              document.getElementById('iframe').src = loc + "?name=" + name;
          } else {
              document.getElementById('iframe').src = loc;
          }
      }
      </script>"""
    with open(f"{savepath}/index.html", "w") as fh:
        fh.write("<html>\n")
        fh.write(f'<style type="text/css">{css}</style>\n')
        fh.write(f"{js}\n")
        fh.write("<div class='left' style='max-width:20%'>\n")
        fh.write("<ul>\n")
        for metadata in flist:
            filename = metadata['outname']+".html"
            meta_str = (f"{metadata['field']}_{metadata['band']}" +
                        (f"_selfcal{metadata['selfcal']}"
                         if isinstance(metadata['selfcal'], int) else
                         "_preselfcal") +
                        f"_{metadata['array']}_robust{metadata['robust']} "
                        f"{' finaliter' if metadata['finaliter'] else ''}"
                        f"{metadata['suffix']}")
            #fh.write(f'<li><a href="{filename}">{meta_str}</a></li>\n')
            fh.write(f"<li><button onclick=\"changeSrc('{filename}')\">{meta_str}</a></li>\n")
        fh.write("</ul>\n")
        fh.write("</div>\n")
        fh.write("<div class='right' style='width:80%'>\n")
        fh.write("<iframe name=iframe id=iframe src='' width='100%' height='100%'></iframe>\n")
        fh.write("</div>\n")
        fh.write("</html>\n")

def make_rand_html(savepath):
    randform_template = """
<html>
<script src="//code.jquery.com/jquery-1.10.2.js"></script>

<script type="text/javascript">
function random_form(){{
    var myimages=new Array()
    {randarr_defs}
    var ry=Math.floor(Math.random()*myimages.length);
    while (myimages[ry] == undefined) {{
        var ry=Math.floor(Math.random()*myimages.length);
    }}

}}

var loadNewContent = function {
  $.ajax(random_form(), {
    success: function(response) {

        $("#content2").html(response);


    }
  }); };

var reader = new FileReader();
var newdocument = reader.readAsText(random_form(), "UTF-16");

document.write(newdocument)

</script>
</html>
"""
    forms = glob.glob(f"{savepath}/*html")

    randarr_defs = "\n".join([f"myimages[{ii}]='{fn}'" for ii, fn in
                              enumerate(forms)])

    with open(f"{savepath}/index.html", "w") as fh:
        fh.write(randform_template.format(randarr_defs=randarr_defs,))



def savestats(basepath="/bio/web/secure/adamginsburg/ALMA-IMF/October31Release"):
    if 'October' in basepath:
        stats = assemble_stats(f"{basepath}/*/*/*_12M_*.image.tt0*.fits", ditch_suffix=".image.tt")
    else:
        # extra layer: bsens, cleanest, etc
        stats = assemble_stats(f"{basepath}/*/*/*/*_12M_*.image.tt0*.fits", ditch_suffix=".image.tt")
    with open(f'{basepath}/tables/metadata.json', 'w') as fh:
        json.dump(stats, fh, cls=MyEncoder)

    requested = get_requested_sens()

    meta_keys = ['region', 'band', 'array', 'selfcaliter', 'robust', 'suffix',
                 'bsens', 'pbcor', 'filename']
    stats_keys = ['bmaj', 'bmin', 'bpa', 'peak', 'mad', 'peak/mad']
    req_keys = ['B3_res', 'B3_sens', 'B6_res', 'B6_sens']
    req_keys_head = ['Req_Res', 'Req_Sens']

    rows = []
    for entry in stats:
        band = entry['meta']['band']
        requested_this = requested[requested['Field'] == entry['meta']['region']]
        if len(requested_this) == 0:
            print(f"Skipped {entry['meta']['region']}")
            continue
        rows += [[entry['meta'][key] for key in meta_keys] +
                 [entry['stats'][key] for key in stats_keys] +
                 [requested_this[key][0] for key in req_keys if band in key]
                ]

    tbl = Table(rows=rows, names=meta_keys+stats_keys+req_keys_head)

    # do some QA
    tbl.add_column(Column(name='SensVsReq', data=tbl['mad']*1e3/tbl['Req_Sens']))
    tbl.add_column(Column(name='BeamVsReq', data=(tbl['bmaj']*tbl['bmin'])**0.5/tbl['Req_Res']))

    tbl.write(f'{basepath}/tables/metadata.ecsv', overwrite=True)
    tbl.write(f'{basepath}/tables/metadata.html',
              format='ascii.html', overwrite=True)
    tbl.write(f'{basepath}/tables/metadata.tex', overwrite=True)
    tbl.write(f'{basepath}/tables/metadata.js.html',
              format='jsviewer')

    return tbl

if __name__ == "__main__":
    import socket
    cwd = os.getcwd()
    if 'ufhpc' in socket.gethostname():
        for basepath,formid in (
                ("/bio/web/secure/adamginsburg/ALMA-IMF/May2020/",
                 "1FAIpQLSc3QnQWNDl97B8XeTFRNMWRqU5rlxNPqIC2i1jMr5nAjcHDug"),
                ("/bio/web/secure/adamginsburg/ALMA-IMF/Feb2020/",
                 "1FAIpQLSc3QnQWNDl97B8XeTFRNMWRqU5rlxNPqIC2i1jMr5nAjcHDug"),
               #("/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/", "1FAIpQLSczsBdB3Am4znOio2Ky5GZqAnRYDrYTD704gspNu7fAMm2-NQ")
               ):

            os.chdir(basepath)
            base_form_url=f"https://docs.google.com/forms/d/e/{formid}/viewform?embedded=true"
            flist = make_analysis_forms(basepath=basepath, base_form_url=base_form_url, dontskip_noresid='May2020' in basepath)
            # done a million times elsewhere? tbl = savestats(basepath=basepath)
    os.chdir(cwd)
