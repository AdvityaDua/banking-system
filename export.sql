-- MySQL dump 10.13  Distrib 8.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: virtual_banking
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `fd_records`
--

DROP TABLE IF EXISTS `fd_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fd_records` (
  `fd_id` int NOT NULL AUTO_INCREMENT,
  `date_of_opening` date NOT NULL,
  `number_of_days` int NOT NULL,
  `invested_amount` decimal(12,2) NOT NULL,
  `rate_of_interest` varchar(20) NOT NULL,
  `closing_date` date NOT NULL,
  `user_id` bigint NOT NULL,
  `amount` bigint DEFAULT NULL,
  PRIMARY KEY (`fd_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `fd_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_details` (`user_id`),
  CONSTRAINT `fd_records_chk_1` CHECK ((`number_of_days` > 0)),
  CONSTRAINT `fd_records_chk_2` CHECK ((`invested_amount` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fd_records`
--

LOCK TABLES `fd_records` WRITE;
/*!40000 ALTER TABLE `fd_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `fd_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `rating` int NOT NULL,
  `comments` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_details` (`user_id`),
  CONSTRAINT `feedback_chk_1` CHECK ((`rating` between 1 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_records`
--

DROP TABLE IF EXISTS `loan_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_records` (
  `loan_id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `loan_type` varchar(30) NOT NULL,
  `loan_amount` decimal(12,2) NOT NULL,
  `interest_rate` varchar(10) NOT NULL,
  `tenure_months` int NOT NULL,
  `issue_date` date NOT NULL, 
  `closing_date` date NOT NULL,
  `status` varchar(15) NOT NULL,
  `monthly_emi` decimal(12,2) NOT NULL,
  PRIMARY KEY (`loan_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `loan_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_details` (`user_id`),
  CONSTRAINT `loan_records_chk_1` CHECK ((`loan_amount` > 0)),
  CONSTRAINT `loan_records_chk_2` CHECK ((`tenure_months` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_records`
--

LOCK TABLES `loan_records` WRITE;
/*!40000 ALTER TABLE `loan_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `transaction_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `priority` enum('Low','Medium','High') NOT NULL,
  `status` enum('Open','In Progress','Resolved','Closed') DEFAULT 'Open',
  `date_submitted` date DEFAULT (curdate()),
  `last_updated` timestamp NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `transaction_id` (`transaction_id`),
  CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_details` (`user_id`),
  CONSTRAINT `tickets_ibfk_2` FOREIGN KEY (`transaction_id`) REFERENCES `transaction_details` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_details`
--

DROP TABLE IF EXISTS `transaction_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction_details` (
  `date` date NOT NULL,
  `time` time NOT NULL,
  `type_of_transaction` varchar(30) DEFAULT NULL,
  `amount` int NOT NULL,
  `user_id` bigint NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'Success',
  `current_balance` int NOT NULL,
  `order_id` varchar(60) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `transaction_id` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `transaction_details_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user_details` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transaction_details_chk_5` CHECK ((`type_of_transaction` in (_utf8mb4'Deposit',_utf8mb4'Withdraw',_utf8mb4'FD Deposit',_utf8mb4'FD Withdrawal',_utf8mb4'Loan Deposit'))),
  CONSTRAINT `transaction_details_chk_6` CHECK ((`type_of_transaction` in (_cp850'Deposit',_cp850'Withdraw',_cp850'FD Deposit',_cp850'FD Withdrawal',_cp850'Loan Deposit')))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_details`
--

LOCK TABLES `transaction_details` WRITE;
/*!40000 ALTER TABLE `transaction_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `transaction_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_details`
--

DROP TABLE IF EXISTS `user_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_details` (
  `user_id` bigint NOT NULL,
  `name` varchar(20) NOT NULL,
  `father_name` varchar(20) NOT NULL,
  `mother_name` varchar(20) NOT NULL,
  `aadhar_number` bigint NOT NULL,
  `address` varchar(60) NOT NULL,
  `type_of_account` varchar(10) NOT NULL,
  `dob` date DEFAULT NULL,
  `m_status` varchar(10) NOT NULL,
  `e_status` varchar(10) NOT NULL,
  `password` varchar(255) NOT NULL,
  `current_balance` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `aadhar_number` (`aadhar_number`),
  CONSTRAINT `user_details_chk_1` CHECK ((`type_of_account` in (_utf8mb4'Saving',_utf8mb4'Current'))),
  CONSTRAINT `user_details_chk_2` CHECK ((`m_status` in (_utf8mb4'Single',_utf8mb4'Married'))),
  CONSTRAINT `user_details_chk_3` CHECK ((`e_status` in (_utf8mb4'Employed',_utf8mb4'Unemployed',_utf8mb4'Student'))),
  CONSTRAINT `user_details_chk_4` CHECK ((`current_balance` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_details`
--

LOCK TABLES `user_details` WRITE;
/*!40000 ALTER TABLE `user_details` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_details` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-04 21:06:28
