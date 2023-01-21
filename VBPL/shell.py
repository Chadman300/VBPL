import basic

exit = False
while exit == False:
    #input
    text = input('VBPL > ')
    print(text)
    if text ==  "exit":
        exit = True

    #grab result and errors from the basic script
    result, error = basic.run('<joe.vb>', text)

    if error:
        print(error.as_string())
    else: print(result)