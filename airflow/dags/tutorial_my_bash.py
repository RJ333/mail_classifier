import textwrap
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

with DAG(
    "tutorial_my_bash",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["rjanssen@barracuda.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="Testing email DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 21),
    catchup=False,
    tags=["example"],
) as dag:
    """
    this is my dag docstring for the bash trial
    """

    # a task needs owner and task_id...owner per default is "airflow"
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    task2 = BashOperator(task_id="sleeeeeep", bash_command="sleep 3")

    task3 = BashOperator(
        task_id="get_mail",
        depends_on_past=False,  # already set by DAG default args
        bash_command="getmail",
        retries=2,  # overriding DAG default args
    )
    task4 = BashOperator(
        task_id="process_real_emails",
        bash_command="python /home/rjanssen/git/mail_classifier/src/mail_classifier/process_real_emails.py",
    )

    dag.doc_md = (
        __doc__  # providing that you have a docstring at the beginning of the DAG
    )

    task1 >> task2 >> task3 >> task4
