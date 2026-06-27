-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: premier_savings_chama
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bank_interests`
--

DROP TABLE IF EXISTS `bank_interests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bank_interests` (
  `interestId` int NOT NULL AUTO_INCREMENT,
  `amount` decimal(15,2) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `period_start` date DEFAULT NULL,
  `period_end` date DEFAULT NULL,
  PRIMARY KEY (`interestId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank_interests`
--

LOCK TABLES `bank_interests` WRITE;
/*!40000 ALTER TABLE `bank_interests` DISABLE KEYS */;
/*!40000 ALTER TABLE `bank_interests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interest_distribution`
--

DROP TABLE IF EXISTS `interest_distribution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interest_distribution` (
  `distributionId` int NOT NULL AUTO_INCREMENT,
  `interestId` int DEFAULT NULL,
  `memberId` int DEFAULT NULL,
  `share_amount` decimal(15,2) DEFAULT NULL,
  `source` enum('loanInterest','bankInterest') DEFAULT NULL,
  `dateDistributed` date DEFAULT NULL,
  PRIMARY KEY (`distributionId`),
  KEY `interestId` (`interestId`),
  KEY `memberId` (`memberId`),
  CONSTRAINT `interest_distribution_ibfk_1` FOREIGN KEY (`interestId`) REFERENCES `bank_interests` (`interestId`),
  CONSTRAINT `interest_distribution_ibfk_2` FOREIGN KEY (`memberId`) REFERENCES `members` (`memberId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interest_distribution`
--

LOCK TABLES `interest_distribution` WRITE;
/*!40000 ALTER TABLE `interest_distribution` DISABLE KEYS */;
/*!40000 ALTER TABLE `interest_distribution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loan_repayments`
--

DROP TABLE IF EXISTS `loan_repayments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loan_repayments` (
  `repaymentId` int NOT NULL AUTO_INCREMENT,
  `loanId` int DEFAULT NULL,
  `amount_paid` decimal(15,2) DEFAULT NULL,
  `interest_paid` decimal(15,2) DEFAULT NULL,
  `paid_by` int DEFAULT NULL,
  `date_paid` date DEFAULT NULL,
  PRIMARY KEY (`repaymentId`),
  KEY `loanId` (`loanId`),
  KEY `paid_by` (`paid_by`),
  CONSTRAINT `loan_repayments_ibfk_1` FOREIGN KEY (`loanId`) REFERENCES `loans` (`loanId`),
  CONSTRAINT `loan_repayments_ibfk_2` FOREIGN KEY (`paid_by`) REFERENCES `members` (`memberId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loan_repayments`
--

LOCK TABLES `loan_repayments` WRITE;
/*!40000 ALTER TABLE `loan_repayments` DISABLE KEYS */;
/*!40000 ALTER TABLE `loan_repayments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loans`
--

DROP TABLE IF EXISTS `loans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loans` (
  `loanId` int NOT NULL AUTO_INCREMENT,
  `borrowerId` int DEFAULT NULL,
  `guarantorId` int DEFAULT NULL,
  `amount` decimal(15,2) DEFAULT NULL,
  `date_borrowed` date DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `status` enum('active','paid','defaulted') DEFAULT NULL,
  `amount_paid` decimal(15,2) DEFAULT NULL,
  `paid_date` date DEFAULT NULL,
  `guarantor_paid` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`loanId`),
  KEY `borrowerId` (`borrowerId`),
  KEY `guarantorId` (`guarantorId`),
  CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`borrowerId`) REFERENCES `members` (`memberId`),
  CONSTRAINT `loans_ibfk_2` FOREIGN KEY (`guarantorId`) REFERENCES `members` (`memberId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loans`
--

LOCK TABLES `loans` WRITE;
/*!40000 ALTER TABLE `loans` DISABLE KEYS */;
/*!40000 ALTER TABLE `loans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `memberId` int NOT NULL AUTO_INCREMENT,
  `firstName` varchar(20) DEFAULT NULL,
  `lastName` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(55) DEFAULT NULL,
  `roles` enum('Admin','Member') DEFAULT NULL,
  `date_joined` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`memberId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `savings`
--

DROP TABLE IF EXISTS `savings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `savings` (
  `savingsId` int NOT NULL AUTO_INCREMENT,
  `memberId` int DEFAULT NULL,
  `amount` decimal(15,2) DEFAULT NULL,
  `date_saved` date DEFAULT NULL,
  PRIMARY KEY (`savingsId`),
  KEY `memberId` (`memberId`),
  CONSTRAINT `savings_ibfk_1` FOREIGN KEY (`memberId`) REFERENCES `members` (`memberId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `savings`
--

LOCK TABLES `savings` WRITE;
/*!40000 ALTER TABLE `savings` DISABLE KEYS */;
/*!40000 ALTER TABLE `savings` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-18 11:29:15
