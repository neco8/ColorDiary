CREATE DATABASE IF NOT EXISTS color_diary_db CHARACTER SET utf8;
CREATE USER IF NOT EXISTS color_diary@'%' IDENTIFIED BY 'color_diary_test';
GRANT ALL PRIVILEGES ON color_diary_db.* TO color_diary@'%';
GRANT CREATE ON *.* TO color_diary@'%';
GRANT ALL PRIVILEGES ON test_color_diary_db.* TO color_diary@'%';

ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'rootpassword';
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'rootpassword';
ALTER USER 'color_diary'@'%' IDENTIFIED WITH mysql_native_password BY 'color_diary_test';

FLUSH PRIVILEGES;