import json
import os
import readchar
import sys
import time

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
                    'friendly': 'This is an example target',
                    'options': []
                },
                {
                    'command': 'mosh',
                    'host': 'user@example-machine.local',
                    'friendly': 'This is an example target using mosh',
                    'options': []
                }
            ]
        }
        resources.user.write('config.json', json.dumps(example_config, indent=4))
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
    puts(colored.cyan('Select a target (up (k), down (j), enter, ctrl+c to exit)'))

    # Save current cursor position so we can overwrite on list updates
    call(['tput', 'sc'])

    # Keep track of currently selected target
    selected_target = 0

    # Support input of long numbers
    number_buffer = []
    # Store time of last number that was entered
    number_last = round(time.time())

    while True:
        # Return to the saved cursor position
        call(['tput', 'rc'])

        # Print items
        for index, target in enumerate(targets):
            desc = '%2d ' % (index) + target['host'].ljust(longest_host) + ' | ' + target['friendly']
            if index == selected_target:
                puts(colored.green(' -> ' + desc))
            else:
                puts('    ' + desc)

        # Hang until we get a keypress
        key = readchar.readkey()

        if key == readchar.key.UP or key == 'k':
            # Ensure the new selection would be valid
            if (selected_target - 1) >= 0:
                selected_target -= 1

            # Empty the number buffer
            number_buffer = []

        elif key == readchar.key.DOWN or key == 'j':
            # Ensure the new selection would be valid
            if (selected_target + 1) <= (num_targets - 1):
                selected_target += 1

            # Empty the number buffer
            number_buffer = []

        elif key == 'g':
            # Go to top
            selected_target = 0

            # Empty the number buffer
            number_buffer = []

        elif key == 'G':
            # Go to bottom
            selected_target = num_targets - 1

            # Empty the number buffer
            number_buffer = []

        # Check if key is a number
        elif key in map(lambda x: str(x), range(10)):
            requested_target = int(key)

            # Check if there are any previously entered numbers, and append if less than one second has gone by
            if round(time.time()) - number_last <= 1:
                number_buffer += key
                requested_target = int(''.join(number_buffer))
                # If the new target is invalid, just keep the previously selected target instead
                if requested_target >= num_targets:
                    requested_target = selected_target
            else:
                number_buffer = [key]

            number_last = round(time.time())

            # Ensure the new selection would be valid
            if requested_target >= num_targets:
                requested_target = num_targets - 1

            selected_target = requested_target

        elif key == readchar.key.ENTER:
            # For cleanliness clear the screen
            call(['tput', 'clear'])

            target = targets[selected_target]

            # Check if there is a custom command for this target
            if 'command' in target.keys():
                command = target['command']
            else:
                command = 'ssh'

            # Arguments to the child process should start with the name of the command being run
            args = [command] + target.get('options', []) + [target['host']]
            try:
                # After this line, ssh will replace the python process
                os.execvp(command, args)
            except FileNotFoundError:
                sys.exit('command not found: {commandname}'.format(commandname=command))

        elif key == readchar.key.CTRL_C:
            exit(0)
