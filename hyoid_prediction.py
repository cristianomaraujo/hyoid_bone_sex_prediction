# -*- coding: utf-8 -*-
"""Hioide - Aline

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1eWPdrVrUx9sa3_pzttbp4tQ-sdzy3XKA

# **Library and packages**
"""

import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_predict, KFold
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import roc_curve, auc

"""# **Dataset**"""

file_path = '/content/dataset.xlsx'
df = pd.read_excel(file_path)

df.columns

"""# **Data preprocessing**"""

colunas = ['sex', 'HD', 'VD',
       'DHM']

df = df.loc[:, colunas]

coluna_grupo = df.pop('sex')
df.insert(0, 'sex', coluna_grupo)

df.info()
df.columns

"""# **Model building**

**Data splitting**
"""

X = df.iloc[:,1:]
y = df.iloc[:,0]

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split


RANDOM_STATE = 3
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.3,random_state=RANDOM_STATE, shuffle=True)

#SMOTE - oversampling (only train data)
oversample = SMOTE(random_state=RANDOM_STATE)
X_train, y_train = oversample.fit_resample(X_train, y_train)


print(f"Train data shape of X = {X_train.shape} and Y = {y_train.shape}")
print(f"Test data shape of X = {X_test.shape} and Y = {y_test.shape}")

y_test.value_counts()

##Data normalization
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

y_train = y_train.astype('category')
y_test = y_test.astype('category')

# K-Folds
fold = 5

"""**GRADIENT BOOSTING**"""

param_grid = {
    'n_estimators': [50, 100, 200],
    'learning_rate': [0.01, 0.1, 0.2],
    'max_depth': [3, 5, 7],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

gb_model = GradientBoostingClassifier(random_state=RANDOM_STATE)
grid_search = GridSearchCV(estimator=gb_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_gb_model = grid_search.best_estimator_
best_gb_model.fit(X_train, y_train)
y_pred_test_gb = best_gb_model.predict(X_test)
y_prob_test_gb = best_gb_model.predict_proba(X_test)[:, 1]
conf_matrix_gb = confusion_matrix(y_test, y_pred_test_gb)
accuracy_gb = accuracy_score(y_test, y_pred_test_gb)
report_gb = classification_report(y_test, y_pred_test_gb)

print("Confusion Matrix (Test Data):\n", conf_matrix_gb)
print("Accuracy:", accuracy_gb)
print("Classification Report (Test Data):\n", report_gb)

kf_gb = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_gb = cross_val_predict(best_gb_model, X_train, y_train, cv=kf_gb, method='predict_proba')[:, 1]

y_pred_cv_gb = cross_val_predict(best_gb_model, X_train, y_train, cv=kf_gb)
conf_matrix_cv_gb = confusion_matrix(y_train, y_pred_cv_gb)
accuracy_cv_gb = accuracy_score(y_train, y_pred_cv_gb)
report_cv_gb = classification_report(y_train, y_pred_cv_gb)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_gb)
print("Cross-Validation Accuracy:", accuracy_cv_gb)
print("Classification Report (Cross-Validation):\n", report_cv_gb)

###Calculation of ROC Curve metrics and graph plotting (Test data and cross-validation)
fpr_gb, tpr_gb, _ = roc_curve(y_test, y_prob_test_gb, pos_label = 2)
roc_auc_gb = auc(fpr_gb, tpr_gb)

plt.figure(figsize=(8, 8))
plt.plot(fpr_gb, tpr_gb, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_gb))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()

# Cross-validation data
fpr_cv_gb, tpr_cv_gb, _ = roc_curve(y_train, y_prob_cv_gb, pos_label = 2)
roc_auc_cv_gb = auc(fpr_cv_gb, tpr_cv_gb)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_gb, tpr_cv_gb, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_gb))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

##FEATURE IMPORTANCE GRADIENT BOOSTING CLASSIFIER
X = df.drop('sex', axis=1)
features=[]
for columns in X.columns:
    features.append(columns)
imp_features = best_gb_model.feature_importances_
importances = best_gb_model.feature_importances_

feature_importance_gb = pd.DataFrame({'Feature': features, 'Importance': importances})

