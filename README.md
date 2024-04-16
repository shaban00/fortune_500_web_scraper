# Guide

## Create database

```sql
   CREATE DATABASE fortune_500_web_scraper;
```

## Create database user

```sql
   CREATE USER 'shaban'@'%' IDENTIFIED BY 'password';
   GRANT ALL ON fortune_500_web_scraper.* to 'shaban'@'%';
   FLUSH PRIVILEGES;
   EXIT;
```

## Use database

```sql
   USE fortune_500_web_scraper;
```

## Create tables

```sql
   CREATE TABLE companies (
      id VARCHAR(36) DEFAULT UUID() PRIMARY KEY,
      rank INT,
      company LONGTEXT,
      website LONGTEXT,
      career_links LONGTEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
   );

```

## Create virtual environment

```bash
   python -m venv .venv
```

## Activate virtual environment

```bash
   source .venv/bin/activate
```

## Install project dependencies

```bash
   pip install -r requirements
```

## Copy project to server

```bash
   scp -r fortune_500_web_scraper sfbu:~/
```

## Local port forwarding to the remote database

```bash
   ssh -L 3307:50.112.145.155:3306 sfbu
```

## Connect to the MySQL server

```bash
   mysql -u professor -p -P 3307
```

- username: professor
- password: 510Fremont

mysql -u professor -p -h 50.112.145.155

mysql -u professor -p -h cs531database.labnet.sfbu.edu

tail -n 4 ~/.ssh/config
