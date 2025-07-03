-- MySQL dump 10.13  Distrib 8.4.5, for Win64 (x86_64)
--
-- Host: localhost    Database: bjs-pa
-- ------------------------------------------------------
-- Server version	8.4.5

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
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `userName` int NOT NULL,
  `userCName` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `userType` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `StationCN` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `userPassword` tinytext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `nci_username` (`userName`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,1,'刘斌','admin','北京站','U2FsdGVkX1/qIYrlr/JHZ0pjRaEgSmnH0Iam32uT3SM='),(2,2,'于涛','admin','北京站','U2FsdGVkX1+dssFo4EYsvRuiyZYnAGUQEpyXcUee/3Q='),(3,3,'蔚江军','admin','北京站','U2FsdGVkX19CUid39R7p6wMLMhRLqtj4MDbzeYF1FFg='),(4,4,'罗泽朝','user','北京站','U2FsdGVkX1/qYuqLBW++JLMuwVh+SRrKeCsbudL6waM='),(5,5,'黄彪','user','北京站','U2FsdGVkX185G5av5BUqy6kfL9Y9uvrfqGSepTmOGPk='),(6,6,'王磊','user','北京站','U2FsdGVkX1/JzQNqtEqNuWGgTt1bwz7UBbZYqwI47f4='),(7,7,'连春生','user','北京站','U2FsdGVkX1/9x8EnJz1LinbJc9CHdMV52IP4qs+/yKI='),(8,8,'穆天赛','user','北京站','U2FsdGVkX1+Bxxyzsb6Eug8p687ZNQIlVYzDHY/GCZs='),(9,9,'穆玲','user','北京站','U2FsdGVkX18nLb8dwnRYzwFufhOinfkJebHZd1nGS5c='),(10,10,'刘泽坤','user','北京站','U2FsdGVkX1+CfoZTOasxy7yaKzxJ20BYXYYEsu61/cU='),(11,11,'杜操','user','北京站','U2FsdGVkX18TAi1sE45a83ebirfsLr4jmSmCqTV/VX4=');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-03 10:46:08
