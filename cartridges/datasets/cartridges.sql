create table public.cartridges (
  id uuid not null default gen_random_uuid (),
  owner_id text null,
  make text not null,
  model text not null,
  bullet_id uuid not null,
  cartridge_type text not null,
  data_source_name text null,
  data_source_link text null,
  cartridge_key text GENERATED ALWAYS as (
    (
      (
        (
          (
            ((lower(make) || '|'::text) || lower(model)) || '|'::text
          ) || lower(cartridge_type)
        ) || '|'::text
      ) || (bullet_id)::text
    )
  ) STORED null,
  created_at timestamp with time zone not null default now(),
  updated_at timestamp with time zone not null default now(),
  verified_by_id text null,
  constraint cartridges_pkey primary key (id),
  constraint cartridges_bullet_id_fkey foreign KEY (bullet_id) references bullets (id) on delete RESTRICT,
  constraint fk_cartridge_type foreign KEY (cartridge_type) references cartridge_types (name) on delete RESTRICT,
  constraint chk_data_source_link_url check (
    (
      (data_source_link is null)
      or (data_source_link ~* '^[a-z][a-z0-9+.-]*://'::text)
    )
  )
) TABLESPACE pg_default;

create unique INDEX IF not exists uq_cartridges_global_key on public.cartridges using btree (cartridge_key) TABLESPACE pg_default
where
  (owner_id is null);

create unique INDEX IF not exists uq_cartridges_user_key on public.cartridges using btree (cartridge_key, owner_id) TABLESPACE pg_default
where
  (owner_id is not null);

create index IF not exists idx_cartridges_owner on public.cartridges using btree (owner_id) TABLESPACE pg_default;

create index IF not exists idx_cartridges_bullet on public.cartridges using btree (bullet_id) TABLESPACE pg_default;

create trigger trg_cartridges_touch BEFORE
update on cartridges for EACH row
execute FUNCTION touch_updated_at ();