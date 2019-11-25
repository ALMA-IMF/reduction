import numpy as np
import warnings
import json
from astropy.table import Table,Column
from astropy import units as u
from astropy.io import fits
from astropy.stats import mad_std
from radio_beam import Beam
import os
import glob


def get_requested_sens():
    # use this file's path
    requested_fn = os.path.join(os.path.dirname(__file__), 'requested.txt')
    from astropy.io import ascii
    tbl = ascii.read(requested_fn, data_start=2)
    return tbl

def imstats(fn):
    fh = fits.open(fn)

    bm = Beam.from_fits_header(fh[0].header)

    data = fh[0].data

    mad = mad_std(data, ignore_nan=True)
    peak = np.nanmax(data)

    return {'beam': bm.to_header_keywords(),
            'mad': mad,
            'peak': peak,
            'peak/mad': peak/mad,
           }

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
        if ditch_suffix is not None:
            meta = parse_fn(fn.split(ditch_suffix)[0])
        else:
            meta = parse_fn(fn)
        stats = imstats(fn)
        allstats.append({'meta': meta, 'stats': stats})

    return allstats

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

def make_quicklook_analysis_form(filename, metadata, savepath, prev, next_):
    base_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSczsBdB3Am4znOio2Ky5GZqAnRYDrYTD704gspNu7fAMm2-NQ/viewform?embedded=true"
    form_url_dict = {#"868884739":"{reviewer}",
                     "639517087": "{field}",
                     "400258516": "{band}",
                     "841871158": "{selfcal}",
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

def make_analysis_forms(savepath="/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/quicklooks/"):
    import glob
    from diagnostic_images import load_images, show as show_images
    from astropy import visualization
    import pylab as pl

    try:
        os.mkdir(savepath)
    except:
        pass


    filedict = {(field, band, config, robust, selfcal):
        glob.glob(f"{field}/B{band}/{field}*_B{band}_*_{config}_robust{robust}*selfcal{selfcal}*.image.tt0*.fits")
                for field in "G008.67 G337.92 W43-MM3 G328.25 G351.77 G012.80 G327.29 W43-MM1 G010.62 W51-IRS2 W43-MM2 G333.60 G338.93 W51-E G353.41".split()
                for band in (3,6)
                for config in ('7M12M', '12M')
                for robust in (-2, 0, 2)
                for selfcal in range(0,8)
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
                print(f"{ii}: {(field, band, config, robust, fn)}"
                      f" basename='{basename}', suffix='{suffix}'")
                imgs, cubes = load_images(basename, suffix=suffix)
        except KeyError as ex:
            print(ex)
            raise
        except Exception as ex:
            print(f"EXCEPTION: {type(ex)}: {str(ex)}")
            continue
        logn = visualization.ImageNormalize(stretch=visualization.LogStretch())
        pl.close(1)
        pl.figure(1, figsize=(14,6))
        show_images(imgs, norm=logn)

        pl.savefig(f"{savepath}/{outname}.png",
                   bbox_inches='tight')

        metadata = {'field': field,
                    'band': band,
                    'selfcal': selfcal, #get_selfcal_number(basename),
                    'array': config,
                    'robust': robust,
                   }
        make_quicklook_analysis_form(filename=outname,
                                     metadata=metadata,
                                     savepath=savepath,
                                     prev=prev,
                                     next_=next_,
                                    )
        metadata['outname'] = outname
        metadata['suffix'] = suffix
        flist.append(metadata)
        prev = outname+".html"


    #make_rand_html(savepath)
    make_index(savepath, flist)

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
            meta_str = (f"{metadata['field']}_{metadata['band']}"
                        f"_selfcal{metadata['selfcal']}"
                        f"_{metadata['array']}_robust{metadata['robust']} "
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



def savestats():
    stats = assemble_stats("/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/*/*/*.image.tt0*.fits", ditch_suffix=".image.tt")
    with open('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.json', 'w') as fh:
        json.dump(stats, fh, cls=MyEncoder)

    requested = get_requested_sens()

    meta_keys = ['region', 'band', 'array', 'selfcaliter', 'robust', 'suffix', 'pbcor']
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

    tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.ecsv', overwrite=True)
    tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.html',
              format='ascii.html', overwrite=True)
    tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.tex')
    tbl.write('/bio/web/secure/adamginsburg/ALMA-IMF/October31Release/metadata.js.html',
              format='jsviewer')

    return tbl

if __name__ == "__main__":
    import socket
    if 'ufhpc' in socket.gethostname():
        tbl = savestats()
        make_analysis_forms()
