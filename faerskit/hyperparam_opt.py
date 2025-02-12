from typing import List
from deepchem.feat import DMPNNFeaturizer
from faerskit.optimizer import FaersLoader


def opt_DMPNN(file_name: str, data_dir: str = "./dataset", save_dir: str = "./dataset", model_dir="./models/dmpnn",
              tasks: List[str] = None) -> None:
    if tasks is None:
        tasks = ['labels']
    featurizer = DMPNNFeaturizer()
    loader = FaersLoader(file_name=file_name, featurizer=featurizer, splitter='scaffold',
                         transformer_generators=['balancing'], data_dir=data_dir, save_dir=save_dir,
                         tasks=tasks, feature_field="smiles")
    tasks, datasets, tf = loader.load_dataset(name='faers', reload=False)
    train_dataset, valid_dataset, test_dataset = datasets
    print(train_dataset)
    # params_dict = {
    #     'n_tasks': [len(tasks)],
    #     'depth': [3, 4, 5],
    #     'enc_hidden': [200, 300, 400, 500],
    #     'ffn_layers': [3, 4, 5],
    #     'dropouts': [0.1, 0.2, 0.3, 0.4, 0.5],
    # }
    # optimizer = dc.hyper.GridHyperparamOpt(dc.models.DMPNNModel)
    # metric = dc.metrics.Metric(dc.metrics.accuracy_score)
    # best_model, best_hyperparams, all_results = optimizer.hyperparam_search(
    #     params_dict, train_dataset, valid_dataset, metric, tf)
    # print(best_hyperparams)
    # print(all_results)
    # best_model.save_checkpoint(model_dir=model_dir)
