-- PostgreSQL schema for technical comment control

create table if not exists projects (
  project_id text primary key,
  project_name text not null,
  created_at timestamptz not null default now()
);

create table if not exists documents (
  document_id bigserial primary key,
  project_id text not null references projects(project_id) on delete cascade,
  document_code text not null,
  revision text,
  document_type text,
  source_hash text,
  source_uri text,
  created_at timestamptz not null default now(),
  unique(project_id, document_code, revision)
);

create table if not exists comments (
  comment_pk bigserial primary key,
  project_id text not null references projects(project_id) on delete cascade,
  comment_id text not null,
  source_comment_id text,
  severity text not null check (severity in ('GRAVE','ALTO','LEVE')),
  document_code text,
  revision text,
  page_or_item text,
  original_comment text not null,
  compiled_action text not null,
  origin_type text not null check (origin_type in ('FORMAL_COMMENT','NEW_DIVERGENCE')),
  status_control text not null default 'UNCHECKED' check (status_control in ('UNCHECKED','CHECKED')),
  responsible text,
  verifier text,
  created_at timestamptz not null default now(),
  verified_at timestamptz,
  reopened_count integer not null default 0 check (reopened_count >= 0),
  due_date date,
  unique(project_id, comment_id, origin_type)
);

create table if not exists comment_required_documents (
  comment_pk bigint not null references comments(comment_pk) on delete cascade,
  document_code text not null,
  primary key(comment_pk, document_code)
);

create table if not exists comment_evidence (
  evidence_id bigserial primary key,
  comment_pk bigint not null references comments(comment_pk) on delete cascade,
  evidence_document text not null,
  evidence_revision text,
  evidence_location text,
  evidence_text text not null,
  evidence_hash text,
  verified_by text,
  verified_at timestamptz not null default now()
);

create table if not exists technical_memory (
  memory_id bigserial primary key,
  project_id text references projects(project_id) on delete cascade,
  category text not null check (category in ('DECISION','LESSON','RULE','CONFLICT','PENDING','SOURCE','REGRESSION')),
  description text not null,
  status text not null default 'ACTIVE',
  origin text,
  document_code text,
  revision text,
  evidence text,
  impact text,
  regression_test text,
  app_version text,
  created_at timestamptz not null default now()
);

create table if not exists comment_events (
  event_id bigserial primary key,
  comment_pk bigint not null references comments(comment_pk) on delete cascade,
  event_type text not null,
  old_value jsonb,
  new_value jsonb,
  actor text,
  created_at timestamptz not null default now()
);

create table if not exists model_scores (
  score_id bigserial primary key,
  comment_pk bigint not null references comments(comment_pk) on delete cascade,
  model_name text not null,
  model_version text not null,
  score numeric(8,6) not null check (score >= 0 and score <= 1),
  features jsonb not null,
  created_at timestamptz not null default now()
);

create or replace function enforce_checked_comment_evidence()
returns trigger language plpgsql as $$
begin
  if new.status_control = 'CHECKED' then
    if not exists (select 1 from comment_evidence e where e.comment_pk = new.comment_pk) then
      raise exception 'CHECKED requires evidence';
    end if;
    if exists (
      select 1
      from comment_required_documents r
      where r.comment_pk = new.comment_pk
        and not exists (
          select 1 from comment_evidence e
          where e.comment_pk = new.comment_pk
            and e.evidence_document = r.document_code
        )
    ) then
      raise exception 'CHECKED requires evidence for every required document';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists trg_checked_comment_evidence on comments;
create constraint trigger trg_checked_comment_evidence
after insert or update of status_control on comments
deferrable initially deferred
for each row execute function enforce_checked_comment_evidence();

create or replace view vw_comment_control_powerbi as
select
  c.project_id,
  c.comment_id,
  c.origin_type,
  c.severity,
  c.document_code,
  c.revision,
  c.page_or_item,
  c.compiled_action,
  c.status_control,
  case when c.status_control = 'CHECKED' then 1 else 0 end as is_checked,
  c.responsible,
  c.verifier,
  c.created_at,
  c.verified_at,
  extract(epoch from (coalesce(c.verified_at, now()) - c.created_at))/86400.0 as age_days,
  c.reopened_count,
  c.due_date,
  count(distinct r.document_code) as required_document_count,
  count(distinct e.evidence_document) as evidence_document_count,
  count(distinct e.evidence_id) as evidence_count
from comments c
left join comment_required_documents r on r.comment_pk = c.comment_pk
left join comment_evidence e on e.comment_pk = c.comment_pk
group by c.comment_pk;

create or replace view vw_comment_integrity as
select
  project_id,
  count(*) filter (where origin_type = 'FORMAL_COMMENT') as formal_comment_count,
  count(*) filter (where origin_type = 'NEW_DIVERGENCE') as new_divergence_count,
  count(*) filter (where status_control = 'UNCHECKED') as unchecked_count,
  count(*) filter (where status_control = 'CHECKED') as checked_count,
  count(*) filter (
    where status_control = 'CHECKED'
      and not exists (select 1 from comment_evidence e where e.comment_pk = comments.comment_pk)
  ) as checked_without_evidence
from comments
group by project_id;
