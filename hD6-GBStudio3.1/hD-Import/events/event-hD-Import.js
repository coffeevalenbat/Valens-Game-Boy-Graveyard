export const id = "VAL_BINARY_BGM";
export const name = "Play Imported hUGEDriver Track";
export const groups = ["EVENT_GROUP_MUSIC"];

// SONG FILE LIST
const song_list = [
    // Put your songs here
    [0,"Strap In And Suit Up - FΛDE","strap_in_SONG"]
];

export const fields = [
    {
        key: "song",
        label: "Song",
        type: "select",
        options: song_list,
        defaultValue: 0
    }
];

export const compile = (input, helpers) => {
  const {
    appendRaw,
    warnings,
  } = helpers;
  var symbol = song_list[input.song][2];
  appendRaw(`VM_MUSIC_PLAY ___bank_${symbol}, _${symbol}, .MUSIC_LOOP`);
};