feature_importance_sorted = feature_importance_gb.sort_values('Importance', ascending=True)
colors = plt.cm.magma(np.linspace(0.2, 1, len(feature_importance_sorted)))
plt.figure(figsize=(10, 6))
bars = plt.barh(feature_importance_sorted['Feature'], feature_importance_sorted['Importance'], color=colors)
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')

for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, round(bar.get_width(), 4),
             va='center', ha='left', fontsize=10, color='white')

plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.gca().set_facecolor('white')
plt.tight_layout()
plt.show()

plt.savefig('figimpKNN.jpg', dpi=300, bbox_inches='tight')

"""**LOGISTIC REGRESSION**"""

param_grid = {

    'C': [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 5, 10, 100],
    'penalty': ['l1', 'l2', 'elasticnet', 'none'],
    'max_iter':[50, 100, 300, 500, 1000],
    'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
    'l1_ratio': [0.2, 0.4, 0.6, 0.8]
}
logreg_model = LogisticRegression(random_state=RANDOM_STATE)
grid_search = GridSearchCV(estimator=logreg_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_logreg_model = grid_search.best_estimator_
best_logreg_model.fit(X_train, y_train)
y_pred_test_logreg = best_logreg_model.predict(X_test)
y_prob_test_logreg = best_logreg_model.predict_proba(X_test)[:, 1]

conf_matrix_logreg = confusion_matrix(y_test, y_pred_test_logreg)
accuracy_logreg = accuracy_score(y_test, y_pred_test_logreg)
report_logreg = classification_report(y_test, y_pred_test_logreg)

print("Confusion Matrix (Test Data):\n", conf_matrix_logreg)
print("Accuracy:", accuracy_logreg)
print("Classification Report (Test Data):\n", report_logreg)

kf_logreg = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_logreg = cross_val_predict(best_logreg_model, X_train, y_train, cv=kf_logreg, method='predict_proba')[:, 1]

y_pred_cv_logreg = cross_val_predict(best_logreg_model, X_train, y_train, cv=kf_logreg)
conf_matrix_cv_logreg = confusion_matrix(y_train, y_pred_cv_logreg)
accuracy_cv_logreg = accuracy_score(y_train, y_pred_cv_logreg)
report_cv_logreg = classification_report(y_train, y_pred_cv_logreg)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_logreg)
print("Cross-Validation Accuracy:", accuracy_cv_logreg)
print("Classification Report (Cross-Validation):\n", report_cv_logreg)

#Calculation of ROC Curve metrics and graph plotting
fpr_logreg, tpr_logreg, _ = roc_curve(y_test, y_prob_test_logreg, pos_label = 2)
roc_auc_logreg = auc(fpr_logreg, tpr_logreg)

plt.figure(figsize=(8, 8))
plt.plot(fpr_logreg, tpr_logreg, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_logreg))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()
fpr_cv_logreg, tpr_cv_logreg, _ = roc_curve(y_train, y_prob_cv_logreg, pos_label = 2)
roc_auc_cv_logreg = auc(fpr_cv_logreg, tpr_cv_logreg)
plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_logreg, tpr_cv_logreg, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_logreg))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

#FEATURE IMPORTANCE LOGISTIC REGRESSION
model = best_logreg_model.fit(X_train, y_train)
coefficients = model.coef_[0]
feature_importance_lr = pd.DataFrame({'Feature': X.columns, 'Importance': np.abs(coefficients)})
feature_importance_lr = feature_importance_lr.sort_values('Importance', ascending=True)
colors = plt.cm.plasma(np.linspace(0.2, 1, len(feature_importance_lr)))
plt.figure(figsize=(10, 6))
bars = plt.barh(feature_importance_lr['Feature'], feature_importance_lr['Importance'], color=colors)
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, round(bar.get_width(), 4),
             va='center', ha='left', fontsize=10, color='white')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.gca().set_facecolor('white')
plt.tight_layout()

plt.show()

"""# SVM"""

param_grid = {
    'C': [0.001, 0.1, 0.9, 1.5, 2.3,23, 50, 100],
    'kernel': ['linear','rbf'],
    'gamma': ['auto','scale']
}

