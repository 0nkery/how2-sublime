# how2-sublime
[How2-rs](https://github.com/0nkery/how2-rs) plugin for Sublime Text 3.

## Usage

You need the installed how2-rs.

This plugin comes with no pre-defined key bindings.

You can add them yourself:

``` json
  
  [
    { "keys": ["f1"], "command": "how2" },
    { "keys": ["shift+f1"], "command": "how2_show_answers" }
  ]

```

The `how2` command shows input panel where you can type your query.

The `how2_show_answers` command used by previous command internally.
If you just call it without any parameters (like in shown key bindings)
it will show previous answers in the quick panel.

You can run both commands with `Ctrl+Shift+P`. Just type `how2`.

## Settings

`how2_binary` - path to how2-rs executable.

`how2_max_answers` - maximum answers to fetch and show.
