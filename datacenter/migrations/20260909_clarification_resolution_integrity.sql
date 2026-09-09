-- Enforce clarification resolution integrity before artifact generation.

create or replace function enforce_clarification_resolution_integrity()
returns trigger language plpgsql as $$
begin
  if new.status = 'OPEN' then
    if new.resolution is not null
       or new.resolution_type is not null
       or new.resolved_by is not null
       or new.resolved_at is not null then
      raise exception 'OPEN clarification cannot contain resolution fields';
    end if;
    return new;
  end if;

  if new.resolution is null or btrim(new.resolution) = '' then
    raise exception 'Resolved clarification requires resolution text';
  end if;
  if new.resolution_type is null then
    raise exception 'Resolved clarification requires resolution_type';
  end if;
  if new.resolved_by is null or btrim(new.resolved_by) = '' then
    raise exception 'Resolved clarification requires resolved_by';
  end if;
  if new.resolved_at is null then
    raise exception 'Resolved clarification requires resolved_at';
  end if;

  if new.status = 'DISMISSED' and new.resolution_type <> 'DISMISSED' then
    raise exception 'DISMISSED clarification requires resolution_type=DISMISSED';
  end if;
  if new.status = 'RESOLVED' and new.resolution_type = 'DISMISSED' then
    raise exception 'resolution_type=DISMISSED requires status=DISMISSED';
  end if;
  return new;
end;
$$;

drop trigger if exists trg_clarification_resolution_integrity on clarification_questions;
create trigger trg_clarification_resolution_integrity
before insert or update on clarification_questions
for each row execute function enforce_clarification_resolution_integrity();

create or replace function assert_preflight_resolved(p_batch_id text)
returns void language plpgsql as $$
declare
  open_count integer;
  invalid_resolution_count integer;
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

  select count(*) into invalid_resolution_count
  from clarification_questions
  where batch_id = p_batch_id
    and status in ('RESOLVED','DISMISSED')
    and (
      resolution is null or btrim(resolution) = ''
      or resolution_type is null
      or resolved_by is null or btrim(resolved_by) = ''
      or resolved_at is null
      or (status = 'DISMISSED' and resolution_type <> 'DISMISSED')
      or (status = 'RESOLVED' and resolution_type = 'DISMISSED')
    );

  if invalid_resolution_count > 0 then
    raise exception 'INVALID_CLARIFICATION_RESOLUTION: batch % has % invalid resolved question(s)',
      p_batch_id, invalid_resolution_count;
  end if;

  if batch_status not in ('READY_TO_GENERATE','GENERATED') then
    raise exception 'Batch % is not ready to generate. Current status: %', p_batch_id, batch_status;
  end if;
end;
$$;
