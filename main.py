from type import Time, Timer

if __name__ == "__main__":
    t = Timer(
        Time("Eat sandwiches", minute=1),
        Time("Eat pizza", minute=1),
    )

    t.run()