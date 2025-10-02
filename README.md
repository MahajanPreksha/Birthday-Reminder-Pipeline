# Birthday Reminder Pipeline
A data pipeline built with Apache Airflow that automatically checks for birthdays from a MySQL database and sends Discord notifications for daily birthday reminders.

## Description
This project implements an automated birthday reminder system using Apache Airflow. The pipeline runs daily to:
- Check for birthdays in a MySQL database
- Send formatted Discord notifications for people celebrating their birthday
- Calculate and display ages in the notifications

## Tech Stack
- **Apache Airflow** - Workflow orchestration
- **MySQL** - Birthday data storage
- **PostgreSQL 13** - Airflow metadata database
- **Docker** - Containerization
- **Python+** - Core programming language
- **Discord Webhooks** - Notification delivery

## Project Structure
```
Birthday-Reminder-Pipeline/
├── dags/
│   └── birthday-reminder.py    # Main Airflow DAG
├── logs/                       # Airflow execution logs
├── plugins/                    # Custom Airflow plugins
├── docker-compose.yaml         # Docker services configuration
├── Dockerfile                  # Custom Airflow image
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── LICENSE                     # MIT License
```

## Setup Instructions
### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM and 10GB disk space available
- Discord webhook URL for notifications

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Birthday-Reminder-Pipeline
```

### 2. Environment Configuration
The project includes a [`.env`](.env) file with default values:
```env
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

### 3. Build and Start Services
```bash
# Build the custom Airflow image
docker-compose build

# Start all services
docker-compose up -d
```

### 4. Access Airflow Web UI
- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### 5. Configure Database Connections
In the Airflow web UI, configure the MySQL connection:

1. Go to Admin → Connections
2. Create a new connection with ID: `birthday_db`
3. Set the following parameters:
   - Connection Type: MySQL
   - Host: `my-sql`
   - Schema: `birthday_db`
   - Login: `airflow`
   - Password: `airflow`
   - Port: 3306

### 6. Set Discord Webhook Variable
1. Go to Admin → Variables
2. Create a new variable:
    - Key: `NOTIFICATION_METHOD`
    - Value: discord
2. Create a new variable:
   - Key: `WEBHOOK_URL`
   - Value: Your Discord webhook URL

### 7. Create Birthday Database Table
Connect to the MySQL container and create the birthdays table:

```sql
CREATE TABLE birthdays (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO birthdays (name, birth_date) VALUES 
('User 1', '1990-01-15'),
('User 2', '1985-12-25');
```

## Services Configuration
The [`docker-compose.yaml`](docker-compose.yaml) file defines the following services:

- **postgres**: Airflow metadata database
- **my-sql**: Birthday data storage (port 3307)
- **redis**: Celery message broker
- **airflow-webserver**: Web UI (port 8080)
- **airflow-scheduler**: Task scheduler
- **airflow-worker**: Task executor
- **airflow-triggerer**: Sensor and trigger handler
- **airflow-init**: Initialization service

## DAG Overview
The [`birthday-reminder.py`](dags/birthday-reminder.py) DAG contains two main tasks:

1. **check_birthdays_task**: Queries MySQL database for today's birthdays
2. **send_reminder_task**: Sends Discord notifications with birthday information

**Schedule**: Daily execution (`@daily`)

## Key Features
- **Automated Daily Checks**: Runs every day to check for birthdays
- **Age Calculation**: Automatically calculates and displays ages
- **Rich Discord Notifications**: Formatted embeds with birthday information

## License
This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

---

**Note**: This configuration is designed for local development. For production deployment, additional security configurations and resource optimizations are recommended.