svc_model = SVC(random_state=RANDOM_STATE, probability=True)
grid_search = GridSearchCV(estimator=svc_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_svc_model = grid_search.best_estimator_
best_svc_model.fit(X_train, y_train)
y_pred_test_svc = best_svc_model.predict(X_test)
y_prob_test_svc = best_svc_model.predict_proba(X_test)[:, 1]
conf_matrix_svc = confusion_matrix(y_test, y_pred_test_svc)
accuracy_svc = accuracy_score(y_test, y_pred_test_svc)
report_svc = classification_report(y_test, y_pred_test_svc)

print("Confusion Matrix (Test Data):\n", conf_matrix_svc)
print("Accuracy:", accuracy_svc)
print("Classification Report (Test Data):\n", report_svc)
kf_svc = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_svc = cross_val_predict(best_svc_model, X_train, y_train, cv=kf_svc, method='predict_proba')[:, 1]

y_pred_cv_svc = cross_val_predict(best_svc_model, X_train, y_train, cv=kf_svc)
conf_matrix_cv_svc = confusion_matrix(y_train, y_pred_cv_svc)
accuracy_cv_svc = accuracy_score(y_train, y_pred_cv_svc)
report_cv_svc = classification_report(y_train, y_pred_cv_svc)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_svc)
print("Cross-Validation Accuracy:", accuracy_cv_svc)
print("Classification Report (Cross-Validation):\n", report_cv_svc)

#Calculation of ROC Curve metrics and graph plotting
fpr_svc, tpr_svc, _ = roc_curve(y_test, y_prob_test_svc, pos_label = 2)
roc_auc_svc = auc(fpr_svc, tpr_svc)

plt.figure(figsize=(8, 8))
plt.plot(fpr_svc, tpr_svc, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_svc))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()
# Plotar a curva ROC para a validação cruzada
fpr_cv_svc, tpr_cv_svc, _ = roc_curve(y_train, y_prob_cv_svc, pos_label = 2)
roc_auc_cv_svc = auc(fpr_cv_svc, tpr_cv_svc)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_svc, tpr_cv_svc, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_svc))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

"""# KNN"""

param_grid = {
   'n_neighbors': [1, 3, 5, 7, 10, 15, 100, 1000],
    'weights': ['uniform', 'distance'],
    'p': [0.001, 0.1, 1, 3, 5, 7, 10, 15, 100, 1000],
    'leaf_size': [0.001, 0.1, 1, 3, 5, 7, 10, 15, 100, 1000]
}

knn_model = KNeighborsClassifier()
grid_search = GridSearchCV(estimator=knn_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_knn_model = grid_search.best_estimator_
best_knn_model.fit(X_train, y_train)
y_pred_test_knn = best_knn_model.predict(X_test)
y_prob_test_knn = best_knn_model.predict_proba(X_test)[:, 1]
conf_matrix_knn = confusion_matrix(y_test, y_pred_test_knn)
accuracy_knn = accuracy_score(y_test, y_pred_test_knn)
report_knn = classification_report(y_test, y_pred_test_knn)

print("Confusion Matrix (Test Data):\n", conf_matrix_knn)
print("Accuracy:", accuracy_knn)
print("Classification Report (Test Data):\n", report_knn)

kf_knn = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_knn = cross_val_predict(best_knn_model, X_train, y_train, cv=kf_knn, method='predict_proba')[:, 1]

y_pred_cv_knn = cross_val_predict(best_knn_model, X_train, y_train, cv=kf_knn)
conf_matrix_cv_knn = confusion_matrix(y_train, y_pred_cv_knn)
accuracy_cv_knn = accuracy_score(y_train, y_pred_cv_knn)
report_cv_knn = classification_report(y_train, y_pred_cv_knn)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_knn)
print("Cross-Validation Accuracy:", accuracy_cv_knn)
print("Classification Report (Cross-Validation):\n", report_cv_knn)

#Calculation of ROC Curve metrics and graph plotting
fpr_knn, tpr_knn, _ = roc_curve(y_test, y_prob_test_knn, pos_label = 2)
roc_auc_knn = auc(fpr_knn, tpr_knn)

plt.figure(figsize=(8, 8))
plt.plot(fpr_knn, tpr_knn, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_knn))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()

fpr_cv_knn, tpr_cv_knn, _ = roc_curve(y_train, y_prob_cv_knn, pos_label = 2)
roc_auc_cv_knn = auc(fpr_cv_knn, tpr_cv_knn)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_knn, tpr_cv_knn, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_knn))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

"""# MLP CLASSIFIER"""

