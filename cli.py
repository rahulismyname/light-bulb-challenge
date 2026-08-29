from light_bulb import LightBulb


def cli():
    bulb = LightBulb()
    while True:
        text = input("User: ")
        print(text)


def main():
    cli()

if __name__ == "__main__":
    main()