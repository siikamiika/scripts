function change_samplerate ()
    while true do
        samplerate = mp.get_property_native("audio-samplerate")
        if samplerate then break end
        os.execute("sleep 0.5")
    end
    os.execute("curl http://siikamiika-w7.lan:9877/samplerate?val="..samplerate)
end
mp.add_timeout(1, change_samplerate)