param_grid = {
    'hidden_layer_sizes': [10, 100, 1000],
    'alpha': [ 0.01, 0.1, 1.0],
    'learning_rate_init': [0.01, 0.1, 1],
    'activation': ['relu', 'logistic', 'tanh'],
    'max_iter': [50, 100, 1000],
    'solver': ['lbfgs', 'sgd', 'adam']
}

mlp_model = MLPClassifier(random_state=RANDOM_STATE)

grid_search = GridSearchCV(estimator=mlp_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_mlp_model = grid_search.best_estimator_
best_mlp_model.fit(X_train, y_train)
y_pred_test_mlp = best_mlp_model.predict(X_test)
y_prob_test_mlp = best_mlp_model.predict_proba(X_test)[:, 1]
conf_matrix_mlp = confusion_matrix(y_test, y_pred_test_mlp)
accuracy_mlp = accuracy_score(y_test, y_pred_test_mlp)
report_mlp = classification_report(y_test, y_pred_test_mlp)

print("Confusion Matrix (Test Data):\n", conf_matrix_mlp)
print("Accuracy:", accuracy_mlp)
print("Classification Report (Test Data):\n", report_mlp)

kf_mlp = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_mlp = cross_val_predict(best_mlp_model, X_train, y_train, cv=kf_mlp, method='predict_proba')[:, 1]

y_pred_cv_mlp = cross_val_predict(best_mlp_model, X_train, y_train, cv=kf_mlp)
conf_matrix_cv_mlp = confusion_matrix(y_train, y_pred_cv_mlp)
accuracy_cv_mlp = accuracy_score(y_train, y_pred_cv_mlp)
report_cv_mlp = classification_report(y_train, y_pred_cv_mlp)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_mlp)
print("Cross-Validation Accuracy:", accuracy_cv_mlp)
print("Classification Report (Cross-Validation):\n", report_cv_mlp)

#Calculation of ROC Curve metrics and graph plotting
fpr_mlp, tpr_mlp, _ = roc_curve(y_test, y_prob_test_mlp, pos_label = 2)
roc_auc_mlp = auc(fpr_mlp, tpr_mlp)
plt.figure(figsize=(8, 8))
plt.plot(fpr_mlp, tpr_mlp, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_mlp))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()

fpr_cv_mlp, tpr_cv_mlp, _ = roc_curve(y_train, y_prob_cv_mlp, pos_label = 2)
roc_auc_cv_mlp = auc(fpr_cv_mlp, tpr_cv_mlp)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_mlp, tpr_cv_mlp, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_mlp))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

"""# DECISION TREE"""

param_grid = {
    'criterion': ['gini', 'entropy'],
    'splitter': ['best', 'random'],
    'max_depth': [None, 5, 10, 15],
}

tree_clf = DecisionTreeClassifier(random_state=RANDOM_STATE)
grid_search = GridSearchCV(estimator=tree_clf, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_tree_clf = grid_search.best_estimator_
best_tree_clf.fit(X_train, y_train)
y_pred_test_dt = best_tree_clf.predict(X_test)
conf_matrix = confusion_matrix(y_test, y_pred_test_dt)
accuracy_dt = accuracy_score(y_test, y_pred_test_dt)
report = classification_report(y_test, y_pred_test_dt)

print("Confusion Matrix (Test Data):\n", conf_matrix)
print("Accuracy:", accuracy_dt)
print("Classification Report (Test Data):\n", report)
kf_dt = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_pred_cv_dt = cross_val_predict(best_tree_clf, X_train, y_train, cv=kf_dt)
conf_matrix_cv = confusion_matrix(y_train, y_pred_cv_dt)
accuracy_cv_dt = accuracy_score(y_train, y_pred_cv_dt)
report_cv = classification_report(y_train, y_pred_cv_dt)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv)
print("Cross-Validation Accuracy:", accuracy_cv_dt)
print("Classification Report (Cross-Validation):\n", report_cv)

#Calculation of ROC Curve metrics and graph plotting

from sklearn.model_selection import StratifiedKFold
def plot_roc_curve(fpr, tpr, auc_score, title='Receiver Operating Characteristic'):
    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(auc_score))
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc='lower right')
    plt.show()
