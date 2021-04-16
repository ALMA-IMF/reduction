import requests
import os
from bs4 import BeautifulSoup
import tqdm


def download_file(url, chunk_size=8192):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        len = int(r.headers['Content-Length'])

        with tqdm.tqdm(total=len) as pb:

            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
                    pb.update(chunk_size)
    return local_filename
            
if __name__ == "__main__":
    url = 'https://almascience.eso.org/arcdistribution/8c51c0f5e5ab90f5cec05460e5c59af1/'
    response = requests.get(url)
    html = BeautifulSoup(response.text)

    print("Found these files to download:")
    for thing in html.findAll('a'):
        nurl = f'{url}/{thing.attrs["href"]}'
        if 'tar' in nurl:
            fn = url.split("/")[-1]
            print(nurl)

    print()
    print("Downloading: ")
    for thing in html.findAll('a'):
        nurl = f'{url}/{thing.attrs["href"]}'
        if 'tar' in nurl:
            fn = nurl.split("/")[-1]
            if not os.path.exists(fn):
                print(nurl, fn)
                download_file(nurl)
