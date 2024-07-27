from type import Time, Timer

if __name__ == "__main__":
    t = Timer(
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