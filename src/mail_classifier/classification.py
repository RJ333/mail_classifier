import logging
import json
import pandas as pd
from pathlib import Path
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)
folder = Path("/mnt/c/wsl_shared/enron")


def read_files(folder):
    folder = folder
    labels_path = folder / "labels"
    df_path = folder / "mails.csv"
    with open(labels_path) as file:
        labels = json.load(file)
    df = pd.read_csv(df_path)
    return labels, df


log.info("Reading files from %s", folder)
labels, my_data_set = read_files(folder)
features = my_data_set.columns
data = my_data_set.fillna(0).to_numpy()

log.info("Splitting data into train and test sets")
data_train, data_test, labels_train, labels_test = train_test_split(
    data, labels, test_size=0.30
)
RF = RandomForestClassifier(n_estimators=100)
log.info("Fitting training data to Random Forest model")
RF.fit(data_train, labels_train)
log.info("Predicting test data with trained model")
labels_pred = RF.predict(data_test)
result_metrics = {
    "Accuracy": round(metrics.accuracy_score(labels_test, labels_pred), 3),
    "Balanced accuracy": round(
        metrics.balanced_accuracy_score(labels_test, labels_pred), 3
    ),
    "F1": round(metrics.f1_score(labels_test, labels_pred, average="macro"), 3),
    "Precision": round(
        metrics.precision_score(labels_test, labels_pred, average="macro"), 3
    ),
}

for key, value in result_metrics.items():
    log.info("%s: %s", key, value)

# take the importance values and display them nicely
# mean decrease impurity (MDI)
feature_imp = (
    pd.Series(RF.feature_importances_, index=features)
    .sort_values(ascending=False)
    .nlargest(20)
    .round(3)
)
log.info("Feature importance:\n%s", feature_imp)
log.info("Writing results to %s", folder)

with open(folder / "result_metrics.json", "w") as file:
    json.dump(result_metrics, file)

feature_imp.to_json(folder / "feature_importance.json")
