CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE username = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE username = p_name;
    ELSE
        INSERT INTO phonebook(username, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;



CREATE OR REPLACE PROCEDURE bulk_insert()
LANGUAGE plpgsql AS $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN SELECT * FROM phonebook LOOP
        IF length(rec.phone) < 5 THEN
            RAISE NOTICE 'Invalid phone: %', rec.phone;
        END IF;
    END LOOP;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook
    WHERE username = p_value OR phone = p_value;
END;
$$;