y_prob_test_dt = best_tree_clf.predict_proba(X_test)[:, 1]
fpr_dt, tpr_dt, _ = roc_curve(y_test, y_prob_test_dt, pos_label = 2)
roc_auc_dt = auc(fpr_dt, tpr_dt)
plot_roc_curve(fpr_dt, tpr_dt, roc_auc_dt, title='ROC - Decision Tree - Test Data')
kf_dt = StratifiedKFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_dt = cross_val_predict(best_tree_clf, X_train, y_train, cv=kf_dt, method='predict_proba')[:, 1]
fpr_cv_dt, tpr_cv_dt, _ = roc_curve(y_train, y_prob_cv_dt, pos_label = 2)
roc_auc_cv_dt = auc(fpr_cv_dt, tpr_cv_dt)
plot_roc_curve(fpr_cv_dt, tpr_cv_dt, roc_auc_cv_dt, title='ROC - Decision Tree - Cross-Validation')

#FEATURE IMPORTANCE DECISION TREE
X_2 = []
X_2
features_2 =[]
imp_features_dt2 = []
df_imp_features_dt2 = []
X_2 = df.drop('sex', axis=1)
features_2 = []

for column in X_2.columns:
    features_2.append(column)

imp_features_dt2 = best_tree_clf.feature_importances_
df_imp_features_dt2 = pd.DataFrame({"features": features_2, "weights": imp_features_dt2})
df_imp_features_dt2_sorted = df_imp_features_dt2.sort_values(by='weights', ascending=True)
plt.figure(figsize=(10, 6))
colors = plt.cm.cividis(np.linspace(0.2, 1, len(df_imp_features_dt2_sorted)))
bars = plt.barh(df_imp_features_dt2_sorted['features'], df_imp_features_dt2_sorted['weights'], color=colors)
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, round(bar.get_width(), 4),
             va='center', ha='left', fontsize=10, color='white')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.gca().set_facecolor('white')
plt.tight_layout()

plt.show()

"""# RANDOM FOREST"""

param_grid = {
    'n_estimators': [5, 50, 200],
    'max_depth': [0, 10, 20],
    'min_samples_split': [2, 10, 15],
    'min_samples_leaf': [1, 4, 6],
    'max_features': ['auto', 'sqrt'],
    'criterion': ['gini', 'entropy']
}

rf_model = RandomForestClassifier(random_state=RANDOM_STATE)
grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)
best_rf_model = grid_search.best_estimator_
best_rf_model.fit(X_train, y_train)
y_pred_test_rf = best_rf_model.predict(X_test)
y_prob_test_rf = best_rf_model.predict_proba(X_test)[:, 1]
conf_matrix_rf = confusion_matrix(y_test, y_pred_test_rf)
accuracy_rf = accuracy_score(y_test, y_pred_test_rf)
report_rf = classification_report(y_test, y_pred_test_rf)

print("Confusion Matrix (Test Data):\n", conf_matrix_rf)
print("Accuracy:", accuracy_rf)
print("Classification Report (Test Data):\n", report_rf)

kf_rf = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_prob_cv_rf = cross_val_predict(best_rf_model, X_train, y_train, cv=kf_rf, method='predict_proba')[:, 1]

y_pred_cv_rf = cross_val_predict(best_rf_model, X_train, y_train, cv=kf_rf)
conf_matrix_cv_rf = confusion_matrix(y_train, y_pred_cv_rf)
accuracy_cv_rf = accuracy_score(y_train, y_pred_cv_rf)
report_cv_rf = classification_report(y_train, y_pred_cv_rf)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv_rf)
print("Cross-Validation Accuracy:", accuracy_cv_rf)
print("Classification Report (Cross-Validation):\n", report_cv_rf)

#Calculation of ROC Curve metrics and graph plotting

fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_test_rf, pos_label = 2)
roc_auc_rf = auc(fpr_rf, tpr_rf)

plt.figure(figsize=(8, 8))
plt.plot(fpr_rf, tpr_rf, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_rf))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()
fpr_cv_rf, tpr_cv_rf, _ = roc_curve(y_train, y_prob_cv_rf, pos_label = 2)
roc_auc_cv_rf = auc(fpr_cv_rf, tpr_cv_rf)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_rf, tpr_cv_rf, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_rf))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

#FEATURE IMPORTANCE RANDOM FOREST CLASSIFIER

X_3 = df.drop('sex', axis=1)
features_3 = []

for column in X_3.columns:
    features_3.append(column)

