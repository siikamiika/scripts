local utils = require "mp.utils"
local assdraw = require "mp.assdraw"

local ass_start = mp.get_property_osd("osd-ass-cc/0")
local ass_stop = mp.get_property_osd("osd-ass-cc/1")

function map(tbl, f)
    local t = {}
    if tbl == nil then return t end
    for k,v in pairs(tbl) do
        t[k] = f(v)
    end
    return t
end


local enabled = false

local analyzed_caption = {}
local word_idx = 0
local char_idx = 1

local pos_color = {}
-- noun
pos_color["名詞"] = "a0ffa0"
pos_color["固有名詞"] = "a0ffa0"
pos_color["代名詞"] = "a0ffa0"
-- particles and such
pos_color["接続助詞"] = "ff9080"
pos_color["助詞"] = "ff9080"
pos_color["接尾辞"] = "ff9080"
pos_color["接頭詞"] = "ff9080"
pos_color["接頭辞"] = "ff9080"
-- conjunction
pos_color["接続詞"] = "ffc0a0"
-- verb
pos_color["動詞"] = "4040ff"
pos_color["助動詞"] = "4040ff"
-- adjective
pos_color["形容詞"] = "7070ff"
pos_color["形状詞"] = "7070ff"
-- adverb
pos_color["副詞"] = "9090ff"
-- determiner
pos_color["連体詞"] = "b0b0ff"
-- interjection
pos_color["感動詞"] = "a0ffff"
-- number
pos_color["数"] = "ffff50"

function process_caption(_, caption)
    analyzed_caption = utils.parse_json(utils.subprocess({args={
        "curl",
        "-sS",
        "-d", utils.format_json(caption),
        "http://localhost:9874/mecab"
    }}).stdout)
    --print(utils.format_json(analyzed_caption))
    word_idx = 0
    char_idx = 1
    draw()
end

function draw()
    local output = map(analyzed_caption and analyzed_caption[1] or {}, function(word)
        return (pos_color[word.pos] and ("{\\c&H%s&}"):format(pos_color[word.pos]) or "") .. (word.literal or "") .. "{\\r}"
    end)

    if output[word_idx] then
        output[word_idx] = "{\\u1}" .. output[word_idx]
        mp.osd_message(ass_start .. "{\\fs10}" .. ass_stop .. table.concat(map(analyzed_caption[1][word_idx].translation.exact, function(t)
            local out = {}
            if t.words then
                table.insert(out, table.concat(map(t.words, function(w) return w.text end), ";"))
            end
            table.insert(out, ("[%s]"):format(table.concat(map(t.readings, function(r) return r.text end), ";")))
            table.insert(out, table.concat(map(t.translations, function(t_) return table.concat(t_.gloss, ", ") end), ass_start .. "{\\c&H0000ff&}" .. ass_stop .. " | " .. ass_start .. "{\\c&Hffffff&}" .. ass_stop))
            --print(table.concat(out, " "))
            return table.concat(out, " ")
        end), "\n"), 10)
    end

    local dw, dh, da = mp.get_osd_size()
    local ass = assdraw.ass_new()
    ass:append("{\\an2}")
    ass:append(table.concat(output, " "))
    mp.set_osd_ass(dw, dh, ass.text)
end

function change_word(offset)
    if not (analyzed_caption and analyzed_caption[1]) then return end
    if #(analyzed_caption)[1] >= word_idx + offset and word_idx + offset >= 1 then
        word_idx = word_idx + offset
        if not analyzed_caption[1][word_idx].translation then
            local w = analyzed_caption[1][word_idx]
            w.translation = utils.parse_json(utils.subprocess({args={
                "curl",
                "-sS",
                "-G",
                "--data-urlencode", ("query=%s"):format(w.lemma and w.lemma:sub(0, (w.lemma:find("-") or 0) - 1) or w.literal or ""),
                "http://localhost:9874/jmdict_e"
            }}).stdout)
            --print(utils.format_json(w.translation))
        end
        draw()
    end
end

function next_word() change_word(1) end
function prev_word() change_word(-1) end
-- TODO
function change_char(offset)
    draw()
end

function next_char() change_char(1) end
function prev_char() change_char(-1) end

function toggle()
    if enabled then -- disable
        mp.unobserve_property(process_caption)
        -- cleanup 
        mp.set_osd_ass(0, 0, "")
        mp.set_property_number("sub-scale", 1)
    else -- enable
        -- hiding subtitles would make sub-text return an empty string
        mp.set_property_number("sub-scale", 0)
        mp.observe_property("sub-text", "string", process_caption)
    end
    enabled = not enabled
    mp.osd_message(mp.get_script_name() .. (" %s"):format(enabled and "enabled" or "disabled"))
end


mp.add_key_binding("M", mp.get_script_name(), toggle)
mp.add_key_binding("Ctrl+MOUSE_BTN3", mp.get_script_name() .. "_next_word", next_word)
mp.add_key_binding("Ctrl+MOUSE_BTN4", mp.get_script_name() .. "_prev_word", prev_word)
mp.add_key_binding("Shift+MOUSE_BTN3", mp.get_script_name() .. "_next_char", next_char)
mp.add_key_binding("Shift+MOUSE_BTN4", mp.get_script_name() .. "_prev_char", prev_char)
