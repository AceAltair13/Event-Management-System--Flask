-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 17, 2025 at 07:16 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `project`
--

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

CREATE TABLE `books` (
  `uid` int(11) DEFAULT NULL,
  `eid` int(11) DEFAULT NULL,
  `person1` varchar(255) DEFAULT NULL,
  `person2` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `books`
--

INSERT INTO `books` (`uid`, `eid`, `person1`, `person2`) VALUES
(1, 1, 'Epsilon Gamma', NULL),
(5, 3, 'sourabh', NULL),
(5, 4, NULL, NULL),
(5, 5, NULL, NULL),
(5, 6, 'yash', NULL),
(5, 7, 'aakash', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `contact`
--

CREATE TABLE `contact` (
  `pid` int(11) DEFAULT NULL,
  `contact1` decimal(10,0) DEFAULT NULL,
  `contact2` decimal(10,0) DEFAULT NULL,
  `contact3` decimal(10,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `contact`
--

INSERT INTO `contact` (`pid`, `contact1`, `contact2`, `contact3`) VALUES
(1, 9924161231, 1231231221, 12312434),
(2, 7385550597, 0, 0),
(3, 7385550597, 0, 0),
(4, 7385550597, 8329870397, 0);

-- --------------------------------------------------------

--
-- Table structure for table `event`
--

CREATE TABLE `event` (
  `eid` int(11) NOT NULL,
  `etype` varchar(255) NOT NULL,
  `edate` date NOT NULL,
  `etier` int(11) NOT NULL,
  `ecost` int(11) NOT NULL,
  `evenue` varchar(255) NOT NULL,
  `emax_people` int(11) NOT NULL,
  `especial` varchar(255) NOT NULL,
  `status` varchar(50) DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `event`
--

INSERT INTO `event` (`eid`, `etype`, `edate`, `etier`, `ecost`, `evenue`, `emax_people`, `especial`, `status`) VALUES
(1, 'Birthday', '2020-06-27', 3, 35000, 'Sunrays Hall, Santacruz (W), Mumbai', 34, 'Theme of decoration should be blue.', 'completed'),
(2, 'Birthday', '2025-03-19', 3, 137500, 'pimpri', 100, 'banana', 'pending'),
(3, 'Birthday', '2025-03-19', 3, 137500, 'pimpri', 100, 'banana', 'pending'),
(4, 'manifest', '2025-03-18', 2, 241000, 'akurdi', 200, 'milk', 'pending'),
(5, 'farewell', '2025-03-27', 3, 266000, 'di mora', 180, 'no drinks', 'pending'),
(6, 'Birthday', '2025-03-16', 2, 60000, 'raga palace', 50, 'nothing', 'completed'),
(7, 'Birthday', '2025-03-18', 2, 60000, 'raga palace', 50, 'nothing', 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `has`
--

CREATE TABLE `has` (
  `uid` int(11) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `has`
--

INSERT INTO `has` (`uid`, `pid`) VALUES
(1, 1),
(5, 3),
(6, 4);

-- --------------------------------------------------------

--
-- Table structure for table `personal`
--

CREATE TABLE `personal` (
  `pid` int(11) NOT NULL,
  `fname` varchar(255) NOT NULL,
  `mname` varchar(255) NOT NULL,
  `lname` varchar(255) NOT NULL,
  `dob` date NOT NULL,
  `gender` varchar(20) NOT NULL,
  `address` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `personal`
--

INSERT INTO `personal` (`pid`, `fname`, `mname`, `lname`, `dob`, `gender`, `address`) VALUES
(1, 'Alpha', 'Beta', 'Gamma', '2020-06-01', 'Male', 'Mumbai, Maharashtra, India'),
(2, 'yash', 'k', 'yadav', '2004-03-03', 'Male', 'pimpri'),
(3, 'test1', 'test2', 'test3', '2004-11-10', 'Male', 'pimpri'),
(4, 'yash', 'tejbahadur', 'yadav', '2004-03-10', 'Male', 'Nehru nagar, near suyog hospital, old telco road, pimpri');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `uid` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `last_login` timestamp NOT NULL DEFAULT current_timestamp(),
  `role` varchar(50) NOT NULL DEFAULT 'user',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`uid`, `username`, `email`, `password`, `last_login`, `role`, `created_at`) VALUES
(1, 'ABC', 'abc@xyz.com', 'e99a18c428cb38d5f260853678922e03', '2020-06-05 18:12:45', 'user', '2025-03-17 10:28:53'),
(2, 'XYZ', 'xyz@abc.com', '613d3b9c91e9445abaeca02f2342e5a6', '2020-06-05 13:53:52', 'user', '2025-03-17 10:28:53'),
(4, 'kuldeep', 'kuldeep@gmail.com', '8e4436dc3ba832ddd00caf213d2913de', '2025-03-17 04:27:42', 'admin', '2025-03-17 10:28:53'),
(5, 'test1', 'test1@gmail.com', '51ce84a6db96daaa7081869fd38c517a', '2025-03-17 05:36:09', 'user', '2025-03-17 10:28:53'),
(6, 'yashyadav', 'yash@gmail.com', '1e8d95050c46fe153d31c33bf93f61df', '2025-03-17 06:03:21', 'user', '2025-03-17 11:32:51');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD KEY `books_ibfk_1` (`uid`),
  ADD KEY `books_ibfk_2` (`eid`);

--
-- Indexes for table `contact`
--
ALTER TABLE `contact`
  ADD KEY `contact_ibfk_1` (`pid`);

--
-- Indexes for table `event`
--
ALTER TABLE `event`
  ADD PRIMARY KEY (`eid`);

--
-- Indexes for table `has`
--
ALTER TABLE `has`
  ADD KEY `has_ibfk_1` (`uid`),
  ADD KEY `has_ibfk_2` (`pid`);

--
-- Indexes for table `personal`
--
ALTER TABLE `personal`
  ADD PRIMARY KEY (`pid`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`uid`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `event`
--
ALTER TABLE `event`
  MODIFY `eid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `personal`
--
ALTER TABLE `personal`
  MODIFY `pid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `uid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `books`
--
ALTER TABLE `books`
  ADD CONSTRAINT `books_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `books_ibfk_2` FOREIGN KEY (`eid`) REFERENCES `event` (`eid`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `contact`
--
ALTER TABLE `contact`
  ADD CONSTRAINT `contact_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `personal` (`pid`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `has`
--
ALTER TABLE `has`
  ADD CONSTRAINT `has_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `has_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `personal` (`pid`) ON DELETE CASCADE ON UPDATE NO ACTION;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
