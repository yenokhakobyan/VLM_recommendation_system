import faiss
import numpy as np
from scipy.spatial.distance import cosine

class FaissIndex:
    def __init__(self, dim=512):
        self.index = faiss.IndexFlatL2(dim)
        self.embeddings = []
        self.ids = []
        self.id_to_vec = {}

    def add(self, vec, item_id):
        self.embeddings.append(vec)
        self.ids.append(item_id)
        self.id_to_vec[item_id] = vec

    def build(self):
        self.index.add(np.stack(self.embeddings).astype('float32'))

    def search(self, query_vec, top_k=5):
        D, I = self.index.search(np.expand_dims(query_vec.astype('float32'), axis=0), top_k * 2)
        candidates = [(self.ids[i], self.id_to_vec[self.ids[i]]) for i in I[0]]
        reranked = sorted(candidates, key=lambda x: cosine(query_vec, x[1]))[:top_k]
        return [item_id for item_id, _ in reranked]