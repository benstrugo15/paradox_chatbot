# Assignment Setup Guide

## Prerequisites

- Ensure Docker is installed and running on your system. [Installation Guide](https://docs.docker.com/get-docker/)
- Ensure Python 3.10 or higher is installed. [Installation Guide](https://www.python.org/downloads/)

## Install the Service

1.  It's recommended to use a virtual environment to manage dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  Copy the sample environment file:
    ```bash
    cp sample.env .env
    ```

3.  Open the newly created `.env` file and replace OpenAI's API key with the key provided to you.

4.  Install the required Python packages:
    ```bash
    pip install setuptools
    pip install -r requirements.txt
    ```

## Qdrant Setup

To get started, you need to run the VectorDB (Qdrant). The necessary files are in the `scripts` folder:

- `startups_demo.json`: A JSON containing information about various startups. A copy of [startups_demo.json](https://storage.googleapis.com/generall-shared-data/startups_demo.json).
- `startup_vectors.npy`: Vector embeddings representing the JSON data.
- `init_collection.py`: Script to load vectors into Qdrant.

1.  Go to the project's root folder and run the following command:
    ```bash
    docker run -p 6333:6333 -p 6334:6334 \
    -v "$(pwd)/qdrant":/qdrant/storage:z \
    qdrant/qdrant
    ```

    If you run into any issues running this container, follow the [Qdrant Quickstart Guide](https://qdrant.tech/documentation/quickstart/#download-and-run).

2.  Run the following command to load the vectors into Qdrant (make sure you're inside the virtual env if you created one):
    ```bash
    python -m scripts.init_collection
    ```

3.  Qdrant will be running on port `6333`. You can access the WebUI at [http://localhost:6333/dashboard](http://localhost:6333/dashboard).

## Run the service

Start the API service, it might take a minute:
```bash
python main.py
```

Once the service is running, you can access the API documentation at http://0.0.0.0:8000/docs.

