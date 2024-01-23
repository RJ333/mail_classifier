import pandas as pd
import json
import logging
import time
import nltk
from pathlib import Path

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


def read_emails():
    spam_json = Path("/mnt/c/wsl_shared/enron", "cleaned_spam_emails.json")
    ham_json = Path("/mnt/c/wsl_shared/enron", "cleaned_ham_emails.json")
    # ham_json = Path("/home/rjanssen/Mail/", "cleaned_good_emails.json")

    log.info("Reading jsons")
    with open(ham_json) as file:
        ham_mails_dict = json.load(file)
    with open(spam_json) as file:
        spam_mails_dict = json.load(file)
    log.info("Done, read in %d items", len(ham_mails_dict) + len(spam_mails_dict))
    return ham_mails_dict, spam_mails_dict


def combine_emails(dict1, dict2):
    all_mails = {**dict1, **dict2}
    return list(all_mails.values())


def create_features(mails):
    mail_features = []
    for mail in mails:
        text = (
            mail["payload_stem_texts"][0].split(" ")
            if isinstance(mail["payload_stem_texts"], list)
            else mail["payload_stem_texts"].split(" ")
        )
        new = mail.copy()  # otherwise we modify the original dict
        del new["Subject"]
        del new["payload_texts"]

        new["subject_stem_len"] = len(mail["Subject_stem"].split(" "))
        new["text_stem_uniq_len"] = len(set(text))
        new["text_stem_len"] = len(text)
        new["text_diversity"] = round(
            (len(set(text)) / len(text)) * 100, 1
        )  # the higher the value, the more words occur only once
        freqdist = nltk.FreqDist(text)
        new["most_common_5"] = freqdist.most_common(5)

        mail_features.append(new)

    return mail_features


def get_labels(mail_features):
    return [mail["label"] for mail in mail_features]


def reduce_email_props(mail_features):
    reduced_mails = []
    most_common_5 = []
    for mail in mail_features:
        reduced_mail = {
            "subject_stem_len": mail["subject_stem_len"],
            "text_stem_len": mail["text_stem_len"],
            "text_stem_uniq_len": mail["text_stem_uniq_len"],
            "text_diversity": mail["text_diversity"],
        }
        reduced_mails.append(reduced_mail)
        most_common_5.append(mail["most_common_5"])
    return reduced_mails, most_common_5


def produce_df(reduced_mails, most_common_5):
    # turn dict into dataframe
    reduced_df = pd.DataFrame(reduced_mails)
    # some data wrangling to make use of the word frequency tuple
    word_list = []
    count_list = []
    for twenty in most_common_5:
        list1, list2 = zip(*twenty)
        word_list.append(list1)
        count_list.append(list2)

    common_dict_list = []  # this is dictionary with top5 word:count per email
    for item in range(len(word_list)):
        common_dict_list.append(dict(zip(word_list[item], count_list[item])))
    # each word becomes a feature
    common_df = pd.DataFrame(common_dict_list)
    # combine the most common word frequencies with the other features
    combined_df = reduced_df.join(common_df).fillna(0)
    return combined_df


def write_to_file(df, labels):
    folder = Path("/mnt/c/wsl_shared/enron")
    labels_path = folder / "labels"
    df_path = folder / "mails.csv"

    log.info("writing labels")
    with open(labels_path, "w") as file:
        json.dump(labels, file)

    log.info("writing dateframe")
    df.to_csv(df_path, sep=",", index=False)


start_time = time.monotonic()
good_mails_dict, spam_mails_dict = read_emails()
mails = combine_emails(good_mails_dict, spam_mails_dict)
mail_features = create_features(mails)
labels = get_labels(mail_features)
reduced_mails, most_common_5 = reduce_email_props(mail_features)
combined_df = produce_df(reduced_mails, most_common_5)
write_to_file(combined_df, labels)

end_time = time.monotonic()
log.info("Creating features done, elapsed time %ss", round(end_time - start_time, 1))
