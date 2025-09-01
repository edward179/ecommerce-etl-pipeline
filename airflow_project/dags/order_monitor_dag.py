from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'email': ['minhvo.study@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='order_monitor_dag',
    default_args=default_args,
    schedule='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    dbt_run = BashOperator(
        task_id='run_dbt_models',
        bash_command='source "/Users/quocminh/Documents/portfolio-projects/ecommerce_project_ETL/airflow_venv_3117/bin/activate" && cd "/Users/quocminh/Documents/portfolio-projects/ecommerce_project_ETL/dbt_ecommerce" && dbt run'
    )

    check_orders = BashOperator(
        task_id='check_delayed_orders',
        bash_command='source "/Users/quocminh/Documents/portfolio-projects/ecommerce_project_ETL/airflow_venv_3117/bin/activate" && python "/Users/quocminh/Documents/portfolio-projects/ecommerce_project_ETL/airflow_project/dags/utils/check_delayed_orders.py"'
    )

    dbt_run >> check_orders

