
create table public.factory_cartridge_specs (
  id serial not null,
  user_id text not null,
  make text not null,
  model text not null,
  bullet_id integer not null,
  constraint factory_cartridge_specs_pkey primary key (id),
  constraint factory_cartridge_specs_user_id_make_model_key unique (user_id, make, model),
  constraint factory_cartridge_specs_bullet_id_fkey foreign key (bullet_id)
    references public.bullets (id),
  constraint factory_cartridge_specs_user_id_fkey foreign key (user_id)
    references public.users (id)
) tablespace pg_default;