CREATE TABLE `daily_counts` (
	`day` text NOT NULL,
	`metric` text NOT NULL,
	`value` text NOT NULL,
	`count` integer DEFAULT 0 NOT NULL,
	PRIMARY KEY(`day`, `metric`, `value`)
);
