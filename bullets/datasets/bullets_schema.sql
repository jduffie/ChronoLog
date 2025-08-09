create table public.bullets (
  id serial not null,
  user_id text not null,
  manufacturer text not null,
  model text not null,
  weight_grains integer not null,
  bullet_diameter_groove_mm double precision not null,
  bore_diameter_land_mm double precision not null,
  bullet_length_mm double precision null,
  ballistic_coefficient_g1 double precision null,
  ballistic_coefficient_g7 double precision null,
  sectional_density double precision null,
  min_req_twist_rate_in_per_rev double precision null,
  pref_twist_rate_in_per_rev double precision null,
  constraint bullets_pkey primary key (id),
  constraint bullets_user_id_fkey foreign KEY (user_id) references users (id)
) TABLESPACE pg_default;