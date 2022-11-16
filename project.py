LANG = "EN"

def hello_world(lang):
    if lang == "NL":
        return "Hallo wereld!"
    elif lang == "FR":
        return "Bonjour le monde!"
    else:
        return "Hello world!"

def test():
    assert hello_world("NL") == "Hallo wereld!", "Test failed"

def main():
    print(hello_world(LANG))

#test()
main()
