"""
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_spw[0-7].flatpb.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/pb/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_sio.flatpb.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/pb/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_spw[0-7].model.minimized.fits.gz /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/model/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_sio.model.minimized.fits.gz /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/model/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_spw[0-7].JvM.image.pbcor.statcont.contsub.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_sio.JvM.image.pbcor.statcont.contsub.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_spw[0-7].JvM.image.pbcor.statcont.cont.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/cont/
ln -v /orange/adamginsburg/ALMA_IMF/2017.1.01355.L/imaging_results/*spw[0-7]_12M_sio.JvM.image.pbcor.statcont.cont.fits /orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/cont/
"""
import os

import glob
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests
import json
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper


dataverse_server='https://dataverse.harvard.edu'

import subprocess
def java_upload_file(filename, api_key, persistentId):
    return subprocess.check_call(
        list(f"/apps/java/jdk-14/bin/java -jar /orange/adamginsburg/software/DVUploader-v1.1.0.jar -directupload -key={api_key} -did=doi:{persistentId} -server=https://dataverse.harvard.edu".split())
            + [filename])

# former dataset_id=6565108,
def upload_dataset(upload_filelist, dataset_id=None, persistentId=None, overwrite=False, n_retries=10):

    #if dataset_id is not None:
    #    url_dataset_id = '%s/api/datasets/%s/add?key=%s' % (dataverse_server, dataset_id, api_key)
    #    url_for_upload = url_dataset_id
    #else:
    url_persistent_id = '%s/api/datasets/:persistentId/add?persistentId=%s&key=%s' % (dataverse_server, persistentId, api_key)
    url_for_upload = url_persistent_id

    for ntries in range(n_retries):
        try:
            #if dataset_id is not None:
            #    url_list = f'{dataverse_server}/api/datasets/{dataset_id}/versions/:draft/files?key={api_key}'
            #elif persistentId is not None:
            url_list = f'{dataverse_server}/api/datasets/:persistentId/versions/:draft/files?key={api_key}&persistentId={persistentId}'
            filelist_resp = requests.get(url_list)
            file_metadata = filelist_resp.json()
            assert file_metadata['status'] == 'OK'
            filelist = [x['dataFile']['filename'] for x in file_metadata['data']]
            file_metadata_withkeys = {x['dataFile']['filename']: x['dataFile']['id'] for x in file_metadata['data']}
            print(f"Found {len(filelist)} files uploaded")

            for filename in upload_filelist:
                print(f"Working on filename {filename}")
                os.chdir(os.path.dirname(filename))
                filename = os.path.basename(filename)
                print(f"Working in {os.getcwd()} on file {filename}")

                # Reupload everything
                if overwrite:
                    if filename in filelist:
                        dataFile_id = file_metadata_withkeys[filename]
                        delete_url = f'{dataverse_server}/dvn/api/data-deposit/v1.1/swordv2/edit-media/file/{dataFile_id}'
                        response_delete = requests.delete(delete_url, auth=(api_key, ''), )
                        response_delete.raise_for_status()

                if filename not in filelist:
                    print(f"Uploading filename {filename}")

                    try:
                        field, band, spw, array, _ = filename.split("_")
                    except Exception as ex:
                        print(f"Skipping file {filename} because of {ex}")
                    params={'description': f'{field} {band} {spw} {array} full JvM corrected cube', }
                    params_as_json_string = json.dumps(params)
                    payload = dict(jsonData=params_as_json_string)

                    file_size = os.stat(filename).st_size
                    print(f'{filename} : {file_size}')
                    try:
                        with open(filename, "rb") as f:
                            with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
                                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                                #file_resp = requests.put('https://zenodo.org/api/deposit/depositions/7035006/files',  data=wrapped_file, params={'access_token': ACCESS_TOKEN}, )
                                payload.update({'file':(filename, wrapped_file, 'text/plain')})
                                data = MultipartEncoder(payload)
                                file_resp = requests.post(url_for_upload,
                                                          data=data,#payload,
                                                          #files=files,
                                                          headers={'Content-Type': data.content_type},
                                                          stream=True)
                                #rslt = requests.put(f'{upload_url}/{filename}', data=wrapped_file, params={'access_token': ACCESS_TOKEN}, )
                        #rslt.raise_for_status()
                        file_resp.raise_for_status()
                    except Exception as ex:
                        print(f"Exception for file {filename}: {ex}")
                        try:
                            result = java_upload_file(filename)
                            print(f"Result of java_upload_filename: {result}")
                        except Exception as ex:
                            print(f"JAVA Exception for file {filename}: {ex}")

        except Exception as ex:
            print(f'Exception: {ex}')
            raise


if __name__ == "__main__":
    with open(os.path.expanduser('~/.almaimf_dataverse_token'), 'r') as fh:
        api_key = token = fh.read().strip()

    print("Uploading models")
    models = glob.glob('/orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/model/*.model.minimized.fits.gz')
    models = [x for x in models if not any((y in x for y in ('12co', 'n2hp', 'h41a', '7M12M')))]
    upload_dataset(models, persistentId='doi:10.7910/DVN/YWW5BY', overwrite=False, n_retries=10)

    print("Uploading PBs")
    pbs = glob.glob('/orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/pb/*.flatpb.fits')
    pbs = [x for x in pbs if not any((y in x for y in ('12co', 'n2hp', 'h41a', '7M12M')))]
    upload_dataset(pbs, persistentId='doi:10.7910/DVN/RBS6KT', overwrite=False, n_retries=10)

    print("Uploading statconts")
    statconts = glob.glob('/orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/cont/*.JvM.image.pbcor.statcont.cont.fits')
    statconts = [x for x in statconts if not any((y in x for y in ('12co', 'n2hp', 'h41a', '7M12M')))]
    upload_dataset(statconts, persistentId='doi:10.7910/DVN/SF09HK', overwrite=False, n_retries=10)

    print("Uploading contsubbed cubes")
    jvm_statcont_pbcor = glob.glob('/orange/adamginsburg/ALMA_IMF/distributions/2023_May_JVM_contsub/*.JvM.image.pbcor.statcont.contsub.fits')
    jvm_statcont_pbcor = [x for x in jvm_statcont_pbcor if not any((y in x for y in ('12co', 'n2hp', 'h41a', '7M12M')))]
    upload_dataset(jvm_statcont_pbcor, persistentId='doi:10.7910/DVN/CJ3YXU', overwrite=False, n_retries=10)
