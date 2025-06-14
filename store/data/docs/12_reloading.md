ConfigurationReloading the configurationReloading the configuration file of the barIf you wish to reload the configuration file of the bar without resorting to
manually restarting the process you can use the following command:sketchybar --reload [Optional: ]which, has the same effect as restarting the process, but is a bit more
convenient. Additionally, an optional  argument to a new sketchybarrc
file can be given to load a different configuration. If the optional argument
is left out, the current configuration is reloaded.Hotloading the configuration of the barIf you wish that the bar automatically reloads the configuration file once you
edit it, you can use the hotload functionality included in SketchyBar. It will
monitor the directory of the current configuration for changes and reload the
configuration should it detect file changes. To control the hotload feature you
can use:sketchybar --hotload PreviousType NomenclatureNextTips & Tricks