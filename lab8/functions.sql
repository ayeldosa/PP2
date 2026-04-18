CREATE OR REPLACE FUNCTION search_contacts(p text)
RETURNS TABLE(username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT pbook.username, pbook.phone
    FROM phonebook pbook
    WHERE pbook.username ILIKE '%' || p || '%'
       OR pbook.phone ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(id INT, username VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.username, p.phone
    FROM phonebook p
    LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;