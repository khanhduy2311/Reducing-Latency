from gptcache import cache
from gptcache.similarity_evaluation.onnx import OnnxModelEvaluation

cache.init(
           similarity_evaluation=OnnxModelEvaluation(),
           )
cache.set_openai_key()