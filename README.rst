===============
mail_classifier
===============

A set of bash and python scripts to classify email via Random Forest as spam or ham

the mail classifier takes either emails from the enron dataset or real emails from newsletters, cleans them, creates features and runs a Random Forest classification on them.

Usage
-----
for real email usage, you need to have the getmail lib installed and configured. Otherwise, just use the files from the enron data set, which you can find here http://nlp.cs.aueb.gr/software_and_datasets/Enron-Spam/index.html (preprocessed).
Then run the process_ham.py and process_spam.py (after adjusting the file paths), followed by classification.py, which will in turn call create_features.py
Now, you can also use the airflow pipeline:: bash
    source venv/bin/activate
    airflow standalone

    #(in another terminal)
    source venv/bin/activate
    airflow dags test email_classifier


Installation
------------
clone the repo and install the required packages


Requirements
^^^^^^^^^^^^

Development
-----------

ToDo
^^^^

Authors
-------

``mail_classifier`` was written by `Rene Janssen <rjanssen@barracuda.com>`_.
