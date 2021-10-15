from web3 import Web3
from glob import glob

import json
import requests
import shutil

infura_url_http  = "https://mainnet.infura.io/v3/3dec7f3741b648c6ace34e2874d5e2e9"
infura_url_ws    = "wss://mainnet.infura.io/ws/v3/3dec7f3741b648c6ace34e2874d5e2e9"
# ipfsGatewayBase  = "http://127.0.0.1:8080/"
ipfsGatewayBase  = "https://ipfs.io/ipfs/"
cropCharsURL     = 7
image_path       = "out/"
image_type       = ".png"
address          = "0x026224A2940bFE258D0dbE947919B62fE321F042"
timeout_metadata = 3
timeout_image    = 10
numDigits        = 4

# w3 = Web3(Web3.HTTPProvider(infura_url_http))
web3 = Web3(Web3.WebsocketProvider(infura_url_ws))

# print(web3.isConnected())

with open("LobstersNftABI.json") as f:
    abi = json.load(f)

lobsters = web3.eth.contract(address = address, abi = abi)

totalSupply = lobsters.functions.totalSupply().call()

# check if any files have already been downloaded, if yes continue
files = sorted(glob(image_path + "*" + image_type)) # "out/*.png"
lastFile = 0
if len(files) > 0:
    firstToProcess = int(files[-1][len(image_path):-(len(image_type))]) + 1
    print("Found previously processed files, will continue at token id " + str(firstToProcess))

for index in range(firstToProcess, totalSupply):
    print("Processing NFT " + str(index) + " of " + str(totalSupply) + "...")

    error = True
    while (error):
        try:
            tokenURI = lobsters.functions.tokenURI(index).call()
            error = False
        except:
            print("Rekt! Trying to load tokenURI from Ethereum again...")
            error = True

    # something between web3.py and Infura IPFS gateway is broken
    # so we gotta hack it with requests against the IPFS gateway

    ipfsURI1 = ipfsGatewayBase + tokenURI[cropCharsURL:]

    error = True
    while (error):
        try:
            res1 = requests.get(ipfsURI1, timeout = timeout_metadata)
            error = False
        except:
            print("Rekt! Trying to get metadata from IPFS again...")
            print(tokenURI)
            error = True
    
    metadata = res1.text

    data = json.loads(metadata)

    imageURI2 = data["image"]
    ipfsURI2 = ipfsGatewayBase + imageURI2[cropCharsURL:]

    errorCopy = True
    while (errorCopy):

        error = True
        while (error):
            try:
                res2 = requests.get(ipfsURI2, stream = True, timeout = timeout_image)
                error = False
            except:
                print("Rekt! Trying to get image from IPFS again...")
                print(ipfsURI2)
                error = True

        filename = str(index)
        filename = filename.rjust(numDigits, "0")

        with open(image_path + filename + image_type, "wb") as out_file:
            try:
                shutil.copyfileobj(res2.raw, out_file)
                errorCopy = False
            except:
                errorCopy = True
                print("Rekt! Trying to store file again...")
