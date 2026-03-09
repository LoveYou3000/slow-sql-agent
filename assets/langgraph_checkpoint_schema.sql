create table memory.checkpoint_migrations
(
    v integer not null
        primary key
);

alter table memory.checkpoint_migrations
    owner to agent_user;

create table memory.checkpoints
(
    thread_id            text                      not null,
    checkpoint_ns        text  default ''::text    not null,
    checkpoint_id        text                      not null,
    parent_checkpoint_id text,
    type                 text,
    checkpoint           jsonb                     not null,
    metadata             jsonb default '{}'::jsonb not null,
    primary key (thread_id, checkpoint_ns, checkpoint_id)
);

alter table memory.checkpoints
    owner to agent_user;

create index checkpoints_thread_id_idx
    on memory.checkpoints (thread_id);

create table memory.checkpoint_blobs
(
    thread_id     text                  not null,
    checkpoint_ns text default ''::text not null,
    channel       text                  not null,
    version       text                  not null,
    type          text                  not null,
    blob          bytea,
    primary key (thread_id, checkpoint_ns, channel, version)
);

alter table memory.checkpoint_blobs
    owner to agent_user;

create index checkpoint_blobs_thread_id_idx
    on memory.checkpoint_blobs (thread_id);

create table memory.checkpoint_writes
(
    thread_id     text                  not null,
    checkpoint_ns text default ''::text not null,
    checkpoint_id text                  not null,
    task_id       text                  not null,
    idx           integer               not null,
    channel       text                  not null,
    type          text,
    blob          bytea                 not null,
    task_path     text default ''::text not null,
    primary key (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

alter table memory.checkpoint_writes
    owner to agent_user;

create index checkpoint_writes_thread_id_idx
    on memory.checkpoint_writes (thread_id);

