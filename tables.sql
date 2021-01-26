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
