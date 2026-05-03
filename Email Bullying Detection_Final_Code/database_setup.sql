/*
SQLyog Community v13.1.1 (64 bit)
MySQL - 5.5.29 : Database - bullymail_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`bullymail_db` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `bullymail_db`;

/*Table structure for table `analyzed_emails` */

DROP TABLE IF EXISTS `analyzed_emails`;

CREATE TABLE `analyzed_emails` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email_subject` text,
  `email_from` text,
  `email_text` text NOT NULL,
  `is_bullying` tinyint(1) NOT NULL,
  `confidence` float NOT NULL,
  `rule_based_matches` text,
  `rule_based_score` float DEFAULT NULL,
  `ml_prediction` tinyint(1) DEFAULT NULL,
  `ml_confidence` float DEFAULT NULL,
  `model_used` varchar(50) DEFAULT NULL,
  `email_date` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;

/*Data for the table `analyzed_emails` */

insert  into `analyzed_emails`(`id`,`email_subject`,`email_from`,`email_text`,`is_bullying`,`confidence`,`rule_based_matches`,`rule_based_score`,`ml_prediction`,`ml_confidence`,`model_used`,`email_date`,`created_at`) values 
(1,'Regarding Your Recent Submission','professor@university.edu','Your recent work is completely unacceptable and demonstrates a fundamental lack of understanding. I\'m surprised someone with your background would even attempt this level of work. You should seriously consider whether this academic path is right for you, as your performance has been consistently disappointing and frankly embarrassing for the department.',1,0.563,'',0,1,0.938,'Latest',NULL,'2025-11-13 17:01:57'),
(2,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to pujith@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser d2e1a72fcca58-7722a0e72easor12529159b3a.0 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:03:19','2025-11-13 17:03:19'),
(3,'Test Email from BullyMail System','cloudkeys1@gmail.com','This is a test email to verify that your email configuration is working correctly.  If you received this email, your BullyMail system is properly configured for email integration.',0,0.194,'',0,0,0.324,'Latest','2025-11-13 17:03:21','2025-11-13 17:03:21'),
(4,'Meeting Reminder - CS101','department@university.edu','This is a reminder about the department meeting scheduled for tomorrow at 3 PM in the main conference room. Please bring your quarterly progress reports. The agenda includes discussion of upcoming curriculum changes and research opportunities. Let me know if you have any conflicts with this timing.',0,0.064,'',0,0,0.107,'Latest',NULL,'2025-11-13 17:05:09'),
(5,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to live.100projects@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser 41be03b00d2f7-b15fa70f40bsor6387672a12.7 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:06:41','2025-11-13 17:06:41'),
(6,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to saney@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser 5b1f17b1804b1-454ccdda1c0sor16279675e9.11 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:06:43','2025-11-13 17:06:43'),
(7,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to saney@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser 5b1f17b1804b1-454b1c170e3sor45052925e9.11 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:06:45','2025-11-13 17:06:45'),
(8,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to pujith@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser d2e1a72fcca58-7722a0e72easor12529159b3a.0 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:06:47','2025-11-13 17:06:47'),
(9,'Test Email from BullyMail System','cloudkeys1@gmail.com','This is a test email to verify that your email configuration is working correctly.  If you received this email, your BullyMail system is properly configured for email integration.',0,0.194,'',0,0,0.324,'Latest','2025-11-13 17:06:49','2025-11-13 17:06:49'),
(10,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to saney@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser 5b1f17b1804b1-454b1c170e3sor45052925e9.11 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:15:26','2025-11-13 17:15:26'),
(11,'Delivery Status Notification (Failure)','Mail Delivery Subsystem <mailer-daemon@googlemail.com>','** Address not found **  Your message wasn\'t delivered to pujith@gmail.com because the address couldn\'t be found, or is unable to receive mail.  Learn more here: https://support.google.com/mail/?p=NoSuchUser  The response was:  550 5.1.1 The email account that you tried to reach does not exist. Please try double-checking the recipient\'s email address for typos or unnecessary spaces. For more information, go to https://support.google.com/mail/?p=NoSuchUser d2e1a72fcca58-7722a0e72easor12529159b3a.0 - gsmtp',0,0.147,'',0,0,0.245,'Latest','2025-11-13 17:15:28','2025-11-13 17:15:28'),
(12,'Test Email from BullyMail System','cloudkeys1@gmail.com','This is a test email to verify that your email configuration is working correctly.  If you received this email, your BullyMail system is properly configured for email integration.',0,0.194,'',0,0,0.324,'Latest','2025-11-13 17:15:30','2025-11-13 17:15:30'),
(13,'Meeting Reminder - CS101','department@university.edu','This is a reminder about the department meeting scheduled for tomorrow at 3 PM in the main conference room. Please bring your quarterly progress reports. The agenda includes discussion of upcoming curriculum changes and research opportunities. Let me know if you have any conflicts with this timing.',0,0.064,'',0,0,0.107,'Latest',NULL,'2025-11-13 17:15:37'),
(14,'Meeting Reminder - CS101','department@university.edu','asfas ;a\'f\'f;f;as\'faf asfamslfkasl;fk a faklsfdjaslfj;af98q34950q7350 q80 vhfsaudifl a',0,0.09,'',0,0,0.15,'SVM',NULL,'2025-11-13 17:17:44'),
(15,'Meeting Reminder - CS101','department@university.edu','I\'ve reviewed your research proposal and I must say this is completely unacceptable. useless student Your work demonstrates a fundamental lack of understanding that is concerning at this stage of your academic career.\n',1,0.607,'useless student',0.016,1,1,'SVM',NULL,'2025-11-13 17:18:08'),
(16,'Great Work on the Assignment','advisor@university.edu','Regarding your recent research paper, the quality is far below what we expect from students at this level. not meeting potential You need to seriously reconsider whether you\'re cut out for this program.\n',1,0.607,'not meeting potential',0.016,1,1,'SVM',NULL,'2025-11-13 17:21:06'),
(17,'Department Announcement - ECON301','','Office hours for SOC101 have been updated. The new schedule is available on the course website.\n',0,0,'',0,0,0.001,'SVM',NULL,'2025-11-13 17:53:52'),
(18,'Aravind','','i working on ml projects but not getting proper results so can you resolve it.',1,0.507,'',0,1,0.845,'SVM',NULL,'2025-11-13 18:18:02'),
(19,'Aravind','','i working on ml projects.',0,0.089,'',0,0,0.148,'SVM',NULL,'2025-11-13 18:18:44'),
(20,'Regarding Your Recent Submission','professor@university.edu','Your recent work is completely unacceptable and demonstrates a fundamental lack of understanding. I\'m surprised someone with your background would even attempt this level of work. You should seriously consider whether this academic path is right for you, as your performance has been consistently disappointing and frankly embarrassing for the department.',1,0.6,'',0,1,1,'SVM',NULL,'2025-11-13 18:19:45');

/*Table structure for table `dataset_history` */

DROP TABLE IF EXISTS `dataset_history`;

CREATE TABLE `dataset_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `total_samples` int(11) DEFAULT NULL,
  `bullying_samples` int(11) DEFAULT NULL,
  `non_bullying_samples` int(11) DEFAULT NULL,
  `file_size` varchar(50) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

