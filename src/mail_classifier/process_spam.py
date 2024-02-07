import os
import datetime
import json
import logging
import time
import random
import re
import string

from pathlib import Path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

log_level = logging.DEBUG
logging.basicConfig(level=log_level)
log = logging.getLogger(__name__)


PS = PorterStemmer()
PARENT_DIR = "/mnt/c/wsl_shared/enron/"
LABEL = "spam_email"


def exp_clean(text):
    text = text.replace("Subject: ", "")
    text = text.lower()
    text = re.sub(r"=\n", "", text)
    text = re.sub(r"[,.\"!@#$%^&*(){}?/;`~:<>+=-]", "", text)
    tokens = word_tokenize(text)
    table = str.maketrans("", "", string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words("english"))
    words = [word for word in words if not word in stop_words]
    words = " ".join(words)
    return words


def stem_text(words):
    words = [PS.stem(word) for word in words.split()]
    words = " ".join(words)
    return words


def mail_to_dict(mails):
    mail_dicts = {}
    for mail_tuple in mails:
        clean_subject = exp_clean(mail_tuple[1][0])
        stemmed_subject = stem_text(clean_subject)

        text = " ".join(mail_tuple[1][1:])
        words = exp_clean(text)
        stem_words = stem_text(words)

        mail_dict = {
            "Received_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "Subject": clean_subject,
            "Subject_stem": stemmed_subject,
            "payload_texts": words,
            "payload_stem_texts": stem_words,
            "label": mail_tuple[2],
        }
        mail_dicts[mail_tuple[0]] = mail_dict
    return mail_dicts


def main():
    start_time = time.monotonic()
    mail_dirs = [f"{PARENT_DIR}/enron{n}/spam" for n in range(1, 7)]
    all_file_names = [
        os.path.join(dir, file) for dir in mail_dirs for file in os.listdir(dir)
    ]
    file_names = random.sample(all_file_names, 1500)  # we have way too many spam emails

    log.info("Reading spam emails")
    all_mails = []
    # create a tuple consisting of filename, the email and the label
    for mail in file_names:
        print(mail)
        with open(mail, errors="ignore") as m:
            # we could save time here if we had one tuple with many lists...
            all_mails.append((mail, m.readlines(), LABEL))

    log.info("Processing %d emails", len(all_mails))
    processed_mails = mail_to_dict(all_mails)

    log.info("writing json to %s", PARENT_DIR)
    with open(Path(PARENT_DIR, "cleaned_spam_emails.json"), "w", encoding="utf-8") as f:
        json.dump(processed_mails, f, ensure_ascii=False, indent=4)
    end_time = time.monotonic()
    log.info("Email processing done, elapsed time %ss", round(end_time - start_time, 1))


if __name__ == "__main__":
    main()
