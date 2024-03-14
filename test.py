import uuid
from instagrapi import Client


def instaDownloader(link):
    filename_uuid = str(uuid.uuid4()) + ".mp4"

    cl = Client()

    res = cl.login("user", "pass")
    
    if not res:
        print("Login failed")
        return
    
    pk = cl.media_pk_from_url(link)
    print(pk)
    print('downloading...')
    f = cl.clip_download(pk)#3322589480392006929
    print('downloaded')
    
    print(f)



link = "https://www.instagram.com/reel/C4cNYdRNx0R/?igsh=Zzdpd3I4cDVudWlv"

instaDownloader(link)
