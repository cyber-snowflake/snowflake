/** Guilds Settings **/

create table guilds
(
    guild_id   bigint                    not null,
    prefix     varchar(16) default null,
    lang       varchar(16) default 'en_US',
    tz         varchar(32) default 'UTC' not null,
    main_vc_id bigint      default null
);

create unique index guilds_guild_id_uindex
    on guilds (guild_id);

alter table guilds
    add constraint guilds_pk
        primary key (guild_id);

/** User Settings **/

create table if not exists user_settings
(
    guild_id bigint                 not null,
    user_id  bigint                 not null,
    opened   bool     default false not null,
    limits   smallint default 2     not null
);

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


