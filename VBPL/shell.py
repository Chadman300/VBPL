import basic

while True:
    #input
    text = input('VBPL > ') 
    if text.strip() == "": continue
    if text ==  "exit":
        break

    result, error = basic.run('<joe.vb>', text)

    if error:
        print(error.as_string())
    elif result: 
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))