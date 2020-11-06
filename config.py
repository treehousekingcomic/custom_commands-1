# Extensions to be loaded
maker_base = "cogs.command.maker."
editor_base = "cogs.command.editor."
command_base = "cogs.command."
config_base = "cogs.config."
management_base = "cogs.management."
others_base = "cogs.others."

extensions = [
    "jishaku",
    maker_base + "embed",
    maker_base + "giverole",
    maker_base + "removerole",
    maker_base + "togglerole",
    maker_base + "giveremove",
    maker_base + "text",
    maker_base + "maker",
    maker_base + "randomresponse",
    editor_base + "editor",
    command_base + "alias",
    command_base + "variables",
    config_base + "config",
    management_base + "approver",
    management_base + "delete",
    management_base + "backup",
    management_base + "key",
    others_base + "help",
    others_base + "info",
    others_base + "others",
    "essentials.error_handler",
    "essentials.events_handler",
    "admin.admin",
    "admin.info",
    "admin.keychecker",
]

# Postgresql DB config
db_config = {
    "host": "localhost",
    "database": "ccbeta",
    "user": "shah",
    "password": "shah",
}

# which prefix should be assigned to new server
default_prefix = "**"

query_strings = [
    """
        CREATE TABLE IF NOT EXISTS guild_data(
            id SERIAL PRIMARY KEY NOT NULL,
            guild BIGINT NOT NULL,
            prefix TEXT NOT NULL,
            noprefix TEXT DEFAULT 'no' NOT NULL,
            cprefix TEXT NULL,
            UNIQUE(guild)
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS commands(
            id serial PRIMARY KEY,
            userid bigint NOT NULL,
            guild bigint NOT NULL,
            name text NOT NULL,
            type text NOT NULL,
            help TEXT NULL,
            approved VARCHAR(3) DEFAULT 'no' NOT NULL,
            FOREIGN KEY (guild) REFERENCES guild_data(guild) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS embed(
            id SERIAL PRIMARY KEY NOT NULL,
            command_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            thumbnail TEXT NULL,
            image TEXT NULL,
            FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS text(
            id SERIAL PRIMARY KEY,
            command_id BIGINT NOT NULL,
            content TEXT NOT NULL
    )
    """,
    """
        CREATE TABLE IF NOT EXISTS randomtext(
            id SERIAL PRIMARY KEY,
            command_id BIGINT NOT NULL,
            contents TEXT[] NOT NULL
    )
    """,
    """
        CREATE TABLE IF NOT EXISTS role(
            id SERIAL PRIMARY KEY NOT NULL,
            command_id BIGINT NOT NULL,
            role BIGINT[] NOT NULL,
            action TEXT NOT NULL,
            FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS aliases(
            id SERIAL PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            cmd_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            guild bigint NOT NULL,
            FOREIGN KEY (cmd_id) REFERENCES commands(id) ON DELETE CASCADE,
            FOREIGN KEY (guild) REFERENCES guild_data(guild) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS variables(
            id SERIAL PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            value TEXT NOT NULL,
            guild BIGINT NOT NULL,
            userid BIGINT NOT NULL,
            editorid BIGINT NULL,
            FOREIGN KEY (guild) REFERENCES guild_data(guild) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS multirole(
            id SERIAL PRIMARY KEY NOT NULL,
            command_id BIGINT NOT NULL,
            gives BIGINT[] NOT NULL,
            removes BIGINT[] NOT NULL,
            FOREIGN KEY (command_id) REFERENCES commands(id) ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS backups(
            id SERIAL PRIMARY KEY NOT NULL,
            guild BIGINT NOT NULL,
            userid BIGINT NOT NULL,
            aud BOOL NOT NULL,
            key TEXT NOT NULL,
            FOREIGN KEY (guild) REFERENCES guild_data(guild) ON DELETE CASCADE,
            UNIQUE(key)
        )
    """,
    """
        CREATE TABLE IF NOT EXISTS keys(
            id serial PRIMARY KEY,
            key VARCHAR(30) NOT NULL,
            guild bigint NOT NULL,
            created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            valid_till timestamp NOT NULL
        )
    """,
]
