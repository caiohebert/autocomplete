import os
import sys
import itertools

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autocomplete.trie import Trie
from autocomplete.index import build_trie_from_csv_file


try:
    QUERIES_FILE = os.environ["QUERIES_FILE"]
except KeyError:
    sys.stderr.write("Variável de ambiente QUERIES_FILE não definida.\n")
    sys.exit(1)

try:
    DEFAULT_SUGGESTION_LIMIT = int(os.environ.get("DEFAULT_SUGGESTION_LIMIT", "50"))
except ValueError:
    sys.stderr.write("Variável de ambiente DEFAULT_SUGGESTION_LIMIT não é um número.\n")
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.trie = build_trie_from_csv_file(QUERIES_FILE)
    yield


app = FastAPI(lifespan=lifespan)

# Política de CORS permissiva para permitir que o frontend acesse o backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["null"],  # unsafe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/autocomplete")
def complete(q: str):
    trie = app.state.trie
    trie_node = trie.find_prefix(q)
    suggestions = []
    if trie_node is not None:
        limit = DEFAULT_SUGGESTION_LIMIT
        iter_suffix = itertools.islice(trie.iter_suffix(trie_node), limit)
        suggestions = list(q + suffix for suffix in iter_suffix)
    return {"suggestions": suggestions}
