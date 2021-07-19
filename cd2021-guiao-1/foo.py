from src.client import Client

if __name__ == "__main__":
    c = Client("Foo")
    c.connect()
    
    c.loop()