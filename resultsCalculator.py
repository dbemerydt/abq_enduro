from pywebio.input import *
from pywebio.output import *
from pywebio import config
from pywebio import STATIC_PATH
from pywebio import start_server
import argparse
import numpy as np
import pandas as pd


def main():

    config(css_style="#output-container{margin: 0 auto;max-width: 1400px;padding: 0 10px;width: 100%; }")
    # config(css_style="#input-container{margin: 0 auto;max-width: 1000px;padding: 0 10px;width: 100%; }")




    # put_markdown("### Example input (start and finish columns must be named and the times must be input using the *same format*.)")
    example_stage = pd.read_csv('example_input-stage1.csv')
    example_riders = pd.read_csv('example_input-rider_list.csv')
    # put_html(example_input.to_html(index=False,border=0))
    # put_markdown("## Full results:")
    # csv_file = file_upload('Upload yer dang time data (as a .csv and not any format or so help me I WILL BREAK)')
    # put_markdown("If this produces a white screen with no results, it is likely the result of the format example not being followed. Reload the page and double check the formatting, or call Ben.")

    # open(csv_file['filename'],'wb').write(csv_file['content'])

    num_stages = int(input("Enter the number of stages"))

    # read the CSV file and create a DataFrame
    # raw_results = pd.read_csv(csv_file['filename'])
    put_markdown("## Rider list example:")
    put_html(example_riders.to_html(index=False,border=0))
    put_markdown("## Stage spreadsheet example:")
    put_html(example_stage.to_html(index=False,border=0))
    df = pd.read_csv('example_input-rider_list.csv')
    csv_file = file_upload('Upload rider list')
    df = pd.read_csv(csv_file['filename'])

    for i in range(1,num_stages+1):

        
        csv_file = file_upload('Upload stage '+str(i)+' times')

        stage = pd.read_csv(csv_file['filename'])
        stage.columns = ['number','stage_'+str(i)+'_start','stage_'+str(i)+'_finish']
        stage['stage_'+str(i)+'_start'] = pd.to_datetime(stage['stage_'+str(i)+'_start'],format='%H:%M:%S')
        stage['stage_'+str(i)+'_finish'] = pd.to_datetime(stage['stage_'+str(i)+'_finish'],format='%H:%M:%S')
        df = pd.merge(df,stage,on='number')
        df['stage_'+str(i)+'_time'] = df['stage_'+str(i)+'_finish'] - df['stage_'+str(i)+'_start']
        df['stage_'+str(i)+'_rank'] = df['stage_'+str(i)+'_time'].rank(ascending=True)

    df['total_time'] = df[['stage_'+str(i)+'_time' for i in range(1,num_stages+1)]].sum(axis=1)
    df['rank'] = df['total_time'].rank(ascending=True)


    for i in range(1,num_stages+1):
        df['stage_'+str(i)+'_start'] = df['stage_'+str(i)+'_start'].astype('str').str.slice(10)
        df['stage_'+str(i)+'_finish'] = df['stage_'+str(i)+'_finish'].astype('str').str.slice(10)

    df = df.sort_values("rank")
    # display the DataFrame as a table
    put_markdown("## Tha results!")
    put_html(df[["rank","total_time","name","number","category"]+[c for c in list(df) if (("time" in c) or ("rank" in c))]+["name"]].to_html(index=False,border=0))
    df[["rank","total_time","name","number","category"]+[c for c in list(df) if (("time" in c) or ("rank" in c))]+["name"]].to_csv('results-full.csv')
    content = open('results-full.csv', 'rb').read()  
    put_file('results-full.csv', content, 'Download full results')
    # df.to_csv("full_results.csv")
    # put_file('full_results.csv', b"results")
    categories = list(df['category'].unique())
    for cat in categories:
        dfcat = df[df['category']==cat]
        for i in range(1,num_stages+1):
            dfcat['stage_'+str(i)+'_rank'] = dfcat['stage_'+str(i)+'_time'].rank(ascending=True)
        dfcat['rank'] = dfcat['total_time'].rank(ascending=True)
        dfcat = dfcat.sort_values("rank")
        put_html(dfcat[["rank","total_time","name","number","category"]+[c for c in list(df) if (("time" in c) or ("rank" in c))]+["name"]].to_html(index=False,border=0))
        dfcat[["rank","total_time","name","number","category"]+[c for c in list(df) if (("time" in c) or ("rank" in c))]+["name"]].to_csv('results-'+cat.replace(' ','_')+'.csv')
        content = open('results-'+cat.replace(' ','_')+'.csv', 'rb').read()  
        put_file('results-'+cat.replace(' ','_')+'.csv', content, 'Download '+cat+' results')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--port',type=int,default=8080)
    args = parser.parse_args()
    start_server(main, args.port)