/*Data for the table `dataset_history` */

/*Table structure for table `email_config` */

DROP TABLE IF EXISTS `email_config`;

CREATE TABLE `email_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email_address` varchar(255) DEFAULT NULL,
  `configured_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

/*Data for the table `email_config` */

insert  into `email_config`(`id`,`email_address`,`configured_at`,`status`) values 
(1,'cloudkeys1@gmail.com','2025-11-13 17:02:34','success');

/*Table structure for table `model_history` */

DROP TABLE IF EXISTS `model_history`;

CREATE TABLE `model_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_type` varchar(50) NOT NULL,
  `precision_score` float DEFAULT NULL,
  `recall_score` float DEFAULT NULL,
  `f1_score` float DEFAULT NULL,
  `accuracy` float DEFAULT NULL,
  `training_samples` int(11) DEFAULT NULL,
  `test_samples` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

/*Data for the table `model_history` */

insert  into `model_history`(`id`,`model_type`,`precision_score`,`recall_score`,`f1_score`,`accuracy`,`training_samples`,`test_samples`,`created_at`) values 
(1,'Logistic Regression',1,1,1,1,700,300,'2025-11-13 16:51:25'),
(2,'SVM',1,1,1,1,3500,1500,'2025-11-13 17:16:54'),
(3,'Logistic Regression',1,1,1,1,700,300,'2025-11-13 17:18:49'),
(4,'SVM',1,1,1,1,3500,1500,'2025-11-13 17:20:04');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) DEFAULT 'moderator',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;

/*Data for the table `users` */

insert  into `users`(`id`,`username`,`password`,`role`,`created_at`) values 
(1,'admin','admin123','admin','2025-11-13 16:37:40');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
