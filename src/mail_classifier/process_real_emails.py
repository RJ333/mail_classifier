import os
import email
import json
import logging
import time
import re
import string

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from bs4 import BeautifulSoup
from email import policy
from pathlib import Path

log_level = logging.DEBUG
logging.basicConfig(level=log_level)
log = logging.getLogger(__name__)

HTML_REGEX = re.compile("<.*?>", re.DOTALL)
LINK_REGEX = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

PS = PorterStemmer()
MAIL_DIR = "/home/rjanssen/Mail"
FOLDER = "new"
LABEL = "normal_email"


def clean_string(raw_string):
    cleanstring_spaces = raw_string.replace("=", "").replace("\n", "")
    cleanstring = " ".join(cleanstring_spaces.split())
    return cleanstring


def html_to_string(mailpart):
    htmlstring = mailpart.get_payload()
    soup = BeautifulSoup(htmlstring)
    soup_text = soup.get_text()
    return soup_text


def remove_html_tags(text: str) -> str:
    return " ".join(re.sub(HTML_REGEX, " ", text).split())


def exp_clean(text):
    text = text.lower()
    text = LINK_REGEX.sub("", text)
    text = re.sub(r"=\n", "", text)
    text = remove_html_tags(text)
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


def mail_to_dict_reduced(mails):
    mail_dicts = {}
    for mail_tuple in mails:
        clean_subject = exp_clean(mail_tuple[1].get("Subject"))
        stemmed_subject = stem_text(clean_subject)
        maildate = mail_tuple[1].get("Date")
        isotimestamp = email.utils.parsedate_to_datetime(maildate).isoformat()
        mime_parts = [part.get_content_type() for part in mail_tuple[1].walk()]
        texts = []
        stemmed_texts = []
        use_html = False

        for part in mail_tuple[1].walk():
            if part.get_content_subtype() == "alternative":
                continue
            if part.get_content_subtype() == "plain":
                plain_clean = str(part.get_payload(decode=False))
                if not plain_clean:
                    use_html = True
                else:
                    part_text = plain_clean
            if part.get_content_subtype() == "html" and "text/plain" in mime_parts:
                continue
            if part.get_content_subtype() == "html" and "text/plain" not in mime_parts:
                part_text = html_to_string(part)
            if use_html and part.get_content_subtype() == "html":
                part_text = html_to_string(part)
            words = exp_clean(part_text)
            # save here as all words
            stem_words = stem_text(words)
            texts.append(words)
            stemmed_texts.append(stem_words)

        mail_dict = {
            "Received_date": isotimestamp,
            "Subject": clean_subject,
            "Subject_stem": stemmed_subject,
            "payload_texts": texts,
            "payload_stem_texts": stemmed_texts,
            "label": mail_tuple[2],
        }
        mail_dicts[mail_tuple[0]] = mail_dict
    return mail_dicts


def main():
    start_time = time.monotonic()
    file_names = os.listdir(Path(MAIL_DIR, FOLDER))

    log.info("Reading %d emails", len(file_names))
    all_mails = []
    # create a tuple consisting of filename, the email and the label
    for mail in file_names:
        with open(Path(MAIL_DIR, FOLDER, mail)) as m:
            all_mails.append(
                (mail, email.message_from_file(m, policy=policy.default), LABEL)
            )  # we could save time here if we had one tuple with many lists...

    log.info("Removing undesired emails")
    mails1 = [
        mail for mail in all_mails if not "properties" in mail[1].get("Subject")
    ]  # hard to process
    mails = [
        mail for mail in mails1 if not "Frankfurter Allgemeine" in mail[1].get("From")
    ]  # German newspaper

    log.info("Length after removal: %d", len(mails))
    log.info("%d emails removed", len(all_mails) - len(mails))

    log.info("Processing %d emails", len(mails))
    processed_mails = mail_to_dict_reduced(mails)

    log.info("writing json to %s", MAIL_DIR)
    with open(Path(MAIL_DIR, "cleaned_good_emails.json"), "w", encoding="utf-8") as f:
        json.dump(processed_mails, f, ensure_ascii=False, indent=4)
    end_time = time.monotonic()
    log.info("Email processing done, elapsed time %ss", round(end_time - start_time, 1))


if __name__ == "__main__":
    main()
