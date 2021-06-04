![](imgs/Logo_Omni_NLU.gif)
# 1 - Introduction

The purpose of this project is to provide NLU resources for Omni Plataform.

It helps to train Machine Learning Models (MLM):

![](imgs/api_for_train_ml_models.gif)

And feed the Omni Plataform with these MLM resources:

![](imgs/intro_nlu_api.png)

# 2 - How to run this project in my local OS?

These are requirements for your local machine, ideally a Debian Linux OS:

* **docker**

* **docker-compose**

* **VS Code**: install the [`ms-vscode-remote.remote-containers`](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension locally. A pop-up will open up asking if you would like to reload the workspace in the container. After choosing "Reopen in Container", VS Code will open the "bash" docker-compose service in the Omni NLU API container, as specified in the manifest `.devcontainer.json`. Notice that VS Code will run intilization commands that may take some time to process. VS Code will already include the [`ms-python.python`](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension, without the need to install it in your own local machine. You may add any other extensions that you may need in your Python project in the configuration file `.devcontainer.json` .

*  **git**

*  **make**: to have make in your local OS, please run the following commands:

    ```
    sudo apt-get update
    sudo apt-get install build-essential
    ```

* **python3.6**

* **pip3**

* **pre-commit**: after you have *make* in you local OS, run  `make install-requirements`

You also need to define the host of your elasticsearch as a environment variable, so do:

```sh
~$ export ELASTICSEARCH_HOST=<the host of your elasticsearch>
```

Another way is creating a ```.env``` file in the root folder of this project and declare the ELASTICSEARCH_HOST.

The Omni NLU API is performed via `make` commands.

To see the commands run:

```bash
~$ make help
```

To build the project run:

```bash
~$ make build-up
```
To access the Jupyter Notebooks of the project in your local browser, run:

```bash
~$ make jupyter
```

To use bash inside container run:

```bash
~$ make bash
```

# Conventions used in this project

Before to make any contribution to Omni NLU API, make sure that you are familiar with the conventions of this project:

* **conventional commits**: write your commit messages following the standards defined [here](https://www.conventionalcommits.org/en/v1.0.0/).



# Postman Colection

You can try the Omni NLU API using the following public collections in you descktop Postman:

* [CRUD entities](https://estatisticacaps.postman.co/collections/7003300-0c6716e6-5d23-4025-a575-d316171eb372?workspace=7408cb64-1ce3-44b5-93e6-f7d5f44cfa42)
* [CRUD intents](https://estatisticacaps.postman.co/collections/7003300-b5c0ff06-bcab-45f3-8aa4-14400cdaca5b?workspace=7408cb64-1ce3-44b5-93e6-f7d5f44cfa42)
* [CRUD NLP Models Settings](https://estatisticacaps.postman.co/collections/7003300-036770e9-d3a9-4a6d-be37-69069d5ff229?workspace=7408cb64-1ce3-44b5-93e6-f7d5f44cfa42)
* [Classification Resources](https://estatisticacaps.postman.co/collections/7003300-873ff05e-662b-421a-ad6f-db8f4b739214?workspace=7408cb64-1ce3-44b5-93e6-f7d5f44cfa42)


# 3 - Authentications

Something here soon...





