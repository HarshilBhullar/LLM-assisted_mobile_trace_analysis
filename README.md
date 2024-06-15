# LLM-assisted Mobile Trace Analysis

LLM-assisted Mobile Trace Analysis Project for CS 219

Groupmates: Harshil Bhullar, Julius Clausnitzer

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

This project's work is primarily done in Python Notebooks (ipynb). In order to run these notebooks, please set up and activate your Python env using the requirements.txt file:
```sh
cd /path/to/directory
conda create --name new_env_name --file requirements.txt
conda activate new_env_name
```

## Usage

There are 4 main .ipynb files, contained in the `/model_notebooks`. Each file focuses on a specific model implementation:

- `zero_shot.ipynb`: implements the zero_shot baseline GPT-3.5-turbo-0125 model
- `in_context_learning`.ipynb: implements the in_context_learning GPT-3.5-turbo-0125 model
- `finetuned_gpt.ipynb`: implements the finetuned model on top of the GPT-3.5-turbo-0125 model
- `langchain_rag_ipynb`: implements the RAG-assisted LLM workflow, using Chroma for the RAG vector store, and the models from the above 3 notebooks.

The `/example_analyzers` folder contains the 10 examples we extracted from the MobileInsight repository, and were used for finetuning the GPT model.

The `/generated_outputs` folder contains the `.py` outputs of all the relevant model outputs we have.

The `/chroma` folder contains metadata relevant to the RAG.

The `/prompts` folder contains the `.txt` prompt files. NOTE: have not really added many prompts there yet since we opted to keep them directly in the `.ipynb` files for now.

The `/testcases` folder contains the testcases provided to us by the TA to be used for evaluating our models.