-- PostgreSQL schema for technical comment control

create table if not exists projects (
  project_id text primary key,
  project_name text not null,
  created_at timestamptz not null default now()
);

create table if not exists comment_batches (
  batch_id text primary key,
  project_id text not null references projects(project_id) on delete cascade,
  source_name text,
  source_hash text,
  source_formal_comment_count integer not null check (source_formal_comment_count >= 0),
  preflight_status text not null default 'ANALYZING',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(project_id, source_hash)
);

alter table comment_batches add column if not exists preflight_status text not null default 'ANALYZING';
alter table comment_batches add column if not exists updated_at timestamptz not null default now();

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

create table if not exists clarification_questions (
  question_pk bigserial primary key,
  batch_id text not null references comment_batches(batch_id) on delete cascade,
  question_id text not null,
  topic text not null,
  question_text text not null,
  why_needed text not null,
  related_documents jsonb not null default '[]'::jsonb,
  status text not null default 'OPEN' check (status in ('OPEN','RESOLVED','DISMISSED')),
  resolution text,
  resolution_type text check (resolution_type in ('CONFIRMED_ERROR','DISMISSED','FORMAL_OBJECTIVE')),
  resolved_by text,
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  unique(batch_id, question_id)
);

create index if not exists idx_clarification_batch_status on clarification_questions(batch_id, status);

create table if not exists comments (
  comment_pk bigserial primary key,
  batch_id text not null references comment_batches(batch_id) on delete cascade,
  project_id text not null references projects(project_id) on delete cascade,
  comment_id text not null,
  source_comment_id text,
  severity text not null check (severity in ('GRAVE','ALTO','LEVE')),
  document_code text,
  revision text,
  page_or_item text,
  original_comment text not null,
  compiled_action text not null,
  finding_basis text,
  source_location text,
  origin_type text not null check (origin_type in ('FORMAL_COMMENT','NEW_DIVERGENCE')),
  status_control text not null default 'UNCHECKED' check (status_control in ('UNCHECKED','CHECKED')),
  responsible text,
  verifier text,
  created_at timestamptz not null default now(),
  verified_at timestamptz,
  reopened_count integer not null default 0 check (reopened_count >= 0),
  due_date date,
  unique(batch_id, comment_id, origin_type)
);

alter table comments add column if not exists finding_basis text;
alter table comments add column if not exists source_location text;

create index if not exists idx_comments_project_status on comments(project_id, status_control);
create index if not exists idx_comments_batch_origin on comments(batch_id, origin_type);
create index if not exists idx_comments_document on comments(project_id, document_code);

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

create index if not exists idx_comment_evidence_comment on comment_evidence(comment_pk);

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

create or replace function assert_preflight_resolved(p_batch_id text)
returns void language plpgsql as $$
declare
  open_count integer;
  batch_status text;
begin
  select preflight_status into batch_status from comment_batches where batch_id = p_batch_id;
  if batch_status is null then
    raise exception 'Unknown comment batch: %', p_batch_id;
  end if;

  select count(*) into open_count
  from clarification_questions
  where batch_id = p_batch_id and status = 'OPEN';

  if open_count > 0 then
    raise exception 'WAITING_CLARIFICATION: batch % has % open question(s)', p_batch_id, open_count;
  end if;

  if batch_status not in ('READY_TO_GENERATE','GENERATED') then
    raise exception 'Batch % is not ready to generate. Current status: %', p_batch_id, batch_status;
  end if;
end;
$$;

create or replace function enforce_checked_comment_evidence()
returns trigger language plpgsql as $$
begin
  if new.status_control = 'CHECKED' then
    if new.verifier is null or new.verified_at is null then
      raise exception 'CHECKED requires human verifier and verified_at';
    end if;
    if not exists (select 1 from comment_evidence e where e.comment_pk = new.comment_pk) then
      raise exception 'CHECKED requires evidence';
    end if;
    if exists (
      select 1 from comment_required_documents r
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

create or replace function assert_comment_batch_integrity(p_batch_id text)
returns void language plpgsql as $$
declare
  expected_count integer;
  actual_count integer;
begin
  perform assert_preflight_resolved(p_batch_id);

  select source_formal_comment_count into expected_count
  from comment_batches where batch_id = p_batch_id;

  select count(*) into actual_count
  from comments
  where batch_id = p_batch_id and origin_type = 'FORMAL_COMMENT';

  if actual_count <> expected_count then
    raise exception 'Formal comment count mismatch for batch %: expected %, actual %',
      p_batch_id, expected_count, actual_count;
  end if;
end;
$$;

create or replace view vw_clarification_status as
select
  b.batch_id,
  b.project_id,
  b.preflight_status,
  count(q.question_pk) as clarification_count,
  count(q.question_pk) filter (where q.status = 'OPEN') as open_clarification_count,
  count(q.question_pk) filter (where q.status = 'RESOLVED') as resolved_clarification_count,
  count(q.question_pk) filter (where q.status = 'DISMISSED') as dismissed_clarification_count
from comment_batches b
left join clarification_questions q on q.batch_id = b.batch_id
group by b.batch_id;

create or replace view vw_comment_control_powerbi as
select
  c.batch_id,
  c.project_id,
  c.comment_id,
  c.origin_type,
  c.severity,
  c.document_code,
  c.revision,
  c.page_or_item,
  c.compiled_action,
  c.finding_basis,
  c.source_location,
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
  b.batch_id,
  b.project_id,
  b.source_name,
  b.source_hash,
  b.source_formal_comment_count,
  b.preflight_status,
  count(c.comment_pk) filter (where c.origin_type = 'FORMAL_COMMENT') as registered_formal_comment_count,
  count(c.comment_pk) filter (where c.origin_type = 'NEW_DIVERGENCE') as new_divergence_count,
  count(c.comment_pk) filter (where c.status_control = 'UNCHECKED') as unchecked_count,
  count(c.comment_pk) filter (where c.status_control = 'CHECKED') as checked_count,
  count(q.question_pk) filter (where q.status = 'OPEN') as open_clarification_count,
  case
    when count(c.comment_pk) filter (where c.origin_type = 'FORMAL_COMMENT') = b.source_formal_comment_count
      and count(q.question_pk) filter (where q.status = 'OPEN') = 0
      then 'OK'
    else 'ERRO'
  end as batch_integrity
from comment_batches b
left join comments c on c.batch_id = b.batch_id
left join clarification_questions q on q.batch_id = b.batch_id
group by b.batch_id;
