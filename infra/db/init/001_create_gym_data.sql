CREATE TABLE IF NOT EXISTS public.gym (
    id SMALLINT PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO public.gym (id, name)
VALUES
    (1, 'Bella Vitalis GmbH Bad Bergzabern'),
    (7, 'Bella Vitalis GmbH Offenbach'),
    (11, 'Bella Vitalis GmbH Edenkoben'),
    (12, 'Bella Vitalis GmbH Marie-Curie-Str.'),
    (13, 'Bella Vitalis GmbH Albert-Einstein-Str.'),
    (20, 'Bella Vitalis GmbH Bellheim'),
    (21, 'Bella Vitalis GmbH Wörth'),
    (23, 'Bella Vitalis GmbH Herxheim'),
    (24, 'Bella Vitalis GmbH Dudenhofen'),
    (33, 'Fitnesswerk Kandel'),
    (34, 'Fitnesswerk Hassloch'),
    (37, 'Fitnesswerk Landau'),
    (38, 'Fitnesswerk Jockgrim'),
    (41, 'Fitnesswerk Edenkoben');

CREATE TABLE IF NOT EXISTS public.data (
    gym_id SMALLINT NOT NULL REFERENCES public.gym (id),
    workload NUMERIC(5, 2) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL
);
