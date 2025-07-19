from . import board as b

mysql = f"""
drop procedure if exists `update_thread_{b}`;
drop procedure if exists `create_thread_{b}`;
drop procedure if exists `delete_thread_{b}`;
drop procedure if exists `insert_image_{b}`;
drop procedure if exists `delete_image_{b}`;
drop procedure if exists `insert_post_{b}`;
drop procedure if exists `delete_post_{b}`;

drop trigger if exists `before_ins_{b}`;
drop trigger if exists `after_ins_{b}`;
drop trigger if exists `after_del_{b}`;

create procedure if not exists `update_thread_{b}` (ins INT, tnum INT, subnum INT, timestamp INT, media INT, email VARCHAR(100))
BEGIN
	UPDATE
		`{b}_threads` op
	SET
		op.time_last = IF((ins AND subnum = 0), GREATEST(timestamp, op.time_last), op.time_last),
		op.time_bump = IF((ins AND subnum = 0), GREATEST(timestamp, op.time_bump), op.time_bump),
		op.time_ghost = IF((ins AND subnum != 0), GREATEST(timestamp, COALESCE(op.time_ghost, 0)), op.time_ghost),
		op.time_ghost_bump = IF((ins AND subnum != 0 AND (email IS NULL OR email != 'sage')), GREATEST(timestamp, COALESCE(op.time_ghost_bump, 0)), op.time_ghost_bump),
		op.time_last_modified = GREATEST(timestamp, op.time_last_modified),
		op.nreplies = IF(ins, (op.nreplies + 1), (op.nreplies - 1)),
		op.nimages = IF(media, IF(ins, (op.nimages + 1), (op.nimages - 1)), op.nimages)
	WHERE op.thread_num = tnum;
END;

create procedure if not exists `create_thread_{b}` (num INT, timestamp INT)
BEGIN
	INSERT IGNORE INTO `{b}_threads` VALUES
		(num, timestamp, timestamp, timestamp, NULL, NULL, timestamp, 0, 0, 0, 0);
END;

create procedure if not exists `delete_thread_{b}` (tnum INT)
BEGIN
	delete from `{b}_threads` WHERE thread_num = tnum;
END;

create procedure if not exists `insert_image_{b}` (n_media_hash VARCHAR(25), n_media VARCHAR(50), n_preview VARCHAR(50), n_op INT)
BEGIN
	IF n_op = 1 THEN
		INSERT INTO `{b}_images` (media_hash, media, preview_op, total)
		VALUES (n_media_hash, n_media, n_preview, 1)
		ON DUPLICATE KEY UPDATE
			media_id = LAST_INSERT_ID(media_id),
			total = (total + 1),
			preview_op = COALESCE(preview_op, VALUES(preview_op)),
			media = COALESCE(media, VALUES(media));
	ELSE
		INSERT INTO `{b}_images` (media_hash, media, preview_reply, total)
		VALUES (n_media_hash, n_media, n_preview, 1)
		ON DUPLICATE KEY UPDATE
			media_id = LAST_INSERT_ID(media_id),
			total = (total + 1),
			preview_reply = COALESCE(preview_reply, VALUES(preview_reply)),
			media = COALESCE(media, VALUES(media));
	END IF;
END;

create procedure if not exists `delete_image_{b}` (n_media_id INT)
BEGIN
	UPDATE `{b}_images` SET total = (total - 1) WHERE media_id = n_media_id;
END;

create trigger `before_ins_{b}` before insert on `{b}`
FOR EACH ROW
BEGIN
	IF NEW.media_hash IS NOT NULL THEN
		CALL insert_image_{b}(NEW.media_hash, NEW.media_orig, NEW.preview_orig, NEW.op);
		SET NEW.media_id = LAST_INSERT_ID();
	END IF;
END;

create trigger `after_ins_{b}` after insert on `{b}`
FOR EACH ROW
BEGIN
	IF NEW.op = 1 THEN
		CALL create_thread_{b}(NEW.num, NEW.timestamp);
	END IF;
	CALL update_thread_{b}(1, NEW.thread_num, NEW.subnum, NEW.timestamp, NEW.media_id, NEW.email);
END;

create trigger `after_del_{b}` after delete on `{b}`
FOR EACH ROW
BEGIN
	CALL update_thread_{b}(0, OLD.thread_num, OLD.subnum, OLD.timestamp, OLD.media_id, OLD.email);
	IF OLD.op = 1 THEN
		CALL delete_thread_{b}(OLD.num);
	END IF;
	IF OLD.media_hash IS NOT NULL THEN
		CALL delete_image_{b}(OLD.media_id);
	END IF;
END;
"""

