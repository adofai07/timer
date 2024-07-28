from type import Time, Timer, Blocker

if __name__ == "__main__":
    t = Timer(
        # Block until 10:30 am (uses 24h format)
        Blocker(hour=10, minute=30),

        Time("work"      , minute=50),
        Time("break"     , minute=5 ),
        Time("work"      , minute=50),
        Time("break"     , minute=5 ),
        Time("work"      , minute=50),
        Time("break"     , minute=5 ),
        Time("work"      , minute=50),
        Time("long break", minute=25),
    )

    t.run()