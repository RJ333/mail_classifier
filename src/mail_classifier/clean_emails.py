import os
import email
import json
import logging
import time
import re
from bs4 import BeautifulSoup
from email import policy
from pathlib import Path

loglevel = logging.DEBUG
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)

html_regex = re.compile("<.*?>")


def clean_string(raw_string):
    cleanstring_spaces = raw_string.replace("=", "").replace("\n", "")
    cleanstring = " ".join(cleanstring_spaces.split())
    return cleanstring


def html_to_string(mailpart):
    htmlstring = mailpart.get_payload().replace("=", "")
    soup = BeautifulSoup(htmlstring)
    soup_text = soup.get_text()
    textstring = clean_string(soup_text)
    return textstring


def remove_html_tags(text: str) -> str:
    return " ".join(re.sub(html_regex, "", text).split())


def mail_to_dict_reduced(mails):
    mail_dicts = {}
    for mail_tuple in mails:
        subject = mail_tuple[1].get("Subject")
        maildate = mail_tuple[1].get("Date")
        isotimestamp = email.utils.parsedate_to_datetime(maildate).isoformat()
        mime_parts = [part.get_content_type() for part in mail_tuple[1].walk()]
        texts = []
        use_html = False
        for part in mail_tuple[1].walk():
            if part.get_content_subtype() == "alternative":
                continue
            if part.get_content_subtype() == "plain":
                plain_clean = clean_string(str(part.get_payload(decode=False)))
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
            cleaner_text = remove_html_tags(part_text)
            texts.append(cleaner_text)

        mail_dict = {
            "Received_date": isotimestamp,
            "Subject": subject,
            "payload_texts": texts,
            "label": mail_tuple[2],
        }
        mail_dicts[mail_tuple[0]] = mail_dict
    return mail_dicts


def mail_to_dict_full(mails):
    mail_dicts = {}
    for mail_tuple in mails:
        subject = mail_tuple[1].get("Subject")
        sender = mail_tuple[1].get("From")
        receiver = mail_tuple[1].get("To")
        maildate = mail_tuple[1].get("Date")
        isotimestamp = email.utils.parsedate_to_datetime(maildate).isoformat()
        cc = mail_tuple[1].get("Cc")
        n_parts = len(mail_tuple[1].get_charsets())
        mime_parts = [part.get_content_type() for part in mail_tuple[1].walk()]
        charset_parts = mail_tuple[1].get_charsets()
        texts = []
        use_html = False
        for part in mail_tuple[1].walk():
            if part.get_content_subtype() == "plain":
                plain_clean = clean_string(str(part.get_payload(decode=False)))
                if not plain_clean:
                    use_html = True
                else:
                    texts.append(plain_clean)
            if part.get_content_subtype() == "html" and "text/plain" not in mime_parts:
                texts.append(html_to_string(part))
            if use_html and part.get_content_subtype() == "html":
                texts.append(html_to_string(part))

        mail_dict = {
            "Sender": sender,
            "Receiver": receiver,
            "Received_date": isotimestamp,
            "CC": cc,
            "Subject": subject,
            "n_parts": n_parts,
            "mime_parts": mime_parts,
            "charset_parts": charset_parts,
            "payload_texts": texts,
            "label": mail_tuple[2],
        }
        mail_dicts[mail_tuple[0]] = mail_dict
    return mail_dicts


def main():
    start_time = time.monotonic()
    mail_dir = "/home/rjanssen/Mail"
    folder = "new"
    label = "normal_email"
    file_names = os.listdir(Path(mail_dir, folder))

    log.info("Reading emails")
    all_mails = []
    # create a tuple consisting of filename, the email and the label
    for mail in file_names:
        with open(Path(mail_dir, folder, mail)) as m:
            all_mails.append(
                (mail, email.message_from_file(m, policy=policy.default), label)
            )  # we could save time here if we had one tuple with many lists...

    log.info("Removing undesired emails by subject")
    mails = [mail for mail in all_mails if not "properties" in mail[1].get("Subject")]
    log.info("Length after removal: %d", len(mails))
    log.info("%d emails removed", len(all_mails) - len(mails))

    log.info("Processing %d emails", len(mails))
    processed_mails = mail_to_dict_reduced(mails)

    log.info("writing json to %s", mail_dir)
    with open(Path(mail_dir, "cleaned_good_emails.json"), "w", encoding="utf-8") as f:
        json.dump(processed_mails, f, ensure_ascii=False, indent=4)
    end_time = time.monotonic()
    log.info("Email processing done, elapsed time %ss", round(end_time - start_time, 1))


if __name__ == "__main__":
    main()