imp_features_dt3 = best_rf_model.feature_importances_
df_imp_features_dt3 = pd.DataFrame({"features": features_3, "weights": imp_features_dt3})
df_imp_features_dt3_sorted = df_imp_features_dt3.sort_values(by='weights', ascending=True)
plt.figure(figsize=(10, 6))
colors = plt.cm.inferno(np.linspace(0.2, 1, len(df_imp_features_dt3_sorted)))
bars = plt.barh(df_imp_features_dt3_sorted['features'], df_imp_features_dt3_sorted['weights'], color=colors)
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')
for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, round(bar.get_width(), 4),
             va='center', ha='left', fontsize=10, color='white')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.gca().set_facecolor('white')
plt.tight_layout()

plt.show()

"""#**Adaboosting**"""

from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, cross_val_predict, KFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Definindo os hiperparâmetros para o AdaBoost
param_grid = {
    'n_estimators': [5, 50, 200],
    'learning_rate': [0.01, 0.1, 1.0],
    'base_estimator__max_depth': [1, 2, 3],  # Usando DecisionTreeClassifier como base
    'base_estimator__min_samples_split': [2, 10, 15],
    'base_estimator__min_samples_leaf': [1, 4, 6]
}

# Criando o classificador base
base_clf = DecisionTreeClassifier(random_state=RANDOM_STATE)

# Criando o classificador AdaBoost com o classificador base
ada_clf = AdaBoostClassifier(base_estimator=base_clf, random_state=RANDOM_STATE)

# GridSearchCV para encontrar os melhores hiperparâmetros
grid_search = GridSearchCV(estimator=ada_clf, param_grid=param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Exibindo os melhores parâmetros e a melhor pontuação
print("Best Parameters:", grid_search.best_params_)
print("Best Score:", grid_search.best_score_)

# Treinando o modelo com os melhores parâmetros
best_ada_clf = grid_search.best_estimator_
best_ada_clf.fit(X_train, y_train)

# Fazendo previsões no conjunto de teste
y_pred_test_ada = best_ada_clf.predict(X_test)
y_prob_test_ada = best_ada_clf.predict_proba(X_test)[:, 1]
# Calculando e exibindo a matriz de confusão e a acurácia
conf_matrix = confusion_matrix(y_test, y_pred_test_ada)
accuracy_ada = accuracy_score(y_test, y_pred_test_ada)
report = classification_report(y_test, y_pred_test_ada)

print("Confusion Matrix (Test Data):\n", conf_matrix)
print("Accuracy:", accuracy_ada)
print("Classification Report (Test Data):\n", report)

# Cross-Validation
kf_ada = KFold(n_splits=fold, shuffle=True, random_state=RANDOM_STATE)
y_pred_cv_ada = cross_val_predict(best_ada_clf, X_train, y_train, cv=kf_ada)
y_prob_cv_ada = cross_val_predict(best_ada_clf, X_train, y_train, cv=kf_ada, method='predict_proba')[:, 1]
# Calculando e exibindo a matriz de confusão e a acurácia para Cross-Validation
conf_matrix_cv = confusion_matrix(y_train, y_pred_cv_ada)
accuracy_cv_ada = accuracy_score(y_train, y_pred_cv_ada)
report_cv = classification_report(y_train, y_pred_cv_ada)

print("Confusion Matrix (Cross-Validation):\n", conf_matrix_cv)
print("Cross-Validation Accuracy:", accuracy_cv_ada)
print("Classification Report (Cross-Validation):\n", report_cv)

fpr_ada, tpr_ada, _ = roc_curve(y_test, y_prob_test_ada, pos_label = 2)
roc_auc_ada = auc(fpr_ada, tpr_ada)

plt.figure(figsize=(8, 8))
plt.plot(fpr_ada, tpr_ada, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_ada))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Test Data')
plt.legend(loc='lower right')
plt.show()
fpr_cv_ada, tpr_cv_ada, _ = roc_curve(y_train, y_prob_cv_ada, pos_label = 2)
roc_auc_cv_ada = auc(fpr_cv_ada, tpr_cv_ada)

plt.figure(figsize=(8, 8))
plt.plot(fpr_cv_ada, tpr_cv_ada, color='darkorange', lw=2, label='ROC curve (area = {:.2f})'.format(roc_auc_cv_ada))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic - Cross-Validation')
plt.legend(loc='lower right')
plt.show()

