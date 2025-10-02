import logging
import requests
import json
from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.mysql.hooks.mysql import MySqlHook

logger = logging.getLogger(__name__)

def check_birthdays(**kwargs):
    """Check birthdays for the current date"""
    mysql_hook = MySqlHook(mysql_conn_id='birthday_db')
    
    today = datetime.now().strftime('%m-%d')
    logger.info(f"Checking birthdays for date: {today}")
    
    query = "SELECT name, birth_date FROM birthdays WHERE DATE_FORMAT(birth_date, '%%m-%%d') = %s"
    
    results = mysql_hook.get_records(query, parameters=(today,))

    birthdays = []
    for row in results:
        birthdays.append({'name': row[0], 'birth_date': row[1]})
    
    kwargs['ti'].xcom_push(key='birthdays', value=birthdays)
    logger.info(f"Found {len(birthdays)} birthdays today")
    
    return birthdays
    
def send_discord_notification(birthdays):
    """Send birthday reminder to Discord"""
    webhook_url = Variable.get("WEBHOOK_URL")
    if not webhook_url:
        logger.warning("No webhook URL configured")
        return False
    
    try:
        if birthdays:
            embed = {
                "title": "🎉 Birthday Reminders for Today!",
                "fields": [],
                "footer": {"text": "Coming From Birthday Reminder Pipeline"},
                "timestamp": datetime.now().isoformat()
            }
            
            for person in birthdays:
                age = ""
                if person.get('birth_date'):
                    birth_year = person['birth_date'].year
                    current_year = datetime.now().year
                    age = f"{current_year - birth_year}"
                
                embed["fields"].append({
                    "name": f"🎂 {person['name']}",
                    "value": f"It is their Birthday! (Turning {age} today!) \n",
                    "inline": False
                })
            
            payload = {"embeds": [embed]}
        else:
            payload = {"content": "No birthdays today! 📅"}
        
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        logger.info("Discord notification sent successfully")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {str(e)}")
        return False

def send_reminder(**kwargs):
    birthdays = kwargs['ti'].xcom_pull(key='birthdays', task_ids='check_birthdays_task')
    
    if birthdays:
        for person in birthdays:
            logger.info(f"Reminder: Today is {person['name']}'s birthday!")
    else:
        logger.info("No birthdays today.")
    
    success = send_discord_notification(birthdays)
    
    if success:
        logger.info("Discord notification sent successfully")
    else:
        logger.error("Failed to send Discord notification")
    
    return success

with DAG(
    dag_id='birthday_reminder',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Task - 1: Task for checking birthdays
    check_birthdays_task = PythonOperator(
        task_id='check_birthdays_task',
        python_callable=check_birthdays,
        provide_context=True
    )

    # Task - 2: Task for sending a reminder message on Discord
    send_reminder_task = PythonOperator(
        task_id='send_reminder_task',
        python_callable=send_reminder,
        provide_context=True
    )

    # Task Dependencies
    check_birthdays_task >> send_reminder_task