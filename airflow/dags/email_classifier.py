from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    "email_classifier",
    default_args={
        "depends_on_past": False,
        "email": ["rjanssen@barracuda.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="Email DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 23),
    catchup=False,
    tags=["example"],
) as dag:
    """
    this is my dag docstring for the bash trial
    """
    get_ham_mails = BashOperator(
        task_id="ham_mails",
        bash_command="python /home/rjanssen/git/mail_classifier/src/mail_classifier/process_ham.py",
    )

    get_spam_mails = BashOperator(
        task_id="spam_mails",
        bash_command="python /home/rjanssen/git/mail_classifier/src/mail_classifier/process_spam.py",
    )

    create_features = BashOperator(
        task_id="features",
        bash_command="python /home/rjanssen/git/mail_classifier/src/mail_classifier/create_features.py",
    )
    classify_emails = BashOperator(
        task_id="classify",
        bash_command="python /home/rjanssen/git/mail_classifier/src/mail_classifier/classification.py",
    )
    display_results = BashOperator(
        task_id="display_results",
        # space at the end or jinja template error!
        # file needs chmod +x
        bash_command="/home/rjanssen/git/mail_classifier/src/mail_classifier/display_results.sh ",
    )
    dag.doc_md = (
        __doc__  # providing that you have a docstring at the beginning of the DAG
    )

    (
        [get_ham_mails, get_spam_mails]
        >> create_features
        >> classify_emails
        >> display_results
    )
