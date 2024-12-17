create database diploma
    with owner admin;

create type public.user_role as enum ('user', 'moderator', 'admin');

alter type public.user_role owner to admin;

create type public.confirmationtype as enum ('registration', 'password_reset');

alter type public.confirmationtype owner to admin;

create type public.notificationtype as enum ('info', 'success', 'warning', 'error');

alter type public.notificationtype owner to admin;

create type public.reportstatus as enum ('open', 'closed', 'rejected', 'satisfied');

alter type public.reportstatus owner to admin;

create type public.translationtaskstatus as enum ('created', 'started', 'failed', 'completed');

alter type public.translationtaskstatus owner to admin;

create table public.alembic_version
(
    version_num varchar(32) not null
        constraint alembic_version_pkc
            primary key
);

alter table public.alembic_version
    owner to admin;

create table public.gptranslate_ai_models
(
    id         serial
        primary key,
    show_name  varchar(50) not null,
    name       varchar     not null,
    provider   varchar     not null,
    created_at timestamp   not null,
    deleted_at timestamp
);

alter table public.gptranslate_ai_models
    owner to admin;

create table public.gptranslate_languages
(
    id       serial
        primary key,
    name     varchar not null
        unique,
    iso_code varchar not null
        unique
);

alter table public.gptranslate_languages
    owner to admin;

create table public.gptranslate_report_reasons
(
    id             serial
        primary key,
    text           varchar not null
        unique,
    order_position integer not null
        unique
);

alter table public.gptranslate_report_reasons
    owner to admin;

create table public.gptranslate_style_prompts
(
    id         serial
        primary key,
    title      varchar(20) not null
        unique,
    text       varchar     not null
        unique,
    created_at timestamp   not null,
    deleted_at timestamp
);

alter table public.gptranslate_style_prompts
    owner to admin;

create table public.gptranslate_users
(
    id                   uuid        not null
        primary key,
    name                 varchar(20) not null,
    email                varchar     not null
        unique,
    email_verified       boolean     not null,
    password_hash        varchar(60) not null,
    role                 user_role   not null,
    logged_with_provider varchar,
    provider_id          varchar,
    created_at           timestamp   not null,
    deleted_at           timestamp
);

comment on column public.gptranslate_users.logged_with_provider is 'External OAuth provider name user has registered with';

comment on column public.gptranslate_users.provider_id is 'User''s ID from OAuth provider user has registered with';

alter table public.gptranslate_users
    owner to admin;

create table public.gptranslate_articles
(
    id                  uuid        not null
        primary key,
    title               varchar(50) not null,
    text                text        not null,
    user_id             uuid        not null
        references public.gptranslate_users
            on delete cascade,
    language_id         integer
        references public.gptranslate_languages
            on delete cascade,
    original_article_id uuid
        references public.gptranslate_articles
            on delete cascade,
    "like"              boolean,
    created_at          timestamp   not null,
    deleted_at          timestamp
);

alter table public.gptranslate_articles
    owner to admin;

create table public.gptranslate_configs
(
    id           serial
        primary key,
    user_id      uuid        not null
        references public.gptranslate_users
            on delete cascade,
    prompt_id    integer
        references public.gptranslate_style_prompts
            on delete cascade,
    name         varchar(20) not null,
    language_ids integer[]   not null,
    model_id     integer
        references public.gptranslate_ai_models
            on delete cascade,
    created_at   timestamp   not null,
    deleted_at   timestamp
);

alter table public.gptranslate_configs
    owner to admin;

create table public.gptranslate_confirmation_codes
(
    id         serial
        primary key,
    code       varchar          not null
        unique,
    reason     confirmationtype not null,
    user_id    uuid             not null
        references public.gptranslate_users
            on delete cascade,
    expired_at timestamp        not null,
    is_used    boolean          not null,
    created_at timestamp        not null
);

comment on column public.gptranslate_confirmation_codes.code is 'The value of the code';

alter table public.gptranslate_confirmation_codes
    owner to admin;

create table public.gptranslate_notifications
(
    id         uuid             not null
        primary key,
    title      varchar          not null,
    text       varchar          not null,
    user_id    uuid             not null
        references public.gptranslate_users
            on delete cascade,
    type       notificationtype not null,
    read_at    timestamp,
    created_at timestamp        not null
);

alter table public.gptranslate_notifications
    owner to admin;

create table public.gptranslate_sessions
(
    id               uuid         not null
        primary key,
    user_id          uuid         not null
        references public.gptranslate_users
            on delete cascade,
    ip               varchar(15)  not null,
    user_agent       varchar(100) not null,
    is_closed        boolean      not null,
    refresh_token_id uuid         not null,
    created_at       timestamp    not null,
    closed_at        timestamp
);

alter table public.gptranslate_sessions
    owner to admin;

create table public.gptranslate_reports
(
    id                uuid          not null
        primary key,
    text              varchar(1024) not null,
    article_id        uuid          not null
        references public.gptranslate_articles
            on delete cascade,
    status            reportstatus  not null,
    closed_by_user_id uuid
        references public.gptranslate_users
            on delete cascade,
    reason_id         integer       not null
        references public.gptranslate_report_reasons
            on delete cascade,
    created_at        timestamp     not null,
    closed_at         timestamp
);

alter table public.gptranslate_reports
    owner to admin;

create table public.gptranslate_translation_tasks
(
    id                    uuid                  not null
        primary key,
    article_id            uuid                  not null
        references public.gptranslate_articles
            on delete cascade,
    target_language_id    integer               not null
        references public.gptranslate_languages
            on delete cascade,
    prompt_id             integer               not null
        references public.gptranslate_style_prompts
            on delete cascade,
    model_id              integer               not null
        references public.gptranslate_ai_models
            on delete cascade,
    status                translationtaskstatus not null,
    data                  jsonb,
    translated_article_id uuid
        references public.gptranslate_articles
            on delete cascade,
    created_at            timestamp             not null,
    deleted_at            timestamp
);

comment on column public.gptranslate_translation_tasks.data is 'Additional data related to the translation task (e.g., errors or metadata)';

alter table public.gptranslate_translation_tasks
    owner to admin;

create table public.gptranslate_report_comments
(
    id         uuid         not null
        primary key,
    text       varchar(100) not null,
    sender_id  uuid         not null
        references public.gptranslate_users
            on delete cascade,
    report_id  uuid         not null
        references public.gptranslate_reports
            on delete cascade,
    created_at timestamp    not null
);

alter table public.gptranslate_report_comments
    owner to admin;

