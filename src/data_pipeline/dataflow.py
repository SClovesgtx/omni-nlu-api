# standard library imports
import os

# setting working dir
os.chdir("../src")

# third party imports
from prefect import Flow, task, context

# local imports
from data_pipeline.data_sourcing import get_data
from data_pipeline.data_preprocessing import fill_missing_examples, clean_examples
from data_pipeline.data_splitting import data_splitting

@task
def sourcing(workspace, es):

    return get_data(
                workspace=workspace, 
                es=es
            )

@task
def treat_missing_data(data):
    
    return fill_missing_examples(data)

@task
def cleansing(data):

    return clean_examples(data)



@task(nout=2)
def splitting(data):

    return data_splitting(data)


def train_data_flow(workspace, es):

    # Define prefect flow
    with Flow("train_data_flow") as flow:
        data = sourcing(workspace=workspace, es=es)
        data = treat_missing_data(data=data)
        data = cleansing(data=data)
        train, test = splitting(data=data)

    flow.run()
    flow.visualize(filename="src/data_pipeline/flow_diagram/train_data_flow")