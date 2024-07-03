import csv
import pickle
import time

import typer

from autocomplete.trie import Trie

app = typer.Typer()


def build_trie_from_csv_reader(csv_reader: csv.DictReader) -> Trie:
    trie = Trie()
    for row in csv_reader:
        query = row["Query"]
        if len(query) > 100:  # XXX problema de recursão
            continue
        trie.add_word(query)
    return trie


def build_trie_from_csv_file(input_file: str) -> Trie:
    print(f"Construindo árvore de prefixos com base no arquivo {input_file}...")
    before_build_trie_time = time.time()

    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        trie = build_trie_from_csv_reader(reader)

    print(
        f"Tempo para construir a árvore de prefixos: {time.time() - before_build_trie_time:.2f}s"
    )
    return trie


@app.command()
def index(input_file: str, output_file: str):
    trie = build_trie_from_csv_file(input_file)

    before_dump_trie_time = time.time()
    with open(output_file, "wb") as f:
        trie.serialize(f)

    print(
        f"Tempo para serializar a árvore de prefixos: {time.time() - before_dump_trie_time:.2f}s"
    )


@app.command()
def load(trie_file: str):
    print(f"Carregando árvore de prefixos do arquivo {trie_file}...")

    trie = Trie()
    before_load_trie = time.time()
    with open(trie_file, "rb") as f:
        trie.deserialize(f)

    print(
        f"Tempo para carregar a árvore de prefixos: {time.time() - before_load_trie:.2f}s"
    )


if __name__ == "__main__":
    app()
