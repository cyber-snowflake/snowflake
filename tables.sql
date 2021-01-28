/** Guilds Settings **/

create table guilds
(
    guild_id   bigint                    not null,
    prefix     varchar(16) default null,
    lang       varchar(16) default 'en_US',
    tz         varchar(32) default 'UTC' not null
);

create unique index guilds_guild_id_uindex
    on guilds (guild_id);

alter table guilds
    add constraint guilds_pk
        primary key (guild_id);

/** Reminders **/

create table reminders
(
    id                    bigserial not null,
    user_id               bigint    not null,
    created_at            timestamp without time zone default timezone('utc', now()),
    trigger_at            timestamp without time zone default timezone('utc', now()),
    initiator_message_url text,
    content               text                        default '...'
);

create unique index reminders_id_uindex
    on reminders (id);

alter table reminders
    add constraint reminders_pk
        primary key (id);

/** Blacklist **/
create table blacklisted
(
	user_id bigint not null,
	reason text default 'because'
);

create unique index blacklisted_user_id_uindex
	on blacklisted (user_id);

alter table blacklisted
	add constraint blacklisted_pk
		primary key (user_id);

/** Stats **/
create table stats
(
    guild_id bigint not null,
    _date date default (current_date at time zone 'UTC')::date not null,
    members_joined bigint default 0 not null,
    members_left bigint default 0 not null,
    members_banned bigint default 0 not null,
    messages_sent bigint default 0 not null,
    messages_edited bigint default 0 not null,
    messages_deleted bigint default 0 not null
);

create index stats__date_index
    on stats (_date);

create unique index stats_guild_id_and__date_uindex
    on stats (guild_id, _date);

create index stats_guild_id_index
    on stats (guild_id);
