"""
Standalone evaluation script for BullyMail.

Loads the large generated dataset, preprocesses it the same way the Flask
app does, trains a Linear SVM and a Logistic Regression model on a 70/30
split, and writes performance plots + the best-performing model to disk.

Run from the project directory:
    python evaluate_model.py
"""
import os

import joblib
import matplotlib
matplotlib.use('Agg')  # headless plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from app import Config, EmailAnalyzer

DATASET_FILENAME = 'large_email_dataset.xlsx'
STATIC_DIR = 'static'


def load_dataset():
    filepath = os.path.join(Config.DATASET_PATH, DATASET_FILENAME)
    df = pd.read_excel(filepath, sheet_name='Email Dataset')
    return df['email_content'].tolist(), df['label'].tolist()


def evaluate(model, X_test_tfidf, y_test):
    y_pred = model.predict(X_test_tfidf)
    return {
        'y_pred': y_pred,
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
    }


def plot_confusion_matrix(y_test, y_pred, out_path):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5), dpi=150)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Not Bullying', 'Bullying'],
                yticklabels=['Not Bullying', 'Bullying'])
    plt.title('SVM Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_model_comparison(svm_metrics, lr_metrics, out_path):
    metric_names = ['accuracy', 'precision', 'recall', 'f1_score']
    labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    svm_values = [svm_metrics[m] for m in metric_names]
    lr_values = [lr_metrics[m] for m in metric_names]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 6), dpi=150)
    plt.bar(x - width / 2, svm_values, width, label='Linear SVM')
    plt.bar(x + width / 2, lr_values, width, label='Logistic Regression')
    plt.xticks(x, labels)
    plt.ylim(0, 1.05)
    plt.ylabel('Score')
    plt.title('Model Performance Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    os.makedirs(STATIC_DIR, exist_ok=True)
    os.makedirs(Config.MODEL_PATH, exist_ok=True)

    print("Loading dataset...")
    emails, labels = load_dataset()

    analyzer = EmailAnalyzer()
    print(f"Preprocessing {len(emails)} emails...")
    processed_emails = [analyzer.preprocess_text(email) for email in emails]

    X_train, X_test, y_train, y_test = train_test_split(
        processed_emails, labels, test_size=0.3, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(max_features=2000, stop_words='english', ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    print("Training Linear SVM...")
    svm_model = SVC(kernel='linear', probability=True, random_state=42)
    svm_model.fit(X_train_tfidf, y_train)
    svm_metrics = evaluate(svm_model, X_test_tfidf, y_test)

    print("Training Logistic Regression...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train_tfidf, y_train)
    lr_metrics = evaluate(lr_model, X_test_tfidf, y_test)

    print(f"SVM:                  accuracy={svm_metrics['accuracy']:.3f} "
          f"precision={svm_metrics['precision']:.3f} recall={svm_metrics['recall']:.3f} "
          f"f1={svm_metrics['f1_score']:.3f}")
    print(f"Logistic Regression:  accuracy={lr_metrics['accuracy']:.3f} "
          f"precision={lr_metrics['precision']:.3f} recall={lr_metrics['recall']:.3f} "
          f"f1={lr_metrics['f1_score']:.3f}")

    print("Saving plots...")
    plot_confusion_matrix(y_test, svm_metrics['y_pred'], os.path.join(STATIC_DIR, 'confusion_matrix.png'))
    plot_model_comparison(svm_metrics, lr_metrics, os.path.join(STATIC_DIR, 'model_comparison.png'))

    # Persist whichever model scored higher on F1 as the "latest" production model
    best_model, best_name = (svm_model, 'SVM') if svm_metrics['f1_score'] >= lr_metrics['f1_score'] else (lr_model, 'Logistic Regression')
    print(f"Saving best model ({best_name}) to {Config.MODEL_PATH}/...")
    joblib.dump(best_model, os.path.join(Config.MODEL_PATH, 'latest_model.joblib'))
    joblib.dump(vectorizer, os.path.join(Config.MODEL_PATH, 'latest_vectorizer.joblib'))

    print("Done.")


if __name__ == '__main__':
    main()
