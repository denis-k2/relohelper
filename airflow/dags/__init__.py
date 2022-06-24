from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

from .operator import CurrencyScoopOperator


with DAG(
        dag_id='exchange_rate2',
        start_date=datetime(2022, 4, 27),
        schedule_interval='@daily',
        catchup=False,
) as dag:

    create_table = PostgresOperator(
        task_id='create_table_task',
        postgres_conn_id='pg_k2',
        sql='sql/create_table.sql'
    )

    tasks = []


    get_rate_task = CurrencyScoopOperator(
        task_id='get_rate',
        base_currency='USD',
        #currency=currency,
        conn_id='cur_scoop_conn_id',
        dag=dag,
        do_xcom_push=True,
    )
    
    insert_rate = PostgresOperator(
        task_id=f'insert_rate',
        postgres_conn_id='pg_k2',
        sql='sql/insert_rate.sql',
        params={
            'base_currency': 'USD',
            #'currency': currency,
            'get_rate_task_id': 'get_rate'
        }
    )

create_table >> get_rate_task >> insert_rate
