state := 0

XButton1::
    WinGetClass, cls, A
    if (cls != "TVPMainWindow") {
        send, {XButton1}
        return
    }
    if (state = 0) {
        send, +e
        state := 1
    } else if (state = 1) {
        send, +n
        state := 0
    }
    return
