from src.client import Client

if __name__ == "__main__":
    c = Client("Bar")
    c.connect()
    
    c.loop()