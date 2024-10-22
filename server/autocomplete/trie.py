import itertools
import struct
import pickle

from dataclasses import dataclass, field
from typing import Iterator, Optional, BinaryIO


@dataclass(slots=True)
class Trie:
    node_list: list["TrieNode"] = field(default_factory=list)
    """Lista de nós da árvore de prefixos."""

    def __post_init__(self):
        self.node_list.append(TrieNode())  # [0] = root node

    def root(self) -> "TrieNode":
        return self.node_list[0]

    def add_word(self, word: str):
        current_node = self.root()
        for char in word:
            # vê se tem a primeira letra já ligada a raiz
            next_node = self.get_next_node(current_node, ord(char))
            if next_node is None:
                # se não, cria o nó e o insere na árvore
                new_node = TrieNode()
                self.node_list.append(new_node)
                index_new_node = len(self.node_list) - 1 # novo nó vai sempre pro final da lista
                current_node.add_edge(ord(char), index_new_node)
                next_node = new_node
            current_node = next_node
        current_node.set_is_word()
        current_node.increase_rank()
        
       
    def insert_word(self, current_node: "TrieNode", word: str):
        # outra forma de inserir palavra
        # usa recursão pra inserir nós enquanto "consome" a palavra
        # caso base: verifica se é o final da palavra
        if(word == ""):
            last_index = len(self.node_list) - 1
            last_node = self.node_list[last_index]
            last_node.set_is_word()
            return

        # vê se tem a primeira letra já ligada a raiz
        next_node = self.get_next_node(current_node, ord(word[0]))
       
        if(next_node != None):
            # retira primeiro char da palavra e faz recursão com o resto
            new_word = word[1:]
            self.insert_word(next_node, new_word)
        else:
            # se não, cria o nó e o insere na árvore antes de entrar na recursão
            new_node = TrieNode()
            self.node_list.append(new_node)
            index_new_node = len(self.node_list) - 1    # novo nó vai sempre pro final da lista
            current_node.add_edge(char=ord(word[0]), node_id=index_new_node)
            
            new_word = word[1:]
            self.insert_word(new_node, new_word)

    
    
    def get_next_node(self, current_node: "TrieNode", char: int) -> Optional["TrieNode"]:
        # encontra o próximo nó de acordo com o próximo char
        for edge in current_node.get_edges():
            if edge.get_char() == char:
                return self.node_list[edge.get_node_id()]
            
        # se não existir: 
        return None
            
    
    def find_prefix(self, prefix: str) -> Optional["TrieNode"]:
        current_node = self.root()

        for char in prefix:
            next_node = self.get_next_node(current_node, ord(char))
            if next_node is None:
                return None
            current_node = next_node
        return current_node


    def iter_suffix(self, node: "TrieNode") -> Iterator[str]:
        yield from self.dfs(node, "")


    def dfs(self, node: "TrieNode", word: str) -> Iterator[str]:
        # imprimir quando uma palavra acabou e se a váriável possuir chars
        # evita que, caso o prefixo já seja uma palavra, a função retorne ""
        if node.get_is_word() and word:
            yield word

        for edge in node.get_edges():
            # segue um caminho até o final antes de voltar e ir para outro
            next_node = self.node_list[edge.get_node_id()]
            yield from self.dfs(next_node, word + chr(edge.get_char()))

            
    def get_ranked_suggestions(self, node: "TrieNode") -> Iterator[str]:
        suggestions = []
        self.ranked_dfs(node, suggestions, "")

        ordered_tuples = sorted(suggestions, key=lambda x: x[1], reverse=True)
        ordered_sug = [x[0] for x in ordered_tuples]
        for suggestion in ordered_sug:
            yield suggestion
    
    def ranked_dfs(self, node: "TrieNode", sug_list: list, word: str):
        if node.get_is_word() and word:
            ranked_word = (word, node.get_rank())
            sug_list.append(ranked_word)

        for edge in node.get_edges():
            # segue um caminho até o final antes de voltar e ir para outro
            next_node = self.node_list[edge.get_node_id()]
            self.ranked_dfs(next_node, sug_list, word + chr(edge.get_char()))


    def serialize(self, output_file: BinaryIO):
        """
        Serializa a árvore de prefixos em um arquivo binário.

        Args:
            output_file: Arquivo binário para serializar a árvore.
        """
        # EXERCÍCIO 4: Implementar função de serialização da árvore.

        pickle.dump(self.node_list, output_file)


    @staticmethod
    def deserialize(input_file: BinaryIO) -> "Trie":
        """
        Deserializa a árvore de prefixos de um arquivo binário.

        Args:
            input_file: Arquivo binário para deserializar a árvore.
        """
        # EXERCÍCIO 4: Implementar função de desserialização da árvore.

        node_list = pickle.load(input_file)
        return Trie(node_list)


@dataclass(slots=True)
class TrieNode:
    edges: list["TrieEdge"] = field(default_factory=list)
    """Arestas que saem deste nó."""
    is_word: bool = False
    """Indica se este nó é o final de uma palavra."""
    quantity: int = 0

    def get_edges(self) -> list["TrieEdge"]:
        return self.edges
    
    def get_is_word(self) -> bool:
        return self.is_word

    def set_is_word(self):
        self.is_word = True

    def add_edge(self, char: int, node_id: int):
        # add aresta ao nó
        new_edge = TrieEdge(char, node_id)
        self.edges.append(new_edge)

    def increase_rank(self):
        self.quantity += 1

    def get_rank(self):
        return self.quantity

@dataclass(frozen=True, slots=True)
class TrieEdge:
    char: int
    """Índice ASCII / UTF-8 do caractere que leva a outro nó."""
    node_id: int
    """Nó ao qual o caractere leva."""
    """ ou seja, o índice na node_list """

    def get_char(self) -> int:
        return self.char
    
    def get_node_id(self) -> int:
        return self.node_id