sqlite = f"""
CREATE TRIGGER IF NOT EXISTS `{b}_before_ins_media_op`
BEFORE INSERT ON `{b}` FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.op = 1
BEGIN
	INSERT INTO `{b}_images` (media_hash, media, preview_op, total)
	VALUES (NEW.media_hash, NEW.media_orig, NEW.preview_orig, 1)
	ON CONFLICT (media_hash) DO UPDATE SET
		total = (total + 1),
		preview_op = COALESCE(preview_op, EXCLUDED.preview_op),
		media = COALESCE(media, EXCLUDED.media);
END;

CREATE TRIGGER IF NOT EXISTS `{b}_before_ins_media_reply`
BEFORE INSERT ON `{b}` FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.op = 0
BEGIN
	INSERT INTO `{b}_images` (media_hash, media, preview_reply, total)
	VALUES (NEW.media_hash, NEW.media_orig, NEW.preview_orig, 1)
	ON CONFLICT (media_hash) DO UPDATE SET
		total = (total + 1),
		preview_reply = COALESCE(preview_reply, EXCLUDED.preview_reply),
		media = COALESCE(media, EXCLUDED.media);
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_ins_media`
AFTER INSERT ON `{b}` FOR EACH ROW
WHEN NEW.media_hash IS NOT NULL and NEW.media_id = 0
BEGIN
	UPDATE `{b}` SET media_id = (
		SELECT media_id FROM `{b}_images` WHERE media_hash = NEW.media_hash
	) WHERE doc_id = NEW.doc_id;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_ins_op`
AFTER INSERT ON `{b}` FOR EACH ROW
WHEN NEW.op = 1
BEGIN
	INSERT OR IGNORE INTO `{b}_threads` (thread_num, time_op, time_last, time_bump, time_last_modified, nimages)
	VALUES (
		NEW.num, NEW.timestamp, NEW.timestamp, NEW.timestamp, NEW.timestamp,
		(NEW.media_hash IS NOT NULL)
	);
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_ins_reply`
AFTER INSERT ON `{b}` FOR EACH ROW
WHEN NEW.op = 0 AND NEW.subnum = 0
BEGIN
	UPDATE
		`{b}_threads`
	SET
		time_last = MAX(NEW.timestamp, time_last),
		time_bump = CASE WHEN (NEW.email = 'sage') THEN time_bump ELSE MAX(NEW.timestamp, COALESCE(time_bump, 0)) END,
		time_last_modified = MAX(NEW.timestamp, time_last_modified),
		nreplies = (nreplies + 1),
		nimages = nimages + (NEW.media_id IS NOT NULL)
	WHERE thread_num = NEW.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_ins_reply_ghost`
AFTER INSERT ON `{b}` FOR EACH ROW
WHEN NEW.op = 0 AND NEW.subnum != 0
BEGIN
	UPDATE
		`{b}_threads`
	SET
		time_ghost = MAX(NEW.timestamp, COALESCE(time_ghost, 0)),
		time_ghost_bump = CASE WHEN (NEW.email = 'sage') THEN time_ghost_bump ELSE MAX(NEW.timestamp, COALESCE(time_ghost_bump, 0)) END,
		time_last_modified = MAX(NEW.timestamp, time_last_modified),
		nreplies = (nreplies + 1),
		nimages = nimages + (NEW.media_id IS NOT NULL)
	WHERE thread_num = NEW.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_del_media`
AFTER DELETE ON `{b}` FOR EACH ROW
WHEN OLD.media_hash IS NOT NULL
BEGIN
	UPDATE `{b}_images` SET total = (total - 1) WHERE media_id = OLD.media_id;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_del_op`
AFTER DELETE ON `{b}` FOR EACH ROW
WHEN OLD.op = 1
BEGIN
	DELETE FROM `{b}_threads` WHERE thread_num = OLD.num;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_del_reply`
AFTER DELETE ON `{b}` FOR EACH ROW
WHEN OLD.op = 0 AND OLD.subnum = 0
BEGIN
	UPDATE
		`{b}_threads`
	SET
		time_last_modified = MAX(OLD.timestamp, time_last_modified),
		nreplies = (nreplies - 1),
		nimages = nimages - (OLD.media_id IS NOT NULL)
	WHERE thread_num = OLD.thread_num;
END;

CREATE TRIGGER IF NOT EXISTS `{b}_after_del_reply_ghost`
AFTER DELETE ON `{b}` FOR EACH ROW
WHEN OLD.op = 0 AND OLD.subnum != 0
BEGIN
	UPDATE
		`{b}_threads`
	SET
		time_last_modified = MAX(OLD.timestamp, time_last_modified),
		nreplies = (nreplies - 1),
		nimages = nimages - (OLD.media_id IS NOT NULL)
	WHERE thread_num = OLD.thread_num;
END;
"""

