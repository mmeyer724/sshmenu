import json
import os
import readchar
from subprocess import call

from clint import resources
from clint.textui import puts, colored


def main():
    # First parameter is 'company' name, hence duplicate arguments
    resources.init('sshmenu', 'sshmenu')

    # For the first run, create an example config
    if resources.user.read('config.json') is None:
        example_config = {
            'targets': [
                {
                    'host': 'user@example-machine.local',
                    'friendly': 'This is an example target'
                }
            ]
        }
        resources.user.write('config.json', json.dumps(example_config))
        puts('I have created a new configuration file, please edit and run again:')
        puts(resources.user.path + '/config.json')
    else:
        config = json.loads(resources.user.read('config.json'))
        display_menu(config['targets'])


def display_menu(targets):
    # We need at least one target for our UI to make sense
    num_targets = len(targets)
    if num_targets <= 0:
        puts('Whoops, you don\'t have any targets listed in your config!')
        exit(0)

    # Determine the longest host length
    longest_host = -1
    for target in targets:
        length = len(target['host'])
        if length > longest_host:
            longest_host = length

    # Clear screen, give instructions
    call(['tput', 'clear'])
    puts(colored.cyan('Select a target (up, down, enter, ctrl+c to exit)'))

    # Save current cursor position so we can overwrite on list updates
    call(['tput', 'sc'])

    # Keep track of currently selected target
    selected_target = 0

    while True:
        # Return to the saved cursor position
        call(['tput', 'rc'])

        # Print items
        for index, target in enumerate(targets):
            desc = target['host'].ljust(longest_host) + ' | ' + target['friendly']
            if index == selected_target:
                puts(colored.green(' -> ' + desc))
            else:
                puts('    ' + desc)

        # Hang until we get a keypress
        key = readchar.readkey()

        if key == readchar.key.UP:
            # Ensure the new selection would be valid
            if (selected_target - 1) >= 0:
                selected_target -= 1
        elif key == readchar.key.DOWN:
            # Ensure the new selection would be valid
            if (selected_target + 1) <= (num_targets - 1):
                selected_target += 1
        elif key == readchar.key.ENTER:
            # For cleanliness clear the screen
            call(['tput', 'clear'])

            # After this line, ssh will replace the python process
            os.execlp('ssh', 'ssh', targets[selected_target]['host'])
        elif key == readchar.key.CTRL_C:
            exit(0)
