-- ============================================================
-- procedures.sql  –  Stored procedures & functions (TSIS 1)
-- ============================================================

-- ──────────────────────────────────────────────
-- 1. add_phone
--    Adds a phone number to an existing contact.
-- ──────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INTEGER;
BEGIN
    SELECT id INTO v_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home, work, or mobile.', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to contact id=%.', p_phone, p_type, v_id;
END;
$$;

-- ──────────────────────────────────────────────
-- 2. move_to_group
--    Moves a contact to a group; creates group if missing.
-- ──────────────────────────────────────────────
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- Find contact
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE first_name ILIKE p_contact_name
       OR (first_name || ' ' || COALESCE(last_name, '')) ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- Find or create group
    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Group "%" created (id=%).', p_group_name, v_group_id;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    RAISE NOTICE 'Contact id=% moved to group "%" (id=%).', v_contact_id, p_group_name, v_group_id;
END;
$$;

-- ──────────────────────────────────────────────
-- 3. search_contacts
--    Full-text pattern search across name, email,
--    and ALL phone numbers in the phones table.
-- ──────────────────────────────────────────────
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name                              AS group_name,
        STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR COALESCE(c.last_name, '') ILIKE '%' || p_query || '%'
        OR COALESCE(c.email, '')     ILIKE '%' || p_query || '%'
        OR EXISTS (
            SELECT 1 FROM phones ph
            WHERE ph.contact_id = c.id
              AND ph.phone ILIKE '%' || p_query || '%'
        )
    GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name
    ORDER BY c.first_name;
END;
$$;

-- ──────────────────────────────────────────────
-- 4. get_contacts_page  (pagination helper)
--    Returns one page of contacts ordered by chosen field.
-- ──────────────────────────────────────────────
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit  INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0,
    p_order  VARCHAR DEFAULT 'first_name'   -- first_name | birthday | created_at
)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    phones     TEXT,
    created_at TIMESTAMP
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                g.name,
                STRING_AGG(p.phone || '' ('' || COALESCE(p.type,''?'') || '')'', '', ''),
                c.created_at
         FROM contacts c
         LEFT JOIN groups g ON g.id = c.group_id
         LEFT JOIN phones p ON p.contact_id = c.id
         GROUP BY c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at
         ORDER BY %I
         LIMIT %s OFFSET %s',
        p_order, p_limit, p_offset
    );
END;
$$;