postgresql = f'''
create or replace function {b}_update_thread(n_row "{b}") RETURNS void AS $$
BEGIN
	UPDATE
		{b}_threads AS op
	SET
		time_last = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT MAX(timestamp) FROM {b} re WHERE
					re.thread_num = $1.thread_num AND re.subnum = 0)
			), op.time_op)
		),
		time_bump = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT MAX(timestamp) FROM {b} re WHERE
					re.thread_num = $1.thread_num AND (re.email <> 'sage' OR re.email IS NULL)
					AND re.subnum = 0)
			), op.time_op)
		),
		time_ghost = (
			SELECT MAX(timestamp) FROM {b} re WHERE
				re.thread_num = $1.thread_num AND re.subnum <> 0
		),
		time_ghost_bump = (
			SELECT MAX(timestamp) FROM {b} re WHERE
				re.thread_num = $1.thread_num AND re.subnum <> 0 AND (re.email <> 'sage' OR
					re.email IS NULL)
		),
		time_last_modified = (
			COALESCE(GREATEST(
				op.time_op,
				(SELECT GREATEST(MAX(timestamp), MAX(timestamp_expired)) FROM {b} re WHERE
					re.thread_num = $1.thread_num)
			), op.time_op)
		),
		nreplies = (
			SELECT COUNT(*) FROM {b} re WHERE
				re.thread_num = $1.thread_num
		),
		nimages = (
			SELECT COUNT(media_hash) FROM {b} re WHERE
				re.thread_num = $1.thread_num
		)
		WHERE op.thread_num = $1.thread_num;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_create_thread(n_row "{b}") RETURNS void AS $$
BEGIN
	IF n_row.op = false THEN RETURN; END IF;
	INSERT INTO {b}_threads SELECT $1.num, $1.timestamp, $1.timestamp,
			$1.timestamp, NULL, NULL, $1.timestamp, 0, 0, false, false WHERE NOT EXISTS (SELECT 1 FROM {b}_threads WHERE thread_num=$1.num);
	RETURN;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_delete_thread(n_parent integer) RETURNS void AS $$
BEGIN
	delete from {b}_threads WHERE thread_num = n_parent;
	RETURN;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_insert_image(n_row "{b}") RETURNS integer AS $$
DECLARE
		img_id INTEGER;
BEGIN
	INSERT INTO {b}_images
		(media_hash, media, preview_op, preview_reply, total)
		SELECT n_row.media_hash, n_row.media_orig, NULL, NULL, 0
		WHERE NOT EXISTS (SELECT 1 FROM {b}_images WHERE media_hash = n_row.media_hash);

	IF n_row.op = true THEN
		UPDATE {b}_images SET total = (total + 1), preview_op = COALESCE(preview_op, n_row.preview_orig) WHERE media_hash = n_row.media_hash RETURNING media_id INTO img_id;
	ELSE
		UPDATE {b}_images SET total = (total + 1), preview_reply = COALESCE(preview_reply, n_row.preview_orig) WHERE media_hash = n_row.media_hash RETURNING media_id INTO img_id;
	END IF;
	RETURN img_id;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_delete_image(n_media_id integer) RETURNS void AS $$
BEGIN
	UPDATE {b}_images SET total = (total - 1) WHERE id = n_media_id;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_insert_post(n_row "{b}") RETURNS void AS $$
DECLARE
	d_day integer;
	d_image integer;
	d_sage integer;
	d_anon integer;
	d_trip integer;
	d_name integer;
BEGIN
	d_day := FLOOR($1.timestamp/86400)*86400;
	d_image := CASE WHEN $1.media_hash IS NOT NULL THEN 1 ELSE 0 END;
	d_sage := CASE WHEN $1.email = 'sage' THEN 1 ELSE 0 END;
	d_anon := CASE WHEN $1.name = 'Anonymous' AND $1.trip IS NULL THEN 1 ELSE 0 END;
	d_trip := CASE WHEN $1.trip IS NOT NULL THEN 1 ELSE 0 END;
	d_name := CASE WHEN COALESCE($1.name <> 'Anonymous' AND $1.trip IS NULL, TRUE) THEN 1 ELSE 0 END;

	INSERT INTO {b}_daily
		SELECT d_day, 0, 0, 0, 0, 0, 0
		WHERE NOT EXISTS (SELECT 1 FROM {b}_daily WHERE day = d_day);

	UPDATE {b}_daily SET posts=posts+1, images=images+d_image,
		sage=sage+d_sage, anons=anons+d_anon, trips=trips+d_trip,
		names=names+d_name WHERE day = d_day;

	IF (SELECT trip FROM {b}_users WHERE trip = $1.trip) IS NOT NULL THEN
		UPDATE {b}_users SET postcount=postcount+1,
			firstseen = LEAST($1.timestamp, firstseen),
			name = COALESCE($1.name, '')
			WHERE trip = $1.trip;
	ELSE
		INSERT INTO {b}_users (name, trip, firstseen, postcount)
			SELECT COALESCE($1.name,''), COALESCE($1.trip,''), $1.timestamp, 0
			WHERE NOT EXISTS (SELECT 1 FROM {b}_users WHERE name = COALESCE($1.name,'') AND trip = COALESCE($1.trip,''));

		UPDATE {b}_users SET postcount=postcount+1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE name = COALESCE($1.name,'') AND trip = COALESCE($1.trip,'');
	END IF;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_delete_post(n_row "{b}") RETURNS void AS $$
DECLARE
	d_day integer;
	d_image integer;
	d_sage integer;
	d_anon integer;
	d_trip integer;
	d_name integer;
BEGIN
	d_day := FLOOR($1.timestamp/86400)*86400;
	d_image := CASE WHEN $1.media_hash IS NOT NULL THEN 1 ELSE 0 END;
	d_sage := CASE WHEN $1.email = 'sage' THEN 1 ELSE 0 END;
	d_anon := CASE WHEN $1.name = 'Anonymous' AND $1.trip IS NULL THEN 1 ELSE 0 END;
	d_trip := CASE WHEN $1.trip IS NOT NULL THEN 1 ELSE 0 END;
	d_name := CASE WHEN COALESCE($1.name <> 'Anonymous' AND $1.trip IS NULL, TRUE) THEN 1 ELSE 0 END;

	UPDATE {b}_daily SET posts=posts-1, images=images-d_image,
		sage=sage-d_sage, anons=anons-d_anon, trips=trips-d_trip,
		names=names-d_name WHERE day = d_day;

	IF (SELECT trip FROM {b}_users WHERE trip = $1.trip) IS NOT NULL THEN
		UPDATE {b}_users SET postcount=postcount-1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE trip = $1.trip;
	ELSE
		UPDATE {b}_users SET postcount=postcount-1,
			firstseen = LEAST($1.timestamp, firstseen)
			WHERE (name = $1.name OR $1.name IS NULL) AND (trip = $1.trip OR $1.trip IS NULL);
	END IF;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_before_insert() RETURNS trigger AS $$
BEGIN
	IF NEW.media_hash IS NOT NULL THEN
		SELECT {b}_insert_image(NEW) INTO NEW.media_id;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

create or replace function {b}_after_insert() RETURNS trigger AS $$
BEGIN
	IF NEW.op = true THEN
		PERFORM {b}_create_thread(NEW);
	END IF;
	PERFORM {b}_update_thread(NEW);
	PERFORM {b}_insert_post(NEW);
	RETURN NULL;
END;
$$ LANGUAGE plpgsql;

create or replace function {b}_after_del() RETURNS trigger AS $$
BEGIN
	PERFORM {b}_update_thread(OLD);
	IF OLD.op = true THEN
		PERFORM {b}_delete_thread(OLD.num);
	END IF;
	PERFORM {b}_delete_post(OLD);
	IF OLD.media_hash IS NOT NULL THEN
		PERFORM {b}_delete_image(OLD.media_id);
	END IF;
	RETURN NULL;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER {b}_after_delete AFTER DELETE ON {b}
	FOR EACH ROW EXECUTE PROCEDURE {b}_after_del();

CREATE TRIGGER {b}_before_insert BEFORE INSERT ON {b}
	FOR EACH ROW EXECUTE PROCEDURE {b}_before_insert();

CREATE TRIGGER {b}_after_insert AFTER INSERT ON {b}
	FOR EACH ROW EXECUTE PROCEDURE {b}_after_insert();
'''
