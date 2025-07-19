from . import (
	board as b,
)

'''
Upgraded the number of characters in board_images from 20 to 25
media_orig and preview_orig entries from /news/
	1658260989011151.webm
	1658159465182541s.jpg
'''

mysql = f"""
create table if not exists `{b}_deleted` like `{b}`;

create table if not exists `{b}_threads` (
	`thread_num` int unsigned not null,
	`time_op` int unsigned not null,
	`time_last` int unsigned not null,
	`time_bump` int unsigned not null,
	`time_ghost` int unsigned default null,
	`time_ghost_bump` int unsigned default null,
	`time_last_modified` int unsigned not null,
	`nreplies` int unsigned not null default 0,
	`nimages` int unsigned not null default 0,
	`sticky` bool not null default 0,
	`locked` bool not null default 0,

	primary key (`thread_num`)
) ENGINE=InnoDB CHARSET=utf8mb4;

create table if not exists `{b}_images` (
	`media_id` int unsigned not null auto_increment,
	`media_hash` varchar(25) not null,
	`media` varchar(25),
	`preview_op` varchar(25),
	`preview_reply` varchar(25),
	`total` int(10) unsigned not null default 0,
	`banned` smallint unsigned not null default 0,

	primary key (`media_id`)
) ENGINE=InnoDB DEFAULT CHARSET=ascii COLLATE=ascii_bin;

create table if not exists `{b}_users` (
	`user_id` int unsigned not null auto_increment,
	`name` varchar(100) not null default '',
	`trip` varchar(25) not null default '',
	`firstseen` int(11) not null,
	`postcount` int(11) not null,

	primary key (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create table if not exists `{b}_daily` (
	`day` int(10) unsigned not null,
	`posts` int(10) unsigned not null,
	`images` int(10) unsigned not null,
	`sage` int(10) unsigned not null,
	`anons` int(10) unsigned not null,
	`trips` int(10) unsigned not null,
	`names` int(10) unsigned not null,

	primary key (`day`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

sqlite = f"""
create table if not exists `{b}_deleted` (
	doc_id integer not null primary key autoincrement,
	media_id integer not null default 0,
	poster_ip text not null default 0,
	num integer not null,
	subnum integer not null,
	thread_num integer not null default 0,
	op integer not null default 0,
	timestamp integer not null,
	timestamp_expired integer not null,
	preview_orig text,
	preview_w integer not null default 0,
	preview_h integer not null default 0,
	media_filename text,
	media_w integer not null default 0,
	media_h integer not null default 0,
	media_size integer not null default 0,
	media_hash text,
	media_orig text,
	spoiler integer not null default 0,
	deleted integer not null default 0,
	capcode text not null default 'N',
	email text,
	name text,
	trip text,
	title text,
	comment text,
	delpass text,
	sticky integer not null default 0,
	locked integer not null default 0,
	poster_hash text,
	poster_country text,
	exif text
);

create table if not exists `{b}_threads` (
	thread_num integer not null primary key,
	time_op integer not null default 0,
	time_last integer not null default 0,
	time_bump integer not null default 0,
	time_ghost integer,
	time_ghost_bump integer,
	time_last_modified integer not null default 0,
	nreplies integer not null default 0,
	nimages integer not null default 0,
	sticky integer not null default 0,
	locked integer not null default 0
);

create table if not exists `{b}_images` (
	media_id integer not null primary key autoincrement,
	media_hash text not null,
	media text,
	preview_op text,
	preview_reply text,
	total integer not null default 0,
	banned integer not null default 0
);

create table if not exists `{b}_users` (
	user_id integer not null primary key autoincrement,
	name text not null,
	trip text not null,
	firstseen integer not null,
	postcount integer not null
);

create table if not exists `{b}_daily` (
	day integer not null primary key,
	posts integer not null default 0,
	images integer not null default 0,
	sage integer not null default 0,
	anons integer not null default 0,
	trips integer not null default 0,
	names integer not null default 0
);
"""

postgresql = f'''
create table if not exists {b}_threads (
	thread_num integer not null,
	time_op integer not null,
	time_last integer not null,
	time_bump integer not null,
	time_ghost integer default null,
	time_ghost_bump integer default null,
	time_last_modified integer not null,
	nreplies integer not null default 0,
	nimages integer not null default 0,
	sticky boolean not null default false,
	locked boolean not null default false,

	primary key (thread_num)
);

create table if not exists {b}_images (
	media_id serial not null,
	media_hash character varying(25) not null,
	media character varying(25),
	preview_op character varying(25),
	preview_reply character varying(25),
	total integer not null default 0,
	banned smallint not null default 0,

	primary key (media_id),
	unique (media_hash)
);

create table if not exists {b}_users (
	user_id serial not null,
	name character varying(100) not null default '',
	trip character varying(25) not null default '',
	firstseen integer not null,
	postcount integer not null,

	primary key (user_id),
	unique (name, trip)
);

create table if not exists {b}_daily (
	day integer not null,
	posts integer not null,
	images integer not null,
	sage integer not null,
	anons integer not null,
	trips integer not null,
	names integer not null,

	primary key (day)
);

create table if not exists {b}_deleted (
	like {b} including all
);
'''
