CREATE TABLE `Item` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar NOT NULL,
	`type` INT NOT NULL,
	`lendingDuration` TIME,
	`deleted` BOOLEAN NOT NULL DEFAULT 'false',
	`visibleFor` varchar NOT NULL DEFAULT 'all',
	PRIMARY KEY (`id`)
);

CREATE TABLE `ItemType` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar NOT NULL AUTO_INCREMENT UNIQUE,
	`namescheme` varchar NOT NULL,
	`lendable` BOOLEAN NOT NULL DEFAULT 'true',
	`lendingDuration` TIME,
	`deleted` BOOLEAN NOT NULL DEFAULT 'false',
	`visibleFor` varchar NOT NULL DEFAULT 'all',
	`howTo` TEXT,
	PRIMARY KEY (`id`)
);

CREATE TABLE `AttributeDefinition` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar NOT NULL,
	`type` varchar NOT NULL,
	`jsonscheme` TEXT DEFAULT 'NULL',
	`visibleFor` varchar NOT NULL DEFAULT 'all',
	PRIMARY KEY (`id`)
);

CREATE TABLE `Attribute` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`value` varchar,
	`valueText` TEXT DEFAULT 'NULL',
	PRIMARY KEY (`id`)
);

CREATE TABLE `ItemToAttribute` (
	`item` INT NOT NULL,
	`metadata` INT NOT NULL,
	PRIMARY KEY (`item`,`metadata`)
);

CREATE TABLE `Tag` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar NOT NULL UNIQUE,
	`lendingDuration` TIME,
	`deleted` BOOLEAN NOT NULL DEFAULT 'false',
	`visibleFor` varchar NOT NULL DEFAULT 'all',
	PRIMARY KEY (`id`)
);

CREATE TABLE `TypeCanContainTypes` (
	`type` INT NOT NULL,
	`contains` INT NOT NULL,
	PRIMARY KEY (`type`,`contains`)
);

CREATE TABLE `ItemToTag` (
	`item` INT NOT NULL,
	`tag` INT NOT NULL,
	PRIMARY KEY (`item`,`tag`)
);

CREATE TABLE `ItemTypeToAttributeDefinition` (
	`itemType` INT NOT NULL,
	`attributeDefinition` INT NOT NULL,
	PRIMARY KEY (`itemType`,`attributeDefinition`)
);

CREATE TABLE `TagToAttributeDefinition` (
	`tag` INT NOT NULL,
	`attributeDefinition` INT NOT NULL,
	`ausleihdauer` TIME,
	PRIMARY KEY (`tag`,`attributeDefinition`)
);

CREATE TABLE `ItemToAttributeTag` (
	`item` INT NOT NULL,
	`tag` INT NOT NULL,
	`metadata` INT NOT NULL,
	PRIMARY KEY (`item`,`tag`,`metadata`)
);

CREATE TABLE `ItemToItem` (
	`parent` INT NOT NULL,
	`item` INT NOT NULL,
	PRIMARY KEY (`parent`,`item`)
);

CREATE TABLE `Lending` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`moderator` INT NOT NULL,
	`user` varchar NOT NULL,
	`date` DATETIME NOT NULL DEFAULT 'NOW()',
	`deposit` varchar NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `ItemToLending` (
	`item` INT NOT NULL,
	`lending` INT NOT NULL,
	`due` DATETIME NOT NULL,
	PRIMARY KEY (`item`,`lending`)
);

CREATE TABLE `File` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`item` INT NOT NULL,
	`name` varchar NOT NULL,
	`path` varchar NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `Blacklist` (
	`id` INT NOT NULL AUTO_INCREMENT,
	`name` varchar NOT NULL,
	`allTypes` BOOLEAN DEFAULT 'true',
	`reason` TEXT,
	PRIMARY KEY (`id`)
);

CREATE TABLE `BlacklistToItemType` (
	`user` INT NOT NULL,
	`itemType` INT NOT NULL,
	PRIMARY KEY (`user`,`itemType`)
);

ALTER TABLE `Item` ADD CONSTRAINT `Item_fk0` FOREIGN KEY (`type`) REFERENCES `ItemType`(`id`);

ALTER TABLE `ItemToAttribute` ADD CONSTRAINT `ItemToAttribute_fk0` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToAttribute` ADD CONSTRAINT `ItemToAttribute_fk1` FOREIGN KEY (`metadata`) REFERENCES `Attribute`(`id`);

ALTER TABLE `TypeCanContainTypes` ADD CONSTRAINT `TypeCanContainTypes_fk0` FOREIGN KEY (`type`) REFERENCES `ItemType`(`id`);

ALTER TABLE `TypeCanContainTypes` ADD CONSTRAINT `TypeCanContainTypes_fk1` FOREIGN KEY (`contains`) REFERENCES `ItemType`(`id`);

ALTER TABLE `ItemToTag` ADD CONSTRAINT `ItemToTag_fk0` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToTag` ADD CONSTRAINT `ItemToTag_fk1` FOREIGN KEY (`tag`) REFERENCES `Tag`(`id`);

ALTER TABLE `ItemTypeToAttributeDefinition` ADD CONSTRAINT `ItemTypeToAttributeDefinition_fk0` FOREIGN KEY (`itemType`) REFERENCES `ItemType`(`id`);

ALTER TABLE `ItemTypeToAttributeDefinition` ADD CONSTRAINT `ItemTypeToAttributeDefinition_fk1` FOREIGN KEY (`attributeDefinition`) REFERENCES `AttributeDefinition`(`id`);

ALTER TABLE `TagToAttributeDefinition` ADD CONSTRAINT `TagToAttributeDefinition_fk0` FOREIGN KEY (`tag`) REFERENCES `Tag`(`id`);

ALTER TABLE `TagToAttributeDefinition` ADD CONSTRAINT `TagToAttributeDefinition_fk1` FOREIGN KEY (`attributeDefinition`) REFERENCES `AttributeDefinition`(`id`);

ALTER TABLE `ItemToAttributeTag` ADD CONSTRAINT `ItemToAttributeTag_fk0` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToAttributeTag` ADD CONSTRAINT `ItemToAttributeTag_fk1` FOREIGN KEY (`tag`) REFERENCES `Tag`(`id`);

ALTER TABLE `ItemToAttributeTag` ADD CONSTRAINT `ItemToAttributeTag_fk2` FOREIGN KEY (`metadata`) REFERENCES `Attribute`(`id`);

ALTER TABLE `ItemToItem` ADD CONSTRAINT `ItemToItem_fk0` FOREIGN KEY (`parent`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToItem` ADD CONSTRAINT `ItemToItem_fk1` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToLending` ADD CONSTRAINT `ItemToLending_fk0` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `ItemToLending` ADD CONSTRAINT `ItemToLending_fk1` FOREIGN KEY (`lending`) REFERENCES `Lending`(`id`);

ALTER TABLE `File` ADD CONSTRAINT `File_fk0` FOREIGN KEY (`item`) REFERENCES `Item`(`id`);

ALTER TABLE `BlacklistToItemType` ADD CONSTRAINT `BlacklistToItemType_fk0` FOREIGN KEY (`user`) REFERENCES `Blacklist`(`id`);

ALTER TABLE `BlacklistToItemType` ADD CONSTRAINT `BlacklistToItemType_fk1` FOREIGN KEY (`itemType`) REFERENCES `ItemType`(`id`);

