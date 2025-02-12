import os
from typing import Union, List
from deepchem.molnet import TransformerGenerator, featurizers, splitters, transformers
from deepchem.feat import Featurizer
from deepchem.splits import Splitter
from deepchem.utils import data_utils
from deepchem.data import DiskDataset, Dataset, CSVLoader


class FaersLoader:
    def __init__(self, file_name: str, featurizer: Union[Featurizer, str],
                 splitter: Union[Splitter, str, None],
                 transformer_generators: List[Union[TransformerGenerator,
                                                    str]], tasks: List[str],
                 data_dir: str = "./dataset", save_dir: str = "./dataset", feature_field="smiles"
                 ):
        self.feature_field = feature_field
        if isinstance(featurizer, str):
            featurizer = featurizers[featurizer.lower()]
        if isinstance(splitter, str):
            splitter = splitters[splitter.lower()]
        self.featurizer = featurizer
        self.splitter = splitter
        self.transformers = [
            transformers[t.lower()] if isinstance(t, str) else t
            for t in transformer_generators
        ]
        self.tasks = list(tasks)
        self.save_dir = save_dir
        self.data_dir = data_dir
        self.file_name = file_name

    def load_dataset(self, name: str, reload: bool):
        # Build the path to the dataset on disk.
        featurizer_name = str(self.featurizer)
        splitter_name = 'None' if self.splitter is None else str(self.splitter)
        save_folder = os.path.join(self.save_dir, name + "-featurized",
                                   featurizer_name, splitter_name)
        if len(self.transformers) > 0:
            transformer_name = '_'.join(
                t.get_directory_name() for t in self.transformers)
            save_folder = os.path.join(save_folder, transformer_name)
        # Try to reload cached datasets.
        if reload:
            if self.splitter is None:
                if os.path.exists(save_folder):
                    data_transformers = data_utils.load_transformers(save_folder)
                    return self.tasks, (DiskDataset(save_folder),), data_transformers
            else:
                loaded, all_dataset, data_transformers = data_utils.load_dataset_from_disk(save_folder)
                if all_dataset is not None:
                    return self.tasks, all_dataset, data_transformers
        # Create the dataset
        dataset = self.create_dataset()
        # Split and transform the dataset.
        if self.splitter is None:
            transformer_dataset: Dataset = dataset
            data_transformers = [
                t.create_transformer(transformer_dataset) for t in self.transformers
            ]
            for transformer in data_transformers:
                dataset = transformer.transform(dataset)
            if reload and isinstance(dataset, DiskDataset):
                dataset.move(save_folder)
                data_utils.save_transformers(save_folder, data_transformers)
            return self.tasks, (dataset,), data_transformers
        else:
            train, valid, test = self.splitter.train_valid_test_split(dataset)
            transformer_dataset = train
            data_transformers = [
                t.create_transformer(transformer_dataset) for t in self.transformers
            ]
        for transformer in data_transformers:
            train = transformer.transform(train)
            valid = transformer.transform(valid)
            test = transformer.transform(test)
        return self.tasks, (train, valid, test), data_transformers

    def create_dataset(self) -> Dataset:
        dataset_file = os.path.join(self.data_dir, self.file_name)
        loader = CSVLoader(tasks=self.tasks, feature_field=self.feature_field, featurizer=self.featurizer)
        return loader.create_dataset(dataset_file, shard_size=8192)
