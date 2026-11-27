-- ============================================================================
-- Strict Day - initial schema
-- Mirrors the device-local Room schema (app/src/main/java/com/strictday/data/
-- local/room/entity) so device -> cloud sync is a 1:1 mapping. Timestamps
-- that the app stores as epoch-milliseconds are kept as bigint for parity;
-- wall-clock columns are added only where the server needs to reason in time.
--
-- Honesty contract: the server is the source of truth for verification. The
-- device only uploads normalized verification_events; the verify-task edge
-- function evaluates rules on the server and records the outcome.
-- ============================================================================

-- RLS helper: schedules/tasks always belong to the invoking user.
create or replace function public.auth_uid()
returns uuid
language sql
stable
as $$
  select auth.uid();
$$;

-- ---------------------------------------------------------------------------
-- profiles
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    display_name text,
    default_strictness text not null default 'normal',
    onboarded boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
    for select using (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles
    for update using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own" on public.profiles
    for insert with check (auth.uid() = id);

-- Auto-provision a profile row when a user signs up.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, display_name)
    values (new.id, coalesce(new.raw_user_meta_data ->> 'displayName', ''))
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- schedules
-- ---------------------------------------------------------------------------
create table if not exists public.schedules (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    local_date date not null,
    status text not null default 'draft',
    created_at timestamptz not null default now(),
    unique (user_id, local_date)
);

alter table public.schedules enable row level security;

drop policy if exists "schedules_select_own" on public.schedules;
create policy "schedules_select_own" on public.schedules
    for select using (auth.uid() = user_id);

drop policy if exists "schedules_insert_own" on public.schedules;
create policy "schedules_insert_own" on public.schedules
    for insert with check (auth.uid() = user_id);

drop policy if exists "schedules_update_own" on public.schedules;
create policy "schedules_update_own" on public.schedules
    for update using (auth.uid() = user_id);

drop policy if exists "schedules_delete_own" on public.schedules;
create policy "schedules_delete_own" on public.schedules
    for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- tasks
-- ---------------------------------------------------------------------------
create table if not exists public.tasks (
    id uuid primary key default gen_random_uuid(),
    schedule_id uuid not null references public.schedules (id) on delete cascade,
    user_id uuid not null references auth.users (id) on delete cascade,
    title text not null,
    description text not null default '',
    starts_at bigint not null,                 -- epoch millis
    ends_at bigint not null,                   -- epoch millis
    strictness text not null default 'normal',
    status text not null default 'pending',
    order_index int not null default 0,
    allowed_apps jsonb not null default '[]',
    blocked_apps jsonb not null default '[]',
    created_at timestamptz not null default now()
);

create index if not exists tasks_schedule_idx on public.tasks (schedule_id);
create index if not exists tasks_user_idx on public.tasks (user_id);
create index if not exists tasks_status_idx on public.tasks (status);

alter table public.tasks enable row level security;

drop policy if exists "tasks_select_own" on public.tasks;
create policy "tasks_select_own" on public.tasks
    for select using (auth.uid() = user_id);

drop policy if exists "tasks_insert_own" on public.tasks;
create policy "tasks_insert_own" on public.tasks
    for insert with check (auth.uid() = user_id);

drop policy if exists "tasks_update_own" on public.tasks;
create policy "tasks_update_own" on public.tasks
    for update using (auth.uid() = user_id);

drop policy if exists "tasks_delete_own" on public.tasks;
create policy "tasks_delete_own" on public.tasks
    for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- verification_rules
-- ---------------------------------------------------------------------------
create table if not exists public.verification_rules (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references public.tasks (id) on delete cascade,
    provider text not null,
    event_type text not null,
    operator text not null,
    target_value text not null default '',
    min_count int not null default 0,
    min_duration_seconds bigint not null default 0,
    created_at timestamptz not null default now()
);

create index if not exists verification_rules_task_idx on public.verification_rules (task_id);

alter table public.verification_rules enable row level security;

drop policy if exists "verification_rules_select_own" on public.verification_rules;
create policy "verification_rules_select_own" on public.verification_rules
    for select using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_rules.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_rules_insert_own" on public.verification_rules;
create policy "verification_rules_insert_own" on public.verification_rules
    for insert with check (
        exists (
            select 1 from public.tasks t
            where t.id = verification_rules.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_rules_update_own" on public.verification_rules;
create policy "verification_rules_update_own" on public.verification_rules
    for update using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_rules.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_rules_delete_own" on public.verification_rules;
create policy "verification_rules_delete_own" on public.verification_rules
    for delete using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_rules.task_id and t.user_id = auth.uid()
        )
    );

-- ---------------------------------------------------------------------------
-- verification_events - immutable server-side evidence uploads
-- ---------------------------------------------------------------------------
create table if not exists public.verification_events (
    id bigint generated always as identity primary key,
    task_id uuid not null references public.tasks (id) on delete cascade,
    provider text not null,
    event_type text not null,
    external_id text not null,
    occurred_at timestamptz not null,
    subject text not null default '',
    metrics jsonb not null default '{}',
    received_at timestamptz not null default now(),
    unique (task_id, provider, external_id)
);

