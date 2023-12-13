import logging
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from create_features import combined_df, labels

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)

my_data_set = combined_df
features = my_data_set.columns
data = my_data_set.fillna(0).to_numpy()

data_train, data_test, labels_train, labels_test = train_test_split(
    data, labels, test_size=0.30
)
RF = RandomForestClassifier(n_estimators=100)
RF.fit(data_train, labels_train)
labels_pred = RF.predict(data_test)

log.info("Accuracy %s", round(metrics.accuracy_score(labels_test, labels_pred), 3))
log.info(
    "Balanced accuracy %s",
    round(metrics.balanced_accuracy_score(labels_test, labels_pred), 3),
)
log.info("F1 %s", round(metrics.f1_score(labels_test, labels_pred, average="macro"), 3))
log.info(
    "Precision %s",
    round(metrics.precision_score(labels_test, labels_pred, average="macro"), 3),
)

# take the importance values and display them nicely
# mean decrease impurity (MDI)
feature_imp = (
    pd.Series(RF.feature_importances_, index=features)
    .sort_values(ascending=False)
    .nlargest(20)
    .round(3)
)
log.info("Feature importance:\n%s", feature_imp)
