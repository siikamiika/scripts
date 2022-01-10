state := 0

isActive() {
    WinGetClass, cls, A
    return cls = "TVPMainWindow"
}

XButton1::
    if (!isActive()) {
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

#f::
    if (isActive()) {
        send, {F9}
    }
    return