from typing import List, Union
import random
import numpy
from deepchem.feat import Featurizer

from ._loader import FaersLoader


def get_dataset(file_name: str, featurizer: Union[Featurizer, str], feature_field: str, data_dir: str,
                save_dir: str, tasks: List[str] = None):
    loader = FaersLoader(file_name=file_name, featurizer=featurizer, splitter=None,
                         transformer_generators=['balancing'], data_dir=data_dir, save_dir=save_dir,
                         tasks=tasks, feature_field=feature_field)
    tasks, (datasets,), tf = loader.load_dataset(name='faers', reload=False)
    return datasets


class Optimizer:
    def __init__(self, file_name: str, featurizer=None, feature_field: str = "smiles", data_dir: str = "./dataset",
                 save_dir: str = "./dataset", tasks: List[str] = None, seed=41):
        self.seed = seed
        self.dataset = get_dataset(file_name=file_name, featurizer=featurizer, feature_field=feature_field,
                                   data_dir=data_dir, save_dir=save_dir, tasks=tasks)

    def set_seed(self):
        random.seed(self.seed)
        numpy.random.seed(self.seed)
