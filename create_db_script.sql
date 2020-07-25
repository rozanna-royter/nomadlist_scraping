CREATE DATABASE IF NOT EXISTS nomadlist1;
USE nomadlist1;

CREATE TABLE `users` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `external_id` varchar(255),
  `username` varchar(255),
  `follower_count` int,
  `following_count` int,
  `trips_count` int,
  `distance_traveled` int,
  `countries_count` int,
  `cities_count` int,
  `twitter` varchar(100),
  `instagram` varchar(100),
  `bio` varchar(511)
);

CREATE TABLE `trips` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `external_id` varchar(255),
  `user_id` int,
  `trip_start` varchar(50),
  `trip_length` varchar(50),
  `trip_end` varchar(50),
  `city_country` int
);

CREATE TABLE `city_country` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `city_name` varchar(100),
  `country_id` int
);

CREATE TABLE `countries` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `country_name` varchar(100)
);

ALTER TABLE `trips` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `trips` ADD FOREIGN KEY (`city_country`) REFERENCES `city_country` (`id`);

ALTER TABLE `city_country` ADD FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`);

ALTER TABLE `countries` ADD CONSTRAINT `country_name` UNIQUE (`country_name`);