create index if not exists verification_events_task_time_idx
    on public.verification_events (task_id, occurred_at desc);

alter table public.verification_events enable row level security;

drop policy if exists "verification_events_insert_own" on public.verification_events;
create policy "verification_events_insert_own" on public.verification_events
    for insert with check (
        exists (
            select 1 from public.tasks t
            where t.id = verification_events.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_events_select_own" on public.verification_events;
create policy "verification_events_select_own" on public.verification_events
    for select using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_events.task_id and t.user_id = auth.uid()
        )
    );

-- ---------------------------------------------------------------------------
-- verification_state - outcome of the last server-side evaluation
-- ---------------------------------------------------------------------------
create table if not exists public.verification_state (
    task_id uuid primary key references public.tasks (id) on delete cascade,
    provider text not null default 'none',
    is_verified boolean not null default false,
    last_checked_at timestamptz not null default now(),
    events_json jsonb not null default '[]'
);

alter table public.verification_state enable row level security;

drop policy if exists "verification_state_insert_own" on public.verification_state;
create policy "verification_state_insert_own" on public.verification_state
    for insert with check (
        exists (
            select 1 from public.tasks t
            where t.id = verification_state.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_state_select_own" on public.verification_state;
create policy "verification_state_select_own" on public.verification_state
    for select using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_state.task_id and t.user_id = auth.uid()
        )
    );

drop policy if exists "verification_state_update_own" on public.verification_state;
create policy "verification_state_update_own" on public.verification_state
    for update using (
        exists (
            select 1 from public.tasks t
            where t.id = verification_state.task_id and t.user_id = auth.uid()
        )
    );

-- ---------------------------------------------------------------------------
-- integrations - external provider credentials (server-stored, device-scoped)
-- ---------------------------------------------------------------------------
create table if not exists public.integrations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    provider text not null,
    status text not null default 'disconnected',
    scopes jsonb not null default '[]',
    metadata jsonb not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, provider)
);

alter table public.integrations enable row level security;

drop policy if exists "integrations_select_own" on public.integrations;
create policy "integrations_select_own" on public.integrations
    for select using (auth.uid() = user_id);

drop policy if exists "integrations_insert_own" on public.integrations;
create policy "integrations_insert_own" on public.integrations
    for insert with check (auth.uid() = user_id);

drop policy if exists "integrations_update_own" on public.integrations;
create policy "integrations_update_own" on public.integrations
    for update using (auth.uid() = user_id);

drop policy if exists "integrations_delete_own" on public.integrations;
create policy "integrations_delete_own" on public.integrations
    for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- device_policies
-- ---------------------------------------------------------------------------
create table if not exists public.device_policies (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    task_id uuid not null references public.tasks (id) on delete cascade,
    device_id text not null,
    mode text not null default 'normal',
    allowed_packages jsonb not null default '[]',
    blocked_packages jsonb not null default '[]',
    status text not null default 'inactive',
    start_time bigint not null,                -- epoch millis
    end_time bigint not null,                  -- epoch millis
    unlock_condition text not null default '',
    emergency_access_allowed boolean not null default false,
    activated_at bigint,
    released_at bigint,
    created_at timestamptz not null default now()
);

create index if not exists device_policies_task_idx on public.device_policies (task_id);
create index if not exists device_policies_device_idx on public.device_policies (device_id);

alter table public.device_policies enable row level security;

drop policy if exists "device_policies_select_own" on public.device_policies;
create policy "device_policies_select_own" on public.device_policies
    for select using (auth.uid() = user_id);

drop policy if exists "device_policies_insert_own" on public.device_policies;
create policy "device_policies_insert_own" on public.device_policies
    for insert with check (auth.uid() = user_id);

drop policy if exists "device_policies_update_own" on public.device_policies;
create policy "device_policies_update_own" on public.device_policies
    for update using (auth.uid() = user_id);

drop policy if exists "device_policies_delete_own" on public.device_policies;
create policy "device_policies_delete_own" on public.device_policies
    for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- audit_events - append-only tamper-evident log
-- ---------------------------------------------------------------------------
create table if not exists public.audit_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    device_id text not null,
    task_id uuid references public.tasks (id) on delete set null,
    type text not null,
    payload jsonb not null default '{}',
    created_at timestamptz not null default now()
);

create index if not exists audit_events_user_idx on public.audit_events (user_id, created_at desc);
create index if not exists audit_events_task_idx on public.audit_events (task_id);

alter table public.audit_events enable row level security;

drop policy if exists "audit_events_insert_own" on public.audit_events;
create policy "audit_events_insert_own" on public.audit_events
    for insert with check (auth.uid() = user_id);

drop policy if exists "audit_events_select_own" on public.audit_events;
create policy "audit_events_select_own" on public.audit_events
    for select using (auth.uid() = user_id);