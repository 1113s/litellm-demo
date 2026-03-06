INSERT INTO tenants (id, name, status)
VALUES ('00000000-0000-0000-0000-000000000001', 'default', 'active')
ON CONFLICT (name) DO NOTHING;
