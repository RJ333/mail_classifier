#!/usr/bin/env bash
cd /home/rjanssen/git/mail_classifier
source ./venv/bin/activate
# config in ~/.getmailrc/getmailrc
# target folder in ~/Mail/
getmail
exit 0
