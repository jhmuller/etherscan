import os
import sys
import pandas as pd
import time
import datetime
import yaml
from microprediction import MicroWriter
from getjson import getjson
import matplotlib as mpl
import matplotlib.pyplot as plt


def extract_gas_prices(data, source):
    try:
        if source == "etherscan":
            hi = float(data["result"]["FastGasPrice"]) 
            med = float(data["result"]["ProposeGasPrice"])
            lo = float(data["result"]["SafeGasPrice"]) 
        elif source == "ethgasstation":
            hi = float(data["fastest"])/ 10.0
            med = float(data["fast"])/ 10.0
            lo = float(data["safeLow"])/ 10.0
        else:
            msg = f"invalid source: {source}"
            msg += str(sys.exc_info())
            raise RuntimeError(msg)
        return (hi, med, lo)
    except Exception:
        msg = f"Error extracting source: {source} data: {data}"
        msg += str(sys.exc_info())        
        raise RuntimeError(msg)


def publish(gas_key, freq_seconds=60,):
    i = 0
    tups = []
    while i < 200:
        i += 1
        yaml_files = [x for x in os.listdir(".") if x.endswith("yaml")]
        for yfile in yaml_files:
            thisdir = os.getcwd()
            fpath = os.path.join(thisdir, yfile)
            try:
                with open(fpath, 'r') as fp:
                    ydata = yaml.safe_load(fp)
                key = ydata["key"]
                endpoint = ydata["endpoint"]    
            except Exception:
                msg = f"Error reading yaml for {yfile} {datetime.datetime.now()}"
                msg += str(sys.exc_info())
                raise RuntimeError(msg)     

            url = endpoint.format(key=key)
            try:
                data = getjson(url)
                pass
            except Exception:
                msg = f"Error getting json from url {url} {datetime.datetime.now()}"
                msg += str(sys.exc_info())
                raise RuntimeError(msg)    
            try:
                source = yfile.split("-")[0]
                hi, med, lo = extract_gas_prices(data=data, source=source)  
                tups.append([hi, med, lo, source, datetime.datetime.now()])
                df = pd.DataFrame(tups, columns=["hi", "med", "lo", "source", "dt"])
                print(f"{source}: hi: {hi}, med: {med}, lo: {lo} {datetime.datetime.now().strftime('%H:%M:%S')}")
            except Exception:
                msg = f"Error getting extracting values from data url: {url}"
                msg += f" {datetime.datetime.now()}\n"
                msg += f" {data}"
                msg += str(sys.exc_info())
                break
        time.sleep(freq_seconds)
        print("--")
    df = pd.DataFrame(tups, columns=["hi", "med", "lo", "source", "dt"])
    df.sort_values(by="dt", inplace=True)  

    df.to_csv("gas.csv")  
    return    
    if False:
        fig, ax = plt.subplots(figsize=[10,10])
        plt.ion()
        plt.show()
        plt.style.use('ggplot')        
        ax.clear()
        plt.plot(df["dt"], df["fastest"], color="red", marker='x')
        plt.plot(df["dt"], df["fast"], color="blue", marker='o')
        plt.plot(df["dt"], df["low"], color="green", marker='+')
        plt.legend()
        plt.draw()
        plt.pause(0.001)
        input("Press [enter] to continue.") 

if __name__ == '__main__':
    freq_seconds = 2
    write_key = ''
    with open('./gas-key.txt', 'r') as fp:
        gas_key = fp.read()
    with open("./sealable_bass.txt", "r") as fp:
        write_key = fp.read()
    mw = MicroWriter(write_key=write_key)

    publish( gas_key=gas_key, freq_seconds=freq_seconds)
