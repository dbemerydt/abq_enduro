from pywebio.input import *
from pywebio.output import *
from pywebio import config
from pywebio import STATIC_PATH
from pywebio import start_server
import argparse
import numpy as np
import pandas as pd


def main():

    config(css_style="#output-container{margin: 0 auto;max-width: 980px;padding: 0 10px;width: 100%; }")
    # config(css_style="#input-container{margin: 0 auto;max-width: 1000px;padding: 0 10px;width: 100%; }")




    put_markdown("### Example input (start and finish columns must be named using the *same format*.)")
    example_input = pd.read_csv('example_input.csv')
    put_html(example_input.to_html(index=False,border=0))
    put_markdown("## Full results:")
    csv_file = file_upload('Upload yer dang time data (as a .csv and not any format or so help me I WILL BREAK)')

    open(csv_file['filename'],'wb').write(csv_file['content'])

    # read the CSV file and create a DataFrame
    raw_results = pd.read_csv(csv_file['filename'])

    num_stages = len([c for c in list(raw_results) if "start" in c])
    df = raw_results.copy()
    for i in range(1,num_stages+1):
        df['stage_'+str(i)+'_start'] = pd.to_datetime(df['stage_'+str(i)+'_start'],format='%H:%M:%S')
        df['stage_'+str(i)+'_finish'] = pd.to_datetime(df['stage_'+str(i)+'_finish'],format='%H:%M:%S')
        df['stage_'+str(i)+'_time'] = df['stage_'+str(i)+'_finish'] - df['stage_'+str(i)+'_start']
        df['stage_'+str(i)+'_rank'] = df['stage_'+str(i)+'_time'].rank(ascending=True)

    df['total_time'] = df[['stage_'+str(i)+'_time' for i in range(1,num_stages+1)]].sum(axis=1)
    df['rank'] = df['total_time'].rank(ascending=True)


    for i in range(1,num_stages+1):
        df['stage_'+str(i)+'_start'] = df['stage_'+str(i)+'_start'].astype('str').str.slice(10)
        df['stage_'+str(i)+'_finish'] = df['stage_'+str(i)+'_finish'].astype('str').str.slice(10)

    df = df.sort_values("rank")
    # display the DataFrame as a table
    put_html(df[["rank","total_time","name","number"]+[c for c in list(df) if (("time" in c) or ("rank" in c))]+["name"]].to_html(index=False,border=0))
    # df.to_csv("full_results.csv")
    # put_file('full_results.csv', b"results")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=8080)
    args = parser.parse_args()
    start_server(main, args.port)
