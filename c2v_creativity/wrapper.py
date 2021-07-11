from vocabularies import VocabType
from config import Config
from common import common
from interactive_predict import InteractivePredictor
from model_base import Code2VecModelBase
import numpy as np
SHOW_TOP_CONTEXTS = 10


class InteractivePredictorWrapper(InteractivePredictor):
    def __init__(self):
        config = Config(set_defaults=True, load_from_args=True)
        config.MODEL_LOAD_PATH = 'models/java14_model/saved_model_iter8.release'
        config.EXPORT_CODE_VECTORS = True
        model = load_model_dynamically(config)
        super().__init__(config, model)

    def predict(self, code_string):
        input_filename = 'C:/C2V/code2vec/tmp/tmp_code.java'
        error_filename = 'C:/C2V/code2vec/tmp/err_code.java'


        try:
            with open(input_filename, 'wt', encoding="utf-8") as f:
                f.write(code_string)
            predict_lines, hash_to_string_dict = self.path_extractor.extract_paths(input_filename)
        except ValueError as e:
            print("Cannot Parse")
#            with open(error_filename, 'at', encoding="utf-8") as fe:
#                fe.write(code_string)
            return np.nan
        raw_prediction_results = self.model.predict(predict_lines)
        return {r.original_name: r.code_vector for r in raw_prediction_results}


def load_model_dynamically(config: Config) -> Code2VecModelBase:
    assert config.DL_FRAMEWORK in {'tensorflow', 'keras'}
    if config.DL_FRAMEWORK == 'tensorflow':
        from tensorflow_model import Code2VecModel
    elif config.DL_FRAMEWORK == 'keras':
        from keras_model import Code2VecModel
    return Code2VecModel(config)


if __name__ == '__main__':
    predictor = InteractivePredictorWrapper()
    code = """
static int f(int n)
{
    if (n == 0)
        return 1;

    return n * f(n-1);
}

static int g(int n)
{
    if (n == 0)
        return 1;

    return n * g(n-1);
}
    """
    vector = predictor.predict(code)
    print(vector)
