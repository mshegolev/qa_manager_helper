-- jira.issue definition

-- Drop table

-- DROP TABLE jira.issue;

CREATE TABLE jira.issue (
	id int8 NULL,
	"key" varchar NOT NULL,
	project varchar NULL,
	epic_key varchar NULL,
	"type" varchar NULL,
	status varchar NULL,
	priority varchar NULL,
	summary varchar NULL,
	reporter varchar NULL,
	assignee varchar NULL,
	resolution varchar NULL,
	created timestamp NULL,
	updated timestamp NULL,
	original_estimate int4 NULL,
	remaining_estimate int4 NULL,
	time_spent int4 NULL,
	severity varchar NULL,
	CONSTRAINT issue_pk PRIMARY KEY (key)
);



-- jira.issue_affected_version definition

-- Drop table

-- DROP TABLE jira.issue_affected_version;

CREATE TABLE jira.issue_affected_version (
	"key" varchar NULL,
	"version" varchar NULL
);
CREATE INDEX issue_affected_version_key_index ON jira.issue_affected_version USING btree (key);




-- jira.issue_change definition

-- Drop table

-- DROP TABLE jira.issue_change;

CREATE TABLE jira.issue_change (
	"key" varchar NULL,
	author varchar NULL,
	created timestamp NULL,
	from_value varchar NULL,
	to_value varchar NULL,
	"type" varchar NULL
);
CREATE INDEX issue_change_key_index ON jira.issue_change USING btree (key);





-- jira.issue_component definition

-- Drop table

-- DROP TABLE jira.issue_component;

CREATE TABLE jira.issue_component (
	"key" varchar NULL,
	component varchar NULL
);
CREATE INDEX issue_component_key_index ON jira.issue_component USING btree (key);



-- jira.issue_fix_version definition

-- Drop table

-- DROP TABLE jira.issue_fix_version;

CREATE TABLE jira.issue_fix_version (
	"key" varchar NULL,
	"version" varchar NULL
);
CREATE INDEX issue_fix_version_key_index ON jira.issue_fix_version USING btree (key);


-- jira.issue_label definition

-- Drop table

-- DROP TABLE jira.issue_label;

CREATE TABLE jira.issue_label (
	"key" varchar NULL,
	"label" varchar NULL
);
CREATE INDEX issue_label_key_index ON jira.issue_label USING btree (key);

-- jira.issue_link definition

-- Drop table

-- DROP TABLE jira.issue_link;

CREATE TABLE jira.issue_link (
	"key" varchar NULL,
	target varchar NULL,
	"type" varchar NULL,
	direction varchar NULL
);
CREATE INDEX issue_link_key_index ON jira.issue_link USING btree (key);

-- jira.issue_sprint definition

-- Drop table

-- DROP TABLE jira.issue_sprint;

CREATE TABLE jira.issue_sprint (
	"key" varchar NOT NULL,
	sprint_id int8 NOT NULL
);
CREATE INDEX issue_sprint_key_index ON jira.issue_sprint USING btree (key);


-- jira.issue_subtask definition

-- Drop table

-- DROP TABLE jira.issue_subtask;

CREATE TABLE jira.issue_subtask (
	"key" varchar NULL,
	target varchar NULL
);
CREATE INDEX issue_subtask_key_index ON jira.issue_subtask USING btree (key);


-- jira.issue_worklog definition

-- Drop table

-- DROP TABLE jira.issue_worklog;

CREATE TABLE jira.issue_worklog (
	"key" varchar NOT NULL,
	created timestamp NULL,
	updated timestamp NULL,
	start_date timestamp NULL,
	author varchar NULL,
	update_author varchar NULL,
	minutes_spent int4 NULL
);
CREATE INDEX issue_worklog_key_index ON jira.issue_worklog USING btree (key);


-- jira.sprint definition

-- Drop table

-- DROP TABLE jira.sprint;

CREATE TABLE jira.sprint (
	id int8 NOT NULL,
	state varchar NULL,
	"name" varchar NULL,
	start_date timestamp NULL,
	end_date timestamp NULL,
	complete_date timestamp NULL,
	origin_board_id int8 NOT NULL,
	board_id int8 NULL,
	CONSTRAINT sprint_pk PRIMARY KEY (id)
);
CREATE INDEX sprint_board_id_index ON jira.sprint USING btree (board_id);
CREATE INDEX sprint_origin_board_id_index ON jira.sprint USING btree (origin_board_id);

-- jira."version" definition

-- Drop table

-- DROP TABLE jira."version";

CREATE TABLE jira."version" (
	project_key varchar NOT NULL,
	"name" varchar NOT NULL,
	description varchar NULL,
	release_date timestamp NULL,
	released bool NULL,
	archived bool NULL
);
CREATE UNIQUE INDEX version_name_uindex ON jira.version USING btree (name);

