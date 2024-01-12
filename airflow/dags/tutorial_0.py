import textwrap
from datetime import datetime, timedelta
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    "tutorial_0",
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
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 11),
    catchup=False,
    tags=["example"],
) as dag:
    """
    this is my dag docstring
    """

    # a task needs owner and task_id...owner per default is "airflow"
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    task2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,  # already set by DAG default args
        bash_command="sleep 5",
        retries=2,  # overriding DAG default args
    )

    templated_command = textwrap.dedent(
        # ds = date stamp
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """
    )

    task3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )

    task1.doc_md = textwrap.dedent(
        """\
#### Task Documentation
You can document your task using the attributes `doc_md`(markdown), `doc` (plain text)
`doc_rst`, `doc_json`, `doc_yaml` which gets rendered in the UI's task instance details page.
"""
    )
    dag.doc_md = (
        __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    )
    # otherwise, type it like this
    # dag.doc_md = """
    # This is a documentation placed anywhere
    # """

    # dependencies
    # task1.set_downstream(task2) # task2 is downstream of/depends on task1
    # task2.set_upstream(task1) # task1 is upstream of task2
    # task1 >> task2 # the same
    # task2 << task1 # the same

    # task1 >> task2 >> task3

    # task1 >> [task2, task3]
    task1.set_downstream([task2, task3])
