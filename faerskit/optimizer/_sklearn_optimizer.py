from typing import Union, List

import deepchem as dc
import optuna
from deepchem.feat import Featurizer
from optuna.visualization import plot_optimization_history
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
from ._optimizer import Optimizer

__all__ = ['SklearnOptimizer']


class SklearnOptimizer(Optimizer):
    def __init__(self, file_name: str, featurizer: Union[Featurizer, str] = None, feature_field: str = "smiles",
                 data_dir: str = "./dataset", save_dir: str = "./dataset", tasks: List[str] = None, seed=41):
        if tasks is None:
            tasks = ['labels']
        if featurizer is None:
            featurizer = dc.feat.CircularFingerprint()
        super(SklearnOptimizer, self).__init__(file_name, featurizer, feature_field, data_dir, save_dir, tasks, seed)

    def optimize_xgboost(self, n_trials=100, save_dir='.'):
        # 创建study并执行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.xgboost_objective(trial), n_trials=n_trials)
        print(study.best_params)
        # 获取所有试验记录
        trials = study.trials_dataframe()
        # 导出为 CSV 文件
        trials.to_csv(save_dir + "/xgboost_trials.csv", index=False)
        # 绘制优化历史
        figure = plot_optimization_history(study, target_name='value')
        # 将图表保存
        figure.write_html(save_dir + '/xgboost_optimization_history.html')

    def xgboost_objective(self, trial):
        # 定义超参数搜索空间
        learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3)
        max_depth = trial.suggest_int("max_depth", 3, 30)
        n_estimators = trial.suggest_int("n_estimators", 100, 500)
        min_child_weight = trial.suggest_int("min_child_weight", 1, 10)
        gamma = trial.suggest_float("gamma", 0.01, 0.3)

        model = XGBClassifier(
            learning_rate=learning_rate,
            max_depth=max_depth,
            n_estimators=n_estimators,
            min_child_weight=min_child_weight,
            gamma=gamma,
            random_state=self.seed
        )
        # 使用交叉验证评估模型性能
        score = cross_val_score(model, self.dataset.X, self.dataset.y.ravel(), cv=5, scoring='accuracy').mean()
        return score

    def optimize_svm(self, n_trials=100, save_dir='.'):
        # 创建study并执行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.svm_objective(trial), n_trials=n_trials)
        print(study.best_params)
        # 获取所有试验记录
        trials = study.trials_dataframe()
        # 导出为 CSV 文件
        trials.to_csv(save_dir + "/svm_trials.csv", index=False)
        # 绘制优化历史
        figure = plot_optimization_history(study, target_name='value')
        # 将图表保存
        figure.write_html(save_dir + '/svm_optimization_history.html')

    def svm_objective(self, trial):
        # 定义超参数搜索空间
        C = trial.suggest_float("C", 0.1, 100, log=True)  # C 的范围：0.1 到 100，对数尺度
        gamma = trial.suggest_float("gamma", 0.001, 1, log=True)  # gamma 的范围：0.001 到 1，对数尺度
        kernel = trial.suggest_categorical("kernel", ["linear", "rbf", "poly"])  # 核函数选择
        model = SVC(C=C, gamma=gamma, kernel=kernel, random_state=self.seed)
        # 使用交叉验证评估模型性能
        score = cross_val_score(model, self.dataset.X, self.dataset.y.ravel(), cv=5, scoring='accuracy').mean()
        return score

    def optimize_rf(self, n_trials=100, save_dir='.'):
        # 创建study并执行优化
        study = optuna.create_study(direction='maximize')
        study.optimize(lambda trial: self.rf_objective(trial), n_trials=n_trials)
        print(study.best_params)
        # 获取所有试验记录
        trials = study.trials_dataframe()
        # 导出为 CSV 文件
        trials.to_csv(save_dir + "/random_forest_trials.csv", index=False)
        # 绘制优化历史
        figure = plot_optimization_history(study, target_name='value')
        # 将图表保存
        figure.write_html(save_dir + '/random_forest_optimization_history.html')

    def rf_objective(self, trial):
        # 定义超参数搜索空间
        n_estimators = trial.suggest_categorical('n_estimators', [100, 200, 300, 400, 500])
        max_depth = trial.suggest_int('max_depth', 3, 30)
        min_samples_split = trial.suggest_int('min_samples_split', 2, 20)
        min_samples_leaf = trial.suggest_int('min_samples_leaf', 1, 10)
        max_features = trial.suggest_categorical('max_features', ['sqrt', 'log2'])
        bootstrap = trial.suggest_categorical('bootstrap', [True, False])
        criterion = trial.suggest_categorical('criterion', ['gini', 'entropy'])

        # 创建随机森林模型
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            bootstrap=bootstrap,
            criterion=criterion,
            random_state=self.seed
        )
        # 使用交叉验证评估模型性能
        score = cross_val_score(model, self.dataset.X, self.dataset.y.ravel(), cv=5, scoring='accuracy').mean()
        return score
