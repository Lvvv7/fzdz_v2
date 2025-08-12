-- MySQL dump 10.13  Distrib 5.7.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: fzdz_system
-- ------------------------------------------------------
-- Server version	5.7.44-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `err_cfg`
--

DROP TABLE IF EXISTS `err_cfg`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `err_cfg` (
  `err_type` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '异常类型码',
  `err_desc` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '异常描述',
  `suggestion` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '处理建议',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`err_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='异常类型配置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `print_log`
--

DROP TABLE IF EXISTS `print_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `print_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cert_no` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '证件号',
  `print_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '打印时间',
  `operator` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '经办人工号/姓名',
  `sys_version` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '系统版本号',
  `status` enum('SUCCESS','FAIL') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'SUCCESS' COMMENT '打印结果',
  `err_type` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '异常类型码（FAIL时必填）',
  `err_msg` text COLLATE utf8mb4_unicode_ci COMMENT '系统原始异常信息',
  PRIMARY KEY (`id`),
  KEY `idx_cert_no` (`cert_no`),
  KEY `idx_print_time` (`print_time`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打证任务流水';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'fzdz_system'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-12  9:22:42
