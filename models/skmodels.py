from sklearn.linear_model import SGDClassifier
from sklearn.svm import NuSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, StratifiedKFold, train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, roc_auc_score
import numpy as np
import pandas as pd
from joblib import dump, load
from os import path


class SkModels:
    def __init__(self):
        self.models = {
            'SGD': SGDClassifier(loss='log', random_state=1, max_iter=10_000, verbose=1, early_stopping=True, n_jobs=-1),
            'Bayes': GaussianNB(),
            'Forest': RandomForestClassifier(verbose=1, n_estimators=100, n_jobs=-1),
            'SVM': NuSVC(verbose=1, probability=True, max_iter=10_000, random_state=1)
        }
        self.scoring = {
            'Accuracy': 'accuracy',
            'Precision': 'precision_macro',
            'Recall': 'recall_macro',
            'F-score': 'f1_macro',
            'ROC AUC': 'roc_auc'
        }

    def validate(self, model, data, labels):
        splitter = StratifiedKFold(n_splits=10, random_state=1)
        return cross_validate(model, data, labels, cv=splitter, scoring=self.scoring,
                              return_train_score=False, n_jobs=-1,
                              return_estimator=False, error_score=np.nan)

    def run_models(self, data, labels):
        labels = labels.ravel()
        train_data, val_data, train_labels, val_labels = train_test_split(data, labels, test_size=0.1)
        scores = {}
        for name, model in self.models.items():
            print(f'Fitting {name} classifier...')
            model.fit(train_data, train_labels)
            y_pred = model.predict(val_data)
            y_scores = model.predict_proba(val_data)
            acc = accuracy_score(val_labels, y_pred)
            pre = precision_score(val_labels, y_pred, average='macro')
            rec = recall_score(val_labels, y_pred, average='macro')
            f1 = f1_score(val_labels, y_pred, average='macro')
            roc = roc_auc_score(val_labels, y_scores[:, 1])
            scores[name] = [acc, pre, rec, f1, roc]
        return pd.DataFrame.from_dict(scores, columns=['Accuracy', 'Precision', 'Recall', 'f1', 'ROC AUC'], orient='index')

    def predict(self, data):
        results = {}
        for name, model in self.models.items():
            results[name] = model.predict(data)
        return results

    def save_models(self, filepath):
        for name, model in self.models.items():
            dump(model, path.join(filepath, f'{name}.gz'), compress=3)

    def load_models(self, filepath):
        for name, model in self.models.items():
            if path.isfile(path.join(filepath, f'{name}.gz')):
                self.models[name] = load(path.join(filepath, f'{name}.gz'))