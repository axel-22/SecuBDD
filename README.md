# SecuBDD
TP Sécurisation des bases de données



mon ip : 172.20.10.2 : 3306


CREATE USER 'axel'@'172.20.10.3' IDENTIFIED BY 'axel';
GRANT ALL PRIVILEGES ON *.* TO 'axel'@'172.20.10.3';
FLUSH PRIVILEGES;


CREATE DATABASE TP_SecuBDD_Jemai_HoussinVonthron;

SHOW DATABASES;

