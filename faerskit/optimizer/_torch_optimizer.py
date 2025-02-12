from typing import List

from deepchem.feat import DMPNNFeaturizer, MolGraphConvFeaturizer
import optuna
from deepchem.metrics import Metric

from deepchem.models import DMPNNModel, TorchModel, GCNModel
from optuna.visualization import plot_optimization_history
from sklearn.metrics import accuracy_score
import numpy as np
from deepchem.splits import RandomSplitter

from ._optimizer import Optimizer

__all__ = ['DMPNNOptimizer', 'GCNOptimizer']


def _cross_val_score(dataset, estimator: TorchModel, k=5):
    spliter = RandomSplitter()
    split_datasets = spliter.k_fold_split(dataset, k=k)
    # 交叉验证
    fold_results = []
    for train, cv in split_datasets:
        estimator.fit(train)
        metric = Metric(accuracy_score)
        evaluate = estimator.evaluate(cv, [metric])
        fold_results.append(evaluate['accuracy_score'])
    return np.mean(fold_results)


class DMPNNOptimizer(Optimizer):
    def __init__(self, file_name: str, feature_field: str = "smiles", data_dir: str = "./dataset",
                 save_dir: str = "./dataset", tasks: List[str] = None, seed=41):
        if tasks is None:
            tasks = ['labels']
        featurizer = DMPNNFeaturizer()
        super(DMPNNOptimizer, self).__init__(file_name, featurizer, feature_field, data_dir, save_dir, tasks, seed)

    def optimize(self, n_trials=100, save_dir="."):
        # 创建study并执行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.objective(trial), n_trials=n_trials)
        print(study.best_params)
        # 获取所有试验记录
        trials = study.trials_dataframe()
        # 导出为 CSV 文件
        trials.to_csv(save_dir + "/dmpnn_trials.csv", index=False)
        # 绘制优化历史
        figure = plot_optimization_history(study, target_name='value')
        # 将图表保存
        figure.write_html(save_dir + '/dmpnn_optimization_history.html')

    def objective(self, trial):
        self.set_seed()
        depth = trial.suggest_int('depth', 3, 5)
        enc_hidden = trial.suggest_categorical('enc_hidden', [200, 300, 400, 500])
        ffn_layers = trial.suggest_int('ffn_layers', 3, 5)
        batch_size = trial.suggest_categorical('batch_size', [1, 2, 4, 8])
        enc_activation = trial.suggest_categorical('enc_activation',
                                                   ["relu", "leakyrelu", "prelu", "tanh", "selu", "elu"])
        enc_dropout_p = trial.suggest_categorical('enc_dropout_p', [0.1, 0.2, 0.3, 0.4, 0.5])
        # 定义模型
        model = DMPNNModel(n_tasks=1, mode='classification', n_classes=2, depth=depth, enc_hidden=enc_hidden,
                           ffn_layers=ffn_layers, batch_size=batch_size, enc_activation=enc_activation,
                           enc_dropout_p=enc_dropout_p)
        return _cross_val_score(self.dataset, model)


class GCNOptimizer(Optimizer):
    def __init__(self, file_name: str, feature_field: str = "smiles", data_dir: str = "./dataset",
                 save_dir: str = "./dataset", tasks: List[str] = None, seed=41):
        if tasks is None:
            tasks = ['labels']
        featurizer = MolGraphConvFeaturizer()
        super(GCNOptimizer, self).__init__(file_name, featurizer, feature_field, data_dir, save_dir, tasks, seed)

    def optimize(self, n_trials=100, save_dir="."):
        # 创建study并执行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.objective(trial), n_trials=n_trials)
        print(study.best_params)
        # 获取所有试验记录
        trials = study.trials_dataframe()
        # 导出为 CSV 文件
        trials.to_csv(save_dir + "/GCN_trials.csv", index=False)
        # 绘制优化历史
        figure = plot_optimization_history(study, target_name='value')
        # 将图表保存
        figure.write_html(save_dir + '/GCN_optimization_history.html')

    def objective(self, trial):
        self.set_seed()
        graph_conv_layers = trial.suggest_categorical('graph_conv_layers', [[32, 32], [64, 64], [128, 128]])
        residual = trial.suggest_categorical('residual', [True, False])
        batchnorm = trial.suggest_categorical('batchnorm', [True, False])
        dropout = trial.suggest_categorical('dropout', [0., 0.01, 0.1])
        predictor_hidden_feats = trial.suggest_categorical('predictor_hidden_feats', [64, 128, 256])
        predictor_dropout = trial.suggest_categorical('predictor_dropout', [0., 0.01, 0.1])
        number_atom_features = trial.suggest_categorical('number_atom_features', [20, 30, 40])
        # 定义模型
        model = GCNModel(n_tasks=1, mode='classification', n_classes=2, graph_conv_layers=graph_conv_layers,
                         residual=residual, batchnorm=batchnorm, dropout=dropout,
                         predictor_hidden_feats=predictor_hidden_feats, predictor_dropout=predictor_dropout,
                         number_atom_features=number_atom_features)
        return _cross_val_score(self.dataset, model)
