import os
import datetime
import json
import logging
import time

from pathlib import Path

loglevel = logging.DEBUG
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


def mail_to_dict(mails):
    mail_dicts = {}
    for mail_tuple in mails:
        subject = mail_tuple[1][0]

        mail_dict = {
            "Received_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "Subject": subject,
            "payload_texts": mail_tuple[1][1:],
            "label": mail_tuple[2],
        }
        mail_dicts[mail_tuple[0]] = mail_dict
    return mail_dicts


def main():
    start_time = time.monotonic()
    mail_dir = "/mnt/c/wsl_shared/enron/enron1"
    folder = "spam"
    label = "spam_email"
    file_names = os.listdir(Path(mail_dir, folder))

    log.info("Reading spam emails")
    all_mails = []
    # create a tuple consisting of filename, the email and the label
    for mail in file_names[:101]:
        with open(Path(mail_dir, folder, mail)) as m:
            all_mails.append(
                (mail, m.readlines(), label)
            )  # we could save time here if we had one tuple with many lists...

    log.info("Processing %d emails", len(all_mails))
    processed_mails = mail_to_dict(all_mails)

    log.info("writing json to %s", mail_dir)
    with open(Path(mail_dir, "cleaned_spam_emails.json"), "w", encoding="utf-8") as f:
        json.dump(processed_mails, f, ensure_ascii=False, indent=4)
    end_time = time.monotonic()
    log.info("Email processing done, elapsed time %ss", round(end_time - start_time, 1))


if __name__ == "__main__":
    main()