#FEATURE IMPORTANCE - ADABOOSTING

X_3 = df.drop('sex', axis=1)
features_3 = X_3.columns.tolist()
imp_features_ada = best_ada_clf.feature_importances_

df_imp_features_ada = pd.DataFrame({"features": features_3, "weights": imp_features_ada})
df_imp_features_ada_sorted = df_imp_features_ada.sort_values(by='weights', ascending=True)

plt.figure(figsize=(10, 6))
colors = plt.cm.inferno(np.linspace(0.2, 1, len(df_imp_features_ada_sorted)))
bars = plt.barh(df_imp_features_ada_sorted['features'], df_imp_features_ada_sorted['weights'], color=colors)
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importance')

for bar in bars:
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, round(bar.get_width(), 4),
             va='center', ha='left', fontsize=10, color='white')

plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.gca().set_facecolor('white')
plt.tight_layout()

plt.show()

"""# Plot-ROC"""

plt.style.use('seaborn-whitegrid')
fig, axs = plt.subplots(1, 2, figsize=(20, 8))  # Criando subplots com 1 linha e 2 colunas

axs[0].plot(fpr_logreg, tpr_logreg, color='red', lw=2, label='Logistic Regression (AUC = %0.2f)' % roc_auc_logreg)
axs[0].plot(fpr_ada, tpr_ada, color='red', lw=2, label='Adaboosting Classifier (AUC = %0.2f)' % roc_auc_ada)
axs[0].plot(fpr_rf, tpr_rf, color='deeppink', lw=2, label='Random Forest (AUC = %0.2f)' % roc_auc_rf)
axs[0].plot(fpr_gb, tpr_gb, color='orange', lw=2, label='Gradient Boosting (AUC = %0.2f)' % roc_auc_gb)
axs[0].plot(fpr_mlp, tpr_mlp, color='purple', lw=2, label='Multilayer Perceptron (AUC = %0.2f)' % roc_auc_mlp)
axs[0].plot(fpr_dt, tpr_dt, color='gray', lw=2, label='Decision Tree (AUC = %0.2f)' % roc_auc_dt)
axs[0].plot(fpr_svc, tpr_svc, color='green', lw=2, label='Support Vector Machine (AUC = %0.2f)' % roc_auc_svc)
axs[0].plot(fpr_knn, tpr_knn, color='blue', lw=2, label='K Nearest Neighbors (AUC = %0.2f)' % roc_auc_knn)



axs[0].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
axs[0].set_xlim([0.0, 1.0])
axs[0].set_ylim([0.0, 1.05])
axs[0].set_xlabel('False Positive Rate')
axs[0].set_ylabel('True Positive Rate')
axs[0].set_title('Receiver Operating Characteristic (ROC) Curve')
axs[0].legend(loc="lower right")
axs[1].plot(fpr_cv_rf, tpr_cv_rf, color='deeppink', lw=2, label='Random Forest (AUC = %0.2f)' % roc_auc_cv_rf)
axs[1].plot(fpr_cv_gb, tpr_cv_gb, color='orange', lw=2, label='Gradient Boosting (AUC = %0.2f)' % roc_auc_cv_gb)
axs[1].plot(fpr_cv_logreg, tpr_cv_logreg, color='red', lw=2, label='Logistic Regression (AUC = %0.2f)' % roc_auc_cv_logreg)
axs[1].plot(fpr_cv_ada, tpr_cv_ada, color='orange', lw=2, label='Adaboosting Classifier (AUC = %0.2f)' % roc_auc_cv_ada)
axs[1].plot(fpr_cv_mlp, tpr_cv_mlp, color='purple', lw=2, label='Multilayer Perceptron (AUC = %0.2f)' % roc_auc_cv_mlp)
axs[1].plot(fpr_cv_svc, tpr_cv_svc, color='green', lw=2, label='Support Vector Machine (AUC = %0.2f)' % roc_auc_cv_svc)
axs[1].plot(fpr_cv_knn, tpr_cv_knn, color='blue', lw=2, label='K Nearest Neighbors (AUC = %0.2f)' % roc_auc_cv_knn)
axs[1].plot(fpr_cv_dt, tpr_cv_dt, color='gray', lw=2, label='Decision Tree (AUC = %0.2f)' % roc_auc_cv_dt)

