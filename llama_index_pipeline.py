from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core import VectorStoreIndex
from llama_index.core.extractors import TitleExtractor
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.llms.huggingface import HuggingFaceLLM

# Configure hugging face embeding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-large-en-v1.5"
)

# seting up llama-2 LLM
llm = HuggingFaceLLM(
    context_window=4096,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.0, "do_sample": False},
    tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
    model_name="meta-llama/Llama-2-7b-chat-hf",
    device_map="auto",
)

# Configure hugging face embeding model
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-large-en-v1.5"
)

# Load data from the directory
documents = SimpleDirectoryReader("./data").load_data()

# Chunking (converting the document into nodes)
node_parser = SentenceWindowNodeParser.from_defaults(
    # how many sentences on either side to capture
    window_size=3,
    # the metadata key that holds the window of surrounding sentences
    window_metadata_key="window",
    # the metadata key that holds the original sentence
    original_text_metadata_key="original_sentence",
)

# create the pipeline with transformations
pipeline = IngestionPipeline(
    transformations=[
        node_parser,
        TitleExtractor(llm=llm),
        HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5"),
    ]
)

# run the pipeline to extract nodes
nodes = pipeline.run(documents=documents)

# indexing on nodes
index = VectorStoreIndex(nodes)

# create query engine
query_engine = index.as_query_engine(llm=llm)

# a function that run query on the data and return its response
def search(query):
    # query on index
    try:
        response = query_engine.query("{query}".format(query=query))
    except IndexError:
        response = "No result found against your query."
    # print("Response: ",response)
    # return query response
    return response