import aiosqlite, os

async def load_extension(bot):
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def create_tables():
    async with aiosqlite.connect("techniker.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS prefix (
            guild_id INTEGER PRIMARY KEY NOT NULL UNIQUE, 
            prefix TEXT NOT NULL, 
            created_at DATE NOT NULL,
            created_by INTEGER NOT NULL
            )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS welcome_channel (
            guild_id INTEGER NOT NULL UNIQUE, 
            channel_id INTEGER NOT NULL,
            welcome_message TEXT NOT NULL,
            created_at DATE NOT NULL,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES prefix(guild_id)
            )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS join_to_create (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            channel_size INTEGER NOT NULL,
            channel_owner INTEGER NOT NULL,
            channel_bits INTEGER NOT NULL,
            created_at DATE NOT NULL,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (guild_id) REFERENCES prefix(guild_id)
            )""")
        await db.execute("""CREATE TABLE IF NOT EXISTS join_to_create_users (
            guild_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            join_to_create_channel_id INTEGER NOT NULL,
            created_at DATE NOT NULL
            )""")
        await db.commit()
        print("Tables created ✅")
