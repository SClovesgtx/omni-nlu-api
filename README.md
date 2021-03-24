![](imgs/Logo_Omni_NLU.gif)
# 1 - Introduction

The purpose of this project is to provide NLU resources for Omni Plataform.

It helps to train Machine Learning Models (MLM):

![](imgs/api_for_train_ml_models.gif)

And feed the Omni Plataform with these MLM resources:

![](imgs/intro_nlu_api.png)

# 2 - Local OS Requirements

These are requirements for your local machine, ideally a Debian Linux OS:

* [docker](https://docs.docker.com/engine/install/): follow the [instructions in the docker docs](https://docs.docker.com/engine/install/linux-postinstall/) to ensure that $USER has root access to docker.

* [docker-compose](https://docs.docker.com/compose/install/).

* [VS Code](https://code.visualstudio.com/docs/setup/linux): install the [`ms-vscode-remote.remote-containers`](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension locally. A pop-up will open up asking if you would like to reload the workspace in the container. After choosing "Reopen in Container", VS Code will open the "bash" docker-compose service in the Omni NLU API container, as specified in the manifest `.devcontainer.json`. Notice that VS Code will run intilization commands that may take some time to process. VS Code will already include the [`ms-python.python`](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension, without the need to install it in your own local machine. You may add any other extensions that you may need in your Python project in the configuration file `.devcontainer.json` .

*  [git](https://git-scm.com/download/linux):
    ```
    sudo apt-get git
    ```

*  make:

    ```
    sudo apt-get update
    sudo apt-get install build-essential
    ```

* python3:

    ```
    sudo apt-get update
    sudo apt-get install python3
    ```

* pip3

    ```
    sudo apt-get update
    sudo apt-get install python3-pip
    ```

* pre-commit

    ```
    pip3 install pre-commit
    pre-commit install
    pre-commit migrate-config
    pre-commit autoupdate
    ```

    Or, simply run in the terminal `make install-requirements`, to install the `pre-commit` Python package.

**Do I need to install any other requirements?** No! After installing the basic local requirements described above, you are all set to run everything else inside a Docker container.

# Quick Start

First, make sure `make`, `docker` and `docker-compose` are installed in your system.

The greenhouse dev work is performed via `make` commands.

To see the most up to date list of available commands run

```bash
$ make help

USAGE

    make <command>
    Include 'sudo' when necessary.
    To avoid using sudo, follow the steps in
    https://docs.docker.com/engine/install/linux-postinstall/


COMMANDS

    build           build image using cache
    build-no-cache  build image from scratch, and not from cache
    bash            bash REPL (Read-Eval-Print loop), suitable for debugging
    python3         access Python through the REPL (Read-Eval-Print loop)
    jupyter         access Python through the Jupyter Notebook
    release         Release on the dev branch

```


To build your greenhouse (as it is), you first need to run:

```bash
$ make build-no-cache
```


To access Jupyter in your local browser:

```bash
$ make jupyter

Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    
    To access the notebook, open this file in a browser:
        file:///root/.local/share/jupyter/runtime/nbserver-1-open.html
    Or copy and paste one of these URLs:
        http://...:8888/lab?token=...
```


Next, you simply need to follow the instructions printed out on your own terminal.


In the generic example above, I would paste the following on my browser:

```bash
http://...:8888/lab?token=...
```


Any changes made in the files within the Jupyter interface, for example saved changes in `.rs`, `.ipynb`, and `.py` files, will be reflected in the original files you store locally, and vice-versa. This is ensured by the fact that the whole greenhouse directory is set as a `volume` in the `docker-compose.yml` configuration file.


You may also choose to run code using the REPL (Read-Eval-Print loop) in the terminal by running:

```bash
$ make python3
```


Now, you are ready to start developing Python code by creating new `.py` files in the `/src` directory.


During development phase, you can normally test out new code in a Jupyter Notebook.

Check out additional examples in the `/notebooks` directory (`.ipynb` files with preffix `example_`).

### 3 - Authentications

Something here soon...

### 1 - Index for NLU Model

Something here soon...

#### 1.1 -  Create

Something here soon...

#### 1.2 - Read

Something here soon...

#### 1.3 - Update

Something here soon...

#### 1.4 - Delete

Something here soon...

### 2 - Intents

Intentions are the main ingredients for training the model.

| Field | Type | Description
| ------ | ------ | ------ |
| ```intent``` | ```string``` | The intent name.
| ```examples``` | ```array of objects``` | A list of objects ```{"text": "some text here"}``` with text examples to train the machine to recognize this intent.

The following is an example of *intent* object:

```json
{
  "intent": "Abono",
  "examples": [
    {
      "text": "abono"
    },
    {
      "text": "Como solicitar abono?"
    },
    {
      "text": "Gostaria de vender 10 dias de férias"
    },
    {
      "text": "O que é abono?"
    },
    {
      "text": "Posso vender 15 dias de ferias e tirar 15 dias?"
    },
    {
      "text": "Posso vender as férias?"
    },
    {
      "text": "Quando é feito o pagamento dos 10 dias que vendi?"
    }
  ],
  "description": "tema Programação, Alteração e Cancelamento de Férias"
}
```

### 2.1 Create

Something here soon...


#### 2.2 - READ

Something here soon...

#### 2.3 - Update

Something here soon...


#### 2.4 Delete

Something here soon...


### 3 - Entities

Entities are useful information to contextualize the user's intent. Think of *entities* as nouns and *intentions* as verbs. For example, if the *intention* is to buy, the *entity* could be a product.

Entities can be of two types:

* **synonyms**: A word and its synonyms. This type of entity is allowed to use [fuzzy-match](https://en.wikipedia.org/wiki/Approximate_string_matching). For example, let's suppose we have an entity for a ```cities```, its values could be:
    * value ```Rio de Janeiro``` and its synonyms ```Rio, RJ```;
    * value ```São Paulo``` and its synonyms ```SP, Sampa, Terra da Garoa```

* **patterns**: An entity that has a very well-defined pattern and could be expressed by a ```regex```. For example: date formats, e-mail, CPF, telephone number, numbers, monetary values, etc.

Entities can be inserted in the examples of training intentions. For example:

```json
{
  "intent": "Abono",
  "examples": [
    {
      "text": "Gostaria de vender @sysNumber dias de férias"
    },
    {
      "text": "Minhas férias começam em no dia @sysDate e vai até dia @sys_date. Eu poderia voltar de férias dia @sys_date e vender o restante?"
    },
    {
      "text": "Quando é feito o pagamento dos @sysNumbers dias que vendi? Estou esperando receber @sysMonetary"
    }
  ]
}
```
See that instead of writing, for example, *15* I wrote ```@sysNumbers```, instead of writing *11/12/2020* I wrote ```@sysDates``` and instead of writing *R$ 1000.00* I wrote ```@sysMonetary```. This way, the machine will know that when the customer intends to *Abono* he will use dates, numbers and monetary values.


#### 3.1 - Create



A example of entity of type pattern:

```json
{
    "entity": "ContactInfo",
    "values": [
        {
          "type": "patterns",
          "value": "email",
          "patterns": [
            "\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b",
            "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
          ]
        },
        {
          "type": "patterns",
          "value": "telefone",
          "patterns": [
            "^\\s?\\(?\\d{2,3}\\)?[\\s-]?\\d{4,5}-?\\d{4}\\s?$"
          ]
        }
      ],
    "fuzzy_match": false
}
```

A example of entity of type synonym:

```json
{
    "entity": "CulturaPlatacao",
    "values": [
        {
          "type": "synonyms",
          "value": "Café",
          "synonyms": []
        },
        {
          "type": "synonyms",
          "value": "Cana-de-Açúcar",
          "synonyms": ["cana"]
        },
        {
          "type": "synonyms",
          "value": "Mandioca",
          "synonyms": ["macaxeira", "aipim", "castelinha", "uaipi", "mandioca-doce", "mandioca-mansa", "maniva", "maniveira", "pão-de-pobre", "mandioca-brava" e "mandioca-amarga"]
        }
      ],
    "fuzzy_match": true
}
```

You will get back a entity id.

#### 3.2 - READ

Something here soon...

#### 3.3 - Update

Something here soon...


#### 3.4 Delete

Something here soon...

# 4 - Resources

Here you will find resources for intent classification and match entities in text.

#### 4.1 - Train the Model

Something here soon...

#### 4.2 - To Get Entities Values Inside Text

Something here soon...