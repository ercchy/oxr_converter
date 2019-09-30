#!/usr/bin/env bash

RED='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color


# Grant and flush privileges
echo "Granting privileges"
echo "GRANT ALL PRIVILEGES ON *.* TO '$MYSQL_USER'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';" | /usr/bin/mysql -S /var/run/mysqld/mysqld.sock -u root -p$MYSQL_ROOT_PASSWORD
echo "FLUSH PRIVILEGES;"| /usr/bin/mysql -S /var/run/mysqld/mysqld.sock -u root -p$MYSQL_ROOT_PASSWORD

echo "Restarting Mysql service"
service mysql start

# Create database
echo "Creating converter database..."
echo "CREATE DATABASE converter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | /usr/bin/mysql -S /var/run/mysqld/mysqld.sock -u $MYSQL_USER -p$MYSQL_PASSWORD

echo
echo -e "${RED}Finished preparing your database.${NC}"
echo
echo -e "${YELLOW}Have a lovely day.${NC}"
echo