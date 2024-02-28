if status is-interactive
    # Commands to run in interactive sessions can go here

    set fish_greeting ''

    # for starship shell theme
    starship init fish | source
end


# pyenv init
if command -v pyenv 1>/dev/null 2>&1
  pyenv init - | source
end