axs[1].plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
axs[1].set_xlim([0.0, 1.0])
axs[1].set_ylim([0.0, 1.05])
axs[1].set_xlabel('False Positive Rate')
axs[1].set_ylabel('True Positive Rate')
axs[1].set_title('Receiver Operating Characteristic (ROC) Curve')
axs[1].legend(loc="lower right")
axs[0].set_title('Receiver Operating Characteristic - Test Data')
axs[1].set_title('Receiver Operating Characteristic - Cross-Validation (5-Folds)')
plt.savefig('ROCCURVE.jpg', dpi=600, bbox_inches='tight')
plt.show()

###FEATURE IMPORTANCE

X = df.drop('sex', axis=1)
features = X.columns

colors = plt.cm.magma(np.linspace(0.2, 0.8, 5))  # Adicionei uma cor extra para evitar repetição

imp_features_gb = best_gb_model.feature_importances_
imp_features_lr = np.abs(best_logreg_model.coef_[0])
imp_features_dt = best_tree_clf.feature_importances_
imp_features_rf = best_rf_model.feature_importances_
imp_features_ada = best_ada_clf.feature_importances_  # Adicionando importância das features do AdaBoost

sorted_indices_gb = np.argsort(imp_features_gb)
sorted_indices_lr = np.argsort(imp_features_lr)
sorted_indices_dt = np.argsort(imp_features_dt)
sorted_indices_rf = np.argsort(imp_features_rf)
sorted_indices_ada = np.argsort(imp_features_ada)  # Ordenando para AdaBoost

fig, axs = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Feature Importance', fontsize=16)

# PLOT 1: Gradient Boosting
axs[0, 0].barh(features[sorted_indices_gb], imp_features_gb[sorted_indices_gb], color=colors[0])
axs[0, 0].set_title('Gradient Boosting')
axs[0, 0].set_xlabel('Importance')
axs[0, 0].set_ylabel('Feature')
axs[0, 0].grid(axis='x', linestyle='--', alpha=0.7)
axs[0, 0].set_facecolor('#f0f0f0')  # Cinza claro

# PLOT 2: Logistic Regression
axs[0, 1].barh(features[sorted_indices_lr], imp_features_lr[sorted_indices_lr], color=colors[1])
axs[0, 1].set_title('Logistic Regression')
axs[0, 1].set_xlabel('Importance')
axs[0, 1].set_ylabel('Feature')
axs[0, 1].grid(axis='x', linestyle='--', alpha=0.7)
axs[0, 1].set_facecolor('#f0f0f0')  # Cinza claro

# PLOT 3: Decision Tree
axs[0, 2].barh(features[sorted_indices_dt], imp_features_dt[sorted_indices_dt], color=colors[2])
axs[0, 2].set_title('Decision Tree')
axs[0, 2].set_xlabel('Importance')
axs[0, 2].set_ylabel('Feature')
axs[0, 2].grid(axis='x', linestyle='--', alpha=0.7)
axs[0, 2].set_facecolor('#f0f0f0')  # Cinza claro

# PLOT 4: Random Forest
axs[1, 0].barh(features[sorted_indices_rf], imp_features_rf[sorted_indices_rf], color=colors[3])
axs[1, 0].set_title('Random Forest')
axs[1, 0].set_xlabel('Importance')
axs[1, 0].set_ylabel('Feature')
axs[1, 0].grid(axis='x', linestyle='--', alpha=0.7)
axs[1, 0].set_facecolor('#f0f0f0')  # Cinza claro

# PLOT 5: Adaboosting
axs[1, 1].barh(features[sorted_indices_ada], imp_features_ada[sorted_indices_ada], color=colors[4])  # Usando a cor extra
axs[1, 1].set_title('AdaBoost')
axs[1, 1].set_xlabel('Importance')
axs[1, 1].set_ylabel('Feature')
axs[1, 1].grid(axis='x', linestyle='--', alpha=0.7)
axs[1, 1].set_facecolor('#f0f0f0')  # Cinza claro

fig.delaxes(axs[1, 2])

plt.tight_layout(rect=[0, 0, 1, 0.96], h_pad=1.5)

plt.savefig('FEATUREIMPORTANCE.jpg', dpi=300, bbox_inches='tight')
plt.show()