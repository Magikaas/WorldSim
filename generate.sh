#!/bin/sh
# Generate tree file

if [ -z $1 ]; then
    echo ERROR: No tree type specified
    exit 1
fi

commandFileName="obj/worldobj/tree/$1.js"

# Add parameters for whether the command has parameters ,is an autocomplete command and requires the bot to be in a voice channel
# The format for these parametser is as follows: "./cc.sh <commandname> "-p -a -v""

hasParameters=false
isAutocomplete=false
requiresVoiceChannel=false

while getopts ":pav" opt; do
    case $opt in
        p)
            hasParameters=true
            ;;
        a)
            isAutocomplete=true
            ;;
        v)
            requiresVoiceChannel=true
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            ;;
    esac
done

if [ -f $commandFileName ]; then
    echo ERROR: A command with this name already exists
    exit 1
fi

touch $commandFileName

echo "// Path: $commandFileName" >> $commandFileName

echo "const { SlashCommandBuilder } = require('discord.js');" >> $commandFileName
echo "" >> $commandFileName
echo "module.exports = {" >> $commandFileName
echo "    data: new SlashCommandBuilder()" >> $commandFileName
echo "        .setName('$1')" >> $commandFileName
echo "        .setDescription('Command description')" >> $commandFileName
if [ ! -z $hasParameters ]; then
    echo "        .addStringOption(option =>" >> $commandFileName
    echo "            option.setName('query')" >> $commandFileName
    echo "                .setDescription('Parameter description')" >> $commandFileName
    echo "                .setRequired(true)," >> $commandFileName
    echo "          )" >> $commandFileName
fi
echo "    name: \"$1\"," >> $commandFileName
echo "    description: \"Command description\"," >> $commandFileName
echo "    usage: \"Command usage\"," >> $commandFileName
if [ ! -z $requiresVoiceChannel ]; then
    echo "    voice: true," >> $commandFileName
fi
if [ ! -z $isAutocomplete ]; then
    echo "    async autocomplete(interaction) {" >> $commandFileName
    echo "        " >> $commandFileName
    echo "    }," >> $commandFileName
fi
echo "    async execute(interaction) {" >> $commandFileName
echo "        " >> $commandFileName
echo "    }" >> $commandFileName
echo "};" >> $commandFileName