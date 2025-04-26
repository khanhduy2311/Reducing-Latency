from gptcache import cache
from gptcache.manager import get_data_manager, CacheBase, VectorBase
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
import numpy as np

d = 8


def mock_embeddings(data, **kwargs):
    return np.random.random((d, )).astype('float32')

cache_base = CacheBase('sqlite')
vector_base = VectorBase('faiss', dimension=d)
data_manager = get_data_manager(cache_base, vector_base)
cache.init(embedding_func=mock_embeddings,
           data_manager=data_manager,
           similarity_evaluation=SearchDistanceEvaluation(),
           )
cache.set_openai